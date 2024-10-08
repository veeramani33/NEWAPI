from sqlalchemy import Column, String, Table

from app.database import Base, engine


class Customer(Base):
    __table__ = Table("coname", Base.metadata, autoload_with=engine)


class DCode(Base):
    __table__ = Table("dcode", Base.metadata, autoload_with=engine)


def create_dynamic_table(table_name: str):
    class DynamicTable(Base):
        __tablename__ = table_name
        __table__ = Table(
            __tablename__,
            Base.metadata,
            Column("sl_no", String, primary_key=True),
            autoload_with=engine,
            extend_existing=True,
        )

    return DynamicTable
