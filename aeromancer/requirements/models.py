from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from aeromancer.db import models


class Requirement(models.Base):
    __tablename__ = 'requirement'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey('line.id'))
    line = relationship(
        models.Line,
        uselist=False,
        single_parent=True,
    )
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(
        models.Project,
        backref='requirements',
    )


class GlobalRequirement(models.Base):
    __tablename__ = 'global_requirement'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey('line.id'))
    line = relationship(
        models.Line,
        uselist=False,
        single_parent=True,
    )
