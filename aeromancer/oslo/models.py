from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from aeromancer.db import models


class Module(models.Base):
    __tablename__ = 'oslo_module'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    line_id = Column(Integer, ForeignKey('line.id'))
    line = relationship(
        models.Line,
        uselist=False,
    )
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship(
        models.Project,
        backref='oslo_modules',
    )
