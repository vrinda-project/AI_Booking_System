from typing import Any, List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.hospital import Hospital
from app.models.department import Department
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.hospital import Hospital as HospitalSchema, HospitalCreate, HospitalUpdate, HospitalDetail

router = APIRouter()


@router.get("/", response_model=List[Union[HospitalSchema, HospitalDetail]])
def read_hospitals(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    include: Optional[str] = Query(None, description="Comma-separated list of related entities to include (departments,doctors)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve hospitals.
    """
    # Parse include parameter
    include_params = include.split(",") if include else []
    include_departments = "departments" in include_params
    include_doctors = "doctors" in include_params
    
    # Base query
    query = db.query(Hospital)
    
    # Add eager loading if needed
    if include_departments:
        query = query.options(joinedload(Hospital.departments))
    if include_doctors:
        query = query.options(joinedload(Hospital.doctors))
    
    # Apply permission filters
    if current_user.role == "super_admin":
        hospitals = query.offset(skip).limit(limit).all()
    elif current_user.role == "hospital_admin":
        hospitals = query.filter(Hospital.admin_id == current_user.id).offset(skip).limit(limit).all()
    else:
        hospitals = query.filter(Hospital.status == "active").offset(skip).limit(limit).all()
    
    # Process hospitals based on includes
    result = []
    for hospital in hospitals:
        # Filter active departments and doctors if included
        if include_departments and hasattr(hospital, "departments"):
            active_departments = [dept for dept in hospital.departments if dept.is_active]
            # We need to set this for the Pydantic model to pick it up
            hospital.departments = active_departments
            
        if include_doctors and hasattr(hospital, "doctors"):
            active_doctors = [doc for doc in hospital.doctors if doc.is_active]
            hospital.doctors = active_doctors
        
        # Convert to appropriate Pydantic model
        if include_departments or include_doctors:
            result.append(HospitalDetail.from_orm(hospital))
        else:
            result.append(HospitalSchema.from_orm(hospital))
    
    return result


@router.get("/{hospital_id}", response_model=Union[HospitalSchema, HospitalDetail])
def read_hospital(
    *,
    db: Session = Depends(deps.get_db),
    hospital_id: int,
    include: Optional[str] = Query(None, description="Comma-separated list of related entities to include (departments,doctors)"),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get hospital by ID.
    """
    # Parse include parameter
    include_params = include.split(",") if include else []
    include_departments = "departments" in include_params
    include_doctors = "doctors" in include_params
    
    # Base query
    query = db.query(Hospital)
    
    # Add eager loading if needed
    if include_departments:
        query = query.options(joinedload(Hospital.departments))
    if include_doctors:
        query = query.options(joinedload(Hospital.doctors))
    
    hospital = query.filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Check permissions
    if current_user.role not in ["super_admin", "hospital_admin"]:
        if hospital.status != "active":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "hospital_admin" and hospital.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Filter active departments and doctors if included
    if include_departments and hasattr(hospital, "departments"):
        hospital.departments = [dept for dept in hospital.departments if dept.is_active]
    if include_doctors and hasattr(hospital, "doctors"):
        hospital.doctors = [doc for doc in hospital.doctors if doc.is_active]
    
    # Convert to appropriate Pydantic model
    if include_departments or include_doctors:
        return HospitalDetail.from_orm(hospital)
    else:
        return HospitalSchema.from_orm(hospital)


@router.get("/{hospital_id}/full", response_model=HospitalDetail)
def read_hospital_full(
    *,
    db: Session = Depends(deps.get_db),
    hospital_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get hospital by ID with all related data (departments and doctors).
    """
    # Query with eager loading
    query = db.query(Hospital)
    query = query.options(
        joinedload(Hospital.departments),
        joinedload(Hospital.doctors)
    )
    
    hospital = query.filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Check permissions
    if current_user.role not in ["super_admin", "hospital_admin"]:
        if hospital.status != "active":
            raise HTTPException(status_code=403, detail="Not enough permissions")
    elif current_user.role == "hospital_admin" and hospital.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Filter active departments and doctors
    hospital.departments = [dept for dept in hospital.departments if dept.is_active]
    hospital.doctors = [doc for doc in hospital.doctors if doc.is_active]
    
    # Convert to Pydantic model
    return HospitalDetail.from_orm(hospital)


@router.post("/", response_model=HospitalSchema)
def create_hospital(
    *,
    db: Session = Depends(deps.get_db),
    hospital_in: HospitalCreate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Create new hospital.
    """
    try:
        # Validate admin_id if provided
        if hospital_in.admin_id:
            admin = db.query(User).filter(User.id == hospital_in.admin_id).first()
            if not admin:
                raise HTTPException(
                    status_code=400,
                    detail=f"User with ID {hospital_in.admin_id} not found. Cannot assign as hospital admin."
                )
            if admin.role != "hospital_admin":
                raise HTTPException(
                    status_code=400,
                    detail=f"User with ID {hospital_in.admin_id} is not a hospital admin."
                )
        
        # Create hospital
        hospital_data = hospital_in.dict()
        hospital = Hospital(
            **hospital_data,
            created_by=str(current_user.id),
        )
        db.add(hospital)
        db.commit()
        db.refresh(hospital)
        
        # Convert to Pydantic model
        return HospitalSchema.from_orm(hospital)
    except Exception as e:
        db.rollback()
        from app.core.logging import logger
        logger.error(f"Error creating hospital: {str(e)}")
        raise


@router.put("/{hospital_id}", response_model=HospitalSchema)
def update_hospital(
    *,
    db: Session = Depends(deps.get_db),
    hospital_id: int,
    hospital_in: HospitalUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update a hospital.
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    # Check permissions
    if current_user.role == "hospital_admin" and hospital.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = hospital_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(hospital, field, value)
    
    hospital.updated_by = str(current_user.id)
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    
    # Convert to Pydantic model
    return HospitalSchema.from_orm(hospital)


@router.delete("/{hospital_id}")
def delete_hospital(
    *,
    db: Session = Depends(deps.get_db),
    hospital_id: int,
    current_user: User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a hospital.
    """
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    db.delete(hospital)
    db.commit()
    return {"status": "success"}