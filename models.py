from sqlalchemy import (
    Column,
    String,
    Integer,
    Date,
    Numeric,
    Float,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ENUM

from base import Base


statuses = ENUM(
    "active",
    "inactive",
    "deleted",
    name="statuses",
    metadata=Base.metadata,
    create_type=True,
    nullable=False,
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)

    user_name = Column(
        String,
        index=True,
    )
    tg_id = Column(Integer, index=True, unique=True)
    counter = Column(Integer, default=0)
    status = Column(statuses)

    email = Column(String)
    mobile_phone = Column(String)
    selected_services = Column(
        JSONB,
        default=list(["personal", "remote_work"]),
        server_default='["personal","remote_work"]',
        nullable=False,
    )
