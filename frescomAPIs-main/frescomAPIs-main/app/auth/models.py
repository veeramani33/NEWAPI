from sqlalchemy import Column, Integer, String

from app.database import Base


class Users(Base):
    __tablename__ = "sass"  # Use the actual table name in the database
    __table_args__ = {"extend_existing": True}

    login = Column(String, primary_key=True)
    co_code = Column(String)
    password = Column(Integer)
    grade = Column(Integer)

    # Only include the columns you want to load
    __mapper_args__ = {"include_properties": ["login", "co_code", "password", "grade"]}

class UserCoView(Base):
    __tablename__ = 'sass3_co_view'  # This refers to the view in the database
    __table_args__ = {"extend_existing": True}

    login = Column(String, primary_key=True)