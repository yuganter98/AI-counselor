from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, ARRAY, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

# ENUMS
class UserStageEnum(str, enum.Enum):
    PROFILE = "PROFILE"
    DISCOVERY = "DISCOVERY"
    FINALIZE = "FINALIZE"
    APPLICATION = "APPLICATION"

class RankTier(str, enum.Enum):
    LOW = "LOW"
    MID = "MID"
    HIGH = "HIGH"

class CompetitionLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ShortlistCategory(str, enum.Enum):
    DREAM = "DREAM"
    TARGET = "TARGET"
    SAFE = "SAFE"

class TaskStatus(str, enum.Enum):
    PENDING = "PENDING"
    DONE = "DONE"

# MODELS

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    stage = relationship("UserStage", back_populates="user", uselist=False)
    shortlists = relationship("Shortlist", back_populates="user")
    tasks = relationship("Task", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    education_level = Column(String, nullable=True)
    major = Column(String, nullable=True)
    graduation_year = Column(Integer, nullable=True)
    gpa = Column(Float, nullable=True)
    
    target_degree = Column(String, nullable=True)
    field_of_study = Column(String, nullable=True)
    intake_year = Column(Integer, nullable=True)
    
    preferred_countries = Column(ARRAY(String), nullable=True)
    
    budget_min = Column(Integer, nullable=True)
    budget_max = Column(Integer, nullable=True)
    funding_type = Column(String, nullable=True)
    
    ielts_status = Column(String, nullable=True)
    gre_status = Column(String, nullable=True)
    sop_status = Column(String, nullable=True)
    
    profile_completed = Column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="profile")

class UserStage(Base):
    __tablename__ = "user_stages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    current_stage = Column(Enum(UserStageEnum), default=UserStageEnum.PROFILE, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="stage")

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    annual_cost = Column(Integer, nullable=True)
    ranking_tier = Column(Enum(RankTier), nullable=True)
    competition_level = Column(Enum(CompetitionLevel), nullable=True)

class Shortlist(Base):
    __tablename__ = "shortlists"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=False)
    category = Column(Enum(ShortlistCategory), nullable=False)
    locked = Column(Boolean, default=False)

    user = relationship("User", back_populates="shortlists")
    university = relationship("University")

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    generated_by_ai = Column(Boolean, default=False)
    university_id = Column(Integer, ForeignKey("universities.id"), nullable=True)

    user = relationship("User", back_populates="tasks")
    university = relationship("University")
