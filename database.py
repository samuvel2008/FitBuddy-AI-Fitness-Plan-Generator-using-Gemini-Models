from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

from .config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(80), nullable=False)
    intensity = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    plans = relationship("Plan", back_populates="user", cascade="all, delete-orphan")

class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    last_feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="plans")

def init_db() -> None:
    Base.metadata.create_all(bind=engine)

def save_user(data: dict) -> User:
    with SessionLocal() as db:
        user = db.query(User).filter(User.user_id == data["user_id"]).first()
        if user:
            user.name = data["name"]
            user.age = data["age"]
            user.weight = data["weight"]
            user.goal = data["goal"]
            user.intensity = data["intensity"]
        else:
            user = User(**data)
            db.add(user)
        db.commit()
        db.refresh(user)
        return user

def save_plan(user_pk: int, original_plan: str, nutrition_tip: str) -> Plan:
    with SessionLocal() as db:
        plan = Plan(
            user_id=user_pk,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

def get_user(user_id: str) -> User | None:
    with SessionLocal() as db:
        return db.query(User).filter(User.user_id == user_id).first()

def get_latest_plan(user_id: str) -> Plan | None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return None
        return (
            db.query(Plan)
            .filter(Plan.user_id == user.id)
            .order_by(Plan.id.desc())
            .first()
        )

def update_plan(plan_id: int, updated_plan: str, feedback: str) -> Plan | None:
    with SessionLocal() as db:
        plan = db.query(Plan).filter(Plan.id == plan_id).first()
        if not plan:
            return None
        plan.updated_plan = updated_plan
        plan.last_feedback = feedback
        db.commit()
        db.refresh(plan)
        return plan

def get_all_users_with_plans() -> list[tuple[User, list[Plan]]]:
    with SessionLocal() as db:
        users = db.query(User).order_by(User.id.desc()).all()
        return [(u, list(u.plans)) for u in users]

def delete_user(user_id: str) -> bool:
    with SessionLocal() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
