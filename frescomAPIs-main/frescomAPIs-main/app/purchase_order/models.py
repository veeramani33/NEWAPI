from sqlalchemy import Column, Sequence, String, Table

from app.database import Base, engine


class PurchaseOrder(Base):
    __table__ = Table("po", Base.metadata, autoload_with=engine)

    po_sl_seq = Sequence("seq")


class PurchaseOrder2(Base):
    __table__ = Table("po2", Base.metadata, autoload_with=engine)

    po2_sl_seq = Sequence("seq")


class Suppliername(Base):
    __tablename__ = "supp_view"
    __table__ = Table(
        __tablename__,
        Base.metadata,
        Column("sl_no", String, primary_key=True),
        autoload_with=engine,
    )


class Shipment(Base):
    __tablename__ = "ship_to_view3"
    __table__ = Table(
        __tablename__,
        Base.metadata,
        Column("sl_no", String, primary_key=True),
        autoload_with=engine,
    )


class Inar(Base):
    __table__ = Table("inar", Base.metadata, autoload_with=engine)


class Currency(Base):
    __table__ = Table("cur", Base.metadata, autoload_with=engine)


class Imas(Base):
    __table__ = Table("imas", Base.metadata, autoload_with=engine)


class UnitOfMeasurement(Base):
    __table__ = Table("uom", Base.metadata, autoload_with=engine)


class ItemMakeView(Base):
    __tablename__ = "item_make_view"
    __table__ = Table(
        __tablename__,
        Base.metadata,
        Column("sl_no", String, primary_key=True),
        autoload_with=engine,
    )


class City(Base):
    __tablename__ = "city"
    __table__ = Table(
        __tablename__,
        Base.metadata,
        Column("sl_no", String, primary_key=True),
        extend_existing=True,
        autoload_with=engine,
    )
