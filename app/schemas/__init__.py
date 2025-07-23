from app.schemas.user import User, UserCreate, UserUpdate, UserInDB
from app.schemas.hospital import Hospital, HospitalCreate, HospitalUpdate, HospitalDetail
from app.schemas.department_summary import DepartmentSummary
from app.schemas.doctor_summary import DoctorSummary
from app.schemas.department import Department, DepartmentCreate, DepartmentUpdate
from app.schemas.doctor import Doctor, DoctorCreate, DoctorUpdate
from app.schemas.patient import Patient, PatientCreate, PatientUpdate
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate
from app.schemas.token import Token, TokenPayload