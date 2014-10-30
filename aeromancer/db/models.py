from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

Base = declarative_base()


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    path = Column(String)
    files = relationship('File',
                         backref='project',
                         cascade="all, delete, delete-orphan")


class File(Base):
    __tablename__ = 'file'
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    name = Column(String, nullable=False)
    path = Column(String)
    lines = relationship('Line',
                         backref='file',
                         cascade="all, delete, delete-orphan")


class Line(Base):
    __tablename__ = 'line'
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('file.id'))
    number = Column(Integer, nullable=False)
    content = Column(String)
