from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.dialects.postgresql import ARRAY

Base = declarative_base()

class OrganizationActivity(Base):
    __tablename__ = "organization_activity"
    organization_id = Column(Integer, ForeignKey("organizations.id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)

class Building(Base):
    __tablename__ = 'buildings'
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    latitude = Column(Float)
    longitude = Column(Float)
    organizations = relationship('Organization', back_populates='building')

class Activity(Base):
    __tablename__ = 'activities'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey('activities.id'), nullable=True)
    children = relationship('Activity', backref='parent', remote_side=[id])
    organizations = relationship('Organization', secondary="organization_activity", back_populates='activities')

class Organization(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    phones = Column(ARRAY(String))
    building_id = Column(Integer, ForeignKey('buildings.id'))
    building = relationship('Building', back_populates='organizations')
    activities = relationship('Activity', secondary="organization_activity", back_populates='organizations')
