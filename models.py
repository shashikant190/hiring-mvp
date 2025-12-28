from sqlalchemy import Column, Integer, String, Text, ForeignKey
from db import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    secret = Column(String, unique=True)  # private access key


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    name = Column(String)
    skills = Column(Text)
    availability = Column(String)
    proof = Column(String)
