from ..database import Base
from .patient import Patient
from .doctor import Doctor, Department
from .appointment import Appointment, TimeSlot
from .conversation import Conversation, Review
from .hospital import Hospital
from .hospital_department import hospital_department