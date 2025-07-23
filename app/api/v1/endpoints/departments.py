from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.department import Department
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.department import Department as DepartmentSchema, DepartmentCreate, DepartmentUpdate

router = APIRouter()


@router.get("/", response_model=List[DepartmentSchema])
def read_departments(
    db: Session = Depends(deps.get_db),
    hospital_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve departments.
    """
    query = db.query(Department)
    
    if hospital_id:
        query = query.filter(Department.hospital_id == hospital_id)
    
    # Filter by permissions
    if current_user.role == "hospital_admin":
        hospitals = db.query(Hospital).filter(Hospital.admin_id == current_user.id).all()
        hospital_ids = [h.id for h in hospitals]
        query = query.filter(Department.hospital_id.in_(hospital_ids))
    
    departments = query.offset(skip).limit(limit).all()
    return departments


@router.post("/", response_model=DepartmentSchema)
def create_department(
    *,
    db: Session = Depends(deps.get_db),
    department_in: DepartmentCreate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Create new department.
    """
    # Check if hospital exists and user has permission
    hospital = db.query(Hospital).filter(Hospital.id == department_in.hospital_id).first()
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    
    if current_user.role == "hospital_admin" and hospital.admin_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    department = Department(
        **department_in.dict(),
        created_by=str(current_user.id),
    )
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.get("/{department_id}", response_model=DepartmentSchema)
def read_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: int,
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get department by ID.
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check permissions for hospital admins
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == department.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return department


@router.put("/{department_id}", response_model=DepartmentSchema)
def update_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: int,
    department_in: DepartmentUpdate,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Update a department.
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == department.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = department_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(department, field, value)
    
    department.updated_by = str(current_user.id)
    db.add(department)
    db.commit()
    db.refresh(department)
    return department


@router.delete("/{department_id}")
def delete_department(
    *,
    db: Session = Depends(deps.get_db),
    department_id: int,
    current_user: User = Depends(deps.get_current_hospital_admin),
) -> Any:
    """
    Delete a department.
    """
    department = db.query(Department).filter(Department.id == department_id).first()
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    # Check permissions
    if current_user.role == "hospital_admin":
        hospital = db.query(Hospital).filter(Hospital.id == department.hospital_id).first()
        if hospital.admin_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(department)
    db.commit()
    return {"status": "success"}