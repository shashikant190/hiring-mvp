from sqlalchemy import Column, Integer, String, Text, ForeignKey
from db import Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(Text)
    secret = Column(String, unique=True)


class Applicant(Base):
    __tablename__ = "applicants"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))

    name = Column(String)
    email = Column(String)
    country = Column(String)
    github = Column(String)

    skills = Column(Text)
    availability = Column(String)
    proof = Column(String)


class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    count = Column(Integer, default=0)
