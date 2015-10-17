# ORM for catalog db and application
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker, backref
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user_account'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    
    @property
    def serialize(self):
        # Return in serializable format - if wanted
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
            }

            
class Category(Base):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    creator_id = Column(Integer, ForeignKey('user_account.id'))
    
    creator = relationship("User")
    items = relationship("Item", cascade="all, delete-orphan")
    
    @property
    def serialize(self):
        # Return in serializable format
        return {
            'id': self.id,
            'name': self.name
        }
    
    
class Item(Base):
    __tablename__ = 'item'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image = Column(LargeBinary, nullable=True)
    category_id = Column(Integer, ForeignKey('category.id'))
    creator_id = Column(Integer, ForeignKey('user_account.id'))
    
    category = relationship("Category")
    creator = relationship("User")    
    
    @property
    def serialize(self):
        # Return in serializable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


engine = create_engine('postgresql:///catalog')

Base.metadata.create_all(engine)