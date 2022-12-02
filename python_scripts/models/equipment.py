from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from app import db

class Equipment(db.Model):
    __tablename__ = 'equipment'
    __table_args__ = (
        UniqueConstraint('external_id', 'type', 'organization_id'),
    )

    id = Column(Integer, primary_key=True)
    organization_id = Column(ForeignKey('organizations.id'), nullable=False)
    created_by = Column(ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    data = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    external_id = Column(String)
    stats = Column(JSONB)
    sub_type = Column(String)
    room = Column(String)
    default_unit_type = Column(String)
    attributes = Column(JSONB)
