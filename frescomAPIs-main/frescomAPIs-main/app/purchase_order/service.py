from typing import Dict, Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, aliased

from app.purchase_order import models, schema
from app.shared import models as global_models


def get_all_po(co_code: str, search: Optional[str] = ""):
    """
    Get all purchase orders from the database with the given company code and search query.

    Args:
        co_code: The company code to filter by.
        search: The search query. If None, all records will be retrieved.

    Returns:
        A SQLAlchemy query object.
    """

    # Build the query to retrieve purchase orders
    query = (
        # Select the columns to be retrieved
        select(
            models.PurchaseOrder.sl_no,
            models.PurchaseOrder.doc_no,
            models.PurchaseOrder.doc_date,
            models.Suppliername.name.label("sup_name"),
            models.Suppliername.code.label("sup_code"),
        )
        # Join the supplier table
        .outerjoin(
            models.Suppliername,
            models.PurchaseOrder.party_sl == models.Suppliername.sl_no,
        )
        # Filter by company code
        .where(models.PurchaseOrder.co_code == co_code)
        # Filter by search query
        .filter(
            or_(
                models.PurchaseOrder.doc_no.ilike(f"{search}%"),
                models.Suppliername.name.ilike(f"{search}%"),
                models.Suppliername.code.ilike(f"{search}%"),
            )
        )
        # Sort by document date
        .order_by(models.PurchaseOrder.doc_date)
    )

    return query


async def create_new_po(
    Values: schema.FormInput, db: Session, co_code: str
) -> models.PurchaseOrder:
    """
    Create a new purchase order in the database.

    Args:
        Values: The data for the new purchase order.
        db: The active database session.
        co_code: The company code to associate with the purchase order.

    Returns:
        The newly created purchase order.
    """

    # Get the current maximum document number
    doc_no = (
        db.query(func.coalesce(func.max(models.PurchaseOrder.doc_no), 0))
        .where(models.PurchaseOrder.co_code == co_code)
        .scalar()
    )

    # Create the new document number
    po_no = f"{Values.po.doc_pref}/{doc_no}"

    # Get a new sequence number for the purchase order
    po_sl_no = db.query(models.PurchaseOrder.po_sl_seq.next_value()).scalar()

    # Create the purchase order
    new_po = models.PurchaseOrder(
        po_no=po_no,
        doc_no=doc_no + 1,
        sl_no=models.PurchaseOrder.po_sl_seq.next_value(),
        co_code=co_code,
        login="aiwoox",
        **Values.po.model_dump(exclude="doc_pref"),
    )

    # Add the purchase order to the database
    db.add(new_po)

    # Print a message to indicate success
    print("po added")

    # Iterate over the items in the purchase order
    for row in Values.po2:
        # Get a new sequence number for the item
        po2_sl_no = db.query(models.PurchaseOrder2.po2_sl_seq.next_value()).scalar()
        print("po2_sl_no:", po2_sl_no)

        # Create the item
        new_po2 = models.PurchaseOrder2(
            po_sl=po_sl_no,
            sl_no=po2_sl_no,
            co_code=co_code,
            login="aiwoox",
            **row.model_dump(),
        )

        # Add the item to the database
        db.add(new_po2)

    # Print a message to indicate success
    print("items added")

    # Save the changes to the database
    db.commit()

    # Refresh the database records
    db.refresh(new_po)
    db.refresh(new_po2)

    # Return the newly created purchase order
    return new_po


async def get_doc_number_and_pref(
    sl_no: str, co_code: str, db: Session
) -> Dict[str, str]:
    """
    Retrieve the document number and document prefix for a given document code and company code.

    Args:
        sl_no: The document sl_no
        co_code: The company code
        db: The active database session

    Returns:
        A dictionary with two keys:
            - "doc_no": The document number (starts from 1)
            - "doc_pref": The document prefix
    """

    # Query the document number
    doc_no_query = select(
        func.coalesce(func.max(models.PurchaseOrder.doc_no), 0)
    ).where(models.PurchaseOrder.co_code == co_code)

    # Query the document prefix
    pref_query = select(global_models.DCode.pref).where(
        global_models.DCode.sl_no == sl_no.lower()
    )

    # Execute the queries
    doc_no = db.execute(doc_no_query).scalar_one_or_none()
    pref = db.execute(pref_query).scalar_one_or_none()

    # Return the results
    return (doc_no, pref)


def get_po2_items_list(co_code: str, search: Optional[str] = None):
    """
    Retrieve a list of items from the 'imas' table, filtered by the given company code and search query.

    The query will return a list of items with their unit of measurement, group code, and sub-group code.

    Args:
        co_code: The company code to filter by.
        search: The search query to filter the results.

    Returns:
        A SQLAlchemy query object that can be executed to retrieve the items.
    """

    # Create aliases for the group and sub-group tables
    gr = aliased(global_models.DCode)
    sub_gr = aliased(global_models.DCode)

    # Build the query
    query = (
        # Select the columns to be retrieved
        select(
            models.Imas.sl_no,
            models.Imas.unit_sl,
            models.Imas.code,
            models.Imas.name,
            models.Imas.gst_pc.label("gst"),
            gr.code.label("gr_code"),
            models.UnitOfMeasurement.code.label("uom_code"),
            sub_gr.code.label("sub_gr_code"),
        )
        # Join the group table
        .outerjoin(gr, models.Imas.gr_sl == gr.sl_no)
        # Join the sub-group table
        .outerjoin(sub_gr, models.Imas.sub_gr_sl == sub_gr.sl_no)
        # Join the unit of measurement table
        .outerjoin(
            models.UnitOfMeasurement,
            models.Imas.unit_sl == models.UnitOfMeasurement.sl_no,
        )
        # Filter by company code
        .filter(models.Imas.co_code == co_code)
        # Filter by search query
        .filter(
            or_(
                models.Imas.code.ilike(f"{search}%"),
                models.Imas.name.ilike(f"{search}%"),
            )
        )
        # Sort the results by item code
        .order_by(models.Imas.code)
    )

    # Return the query object
    return query


def get_po2_items_specs(item_sl: str, search: Optional[str]):
    query = (
        select(
            models.ItemMakeView.sl_no,
            models.ItemMakeView.man_code,
            models.ItemMakeView.man_name,
        )
        .filter(models.ItemMakeView.item_sl == item_sl)
        .filter(
            or_(
                models.ItemMakeView.man_code.ilike(f"{search}%"),
                models.ItemMakeView.man_name.ilike(f"{search}%"),
            )
        )
    )

    return query


async def get_po1_print_values(
    po_sl_no: str, db: Session
) -> schema.PurchaseOrderOnePrint:
    """
    Retrieve the details of a purchase order from the database.

    Args:
        doc_no: The document number of the purchase order.
        db: The active database session.

    Returns:
        A `PurchaseOrderOnePrint` object containing the details of the purchase order.
    """
    # Create aliases for the DCode tables used in the query
    PayTermsDCode = aliased(global_models.DCode)
    DespModeDCode = aliased(global_models.DCode)
    FreightDCode = aliased(global_models.DCode)
    PackTypeDCode = aliased(global_models.DCode)
    PLCodeDCode = aliased(global_models.DCode)
    PDCodeDCode = aliased(global_models.DCode)
    TransporterDCode = aliased(global_models.DCode)
    IncoTermsDCode = aliased(global_models.DCode)
    InsuranceDCode = aliased(global_models.DCode)

    # Build the query to retrieve the purchase order details
    poResult = (
        db.query(
            # Retrieve the columns from the PurchaseOrder table
            models.PurchaseOrder.po_no,
            models.PurchaseOrder.doc_date,
            models.Suppliername.code.label("supp_code"),
            models.Suppliername.name.label("supp_name"),
            models.Suppliername.add1.label("supp_add1"),
            models.Suppliername.add2.label("supp_add2"),
            models.Suppliername.phone.label("supp_phone"),
            models.Suppliername.fax.label("supp_fax"),
            models.Suppliername.city_name.label("supp_city_name"),
            models.Suppliername.pin.label("supp_pin"),
            models.Shipment.name.label("ship_to_name"),
            models.Shipment.add1.label("ship_to_add1"),
            models.Shipment.add2.label("ship_to_add2"),
            models.City.name.label("ship_to_city_name"),
            models.Shipment.pin.label("ship_to_pin"),
            PayTermsDCode.name.label("pay_terms_name"),
            DespModeDCode.name.label("desp_mode_name"),
            FreightDCode.name.label("freight_name"),
            PackTypeDCode.name.label("pack_type_name"),
            PLCodeDCode.code.label("pl_code"),
            PLCodeDCode.name.label("pl_name"),
            PDCodeDCode.code.label("pd_code"),
            PDCodeDCode.name.label("pd_name"),
            TransporterDCode.name.label("transporter_name"),
            models.Inar.code.label("spl_ins_code"),
            models.Inar.name.label("spl_ins_name"),
            models.PurchaseOrder.nar1.label("spl_remarks"),
            IncoTermsDCode.name.label("inco_terms"),
            InsuranceDCode.name.label("insurance"),
            models.PurchaseOrder.tc_yn.label("test_cert"),
            models.Currency.name.label("currency_name"),
        )
        # Join the Suppliername table
        .outerjoin(
            models.Suppliername,
            models.PurchaseOrder.party_sl == models.Suppliername.sl_no,
        )
        # Join the Shipment table
        .outerjoin(
            models.Shipment, models.PurchaseOrder.shipto_sl == models.Shipment.sl_no
        )
        # Join the City table
        .outerjoin(models.City, models.Shipment.city_sl == models.City.sl_no)
        # Join the DCode tables
        .outerjoin(PayTermsDCode, models.PurchaseOrder.pt_sl == PayTermsDCode.sl_no)
        .outerjoin(
            DespModeDCode, models.PurchaseOrder.desp_mode_sl == DespModeDCode.sl_no
        )
        .outerjoin(FreightDCode, models.PurchaseOrder.frt_sl == FreightDCode.sl_no)
        .outerjoin(
            TransporterDCode,
            models.PurchaseOrder.transporter_sl == TransporterDCode.sl_no,
        )
        .outerjoin(
            PackTypeDCode, models.PurchaseOrder.pack_type_sl == PackTypeDCode.sl_no
        )
        .outerjoin(PLCodeDCode, models.PurchaseOrder.pl_sl == PLCodeDCode.sl_no)
        .outerjoin(PDCodeDCode, models.PurchaseOrder.pd_sl == PDCodeDCode.sl_no)
        .outerjoin(models.Inar, models.PurchaseOrder.inar_sl == models.Inar.sl_no)
        .outerjoin(
            IncoTermsDCode, models.PurchaseOrder.pricetype_sl == IncoTermsDCode.sl_no
        )
        .outerjoin(InsuranceDCode, models.PurchaseOrder.ins_sl == InsuranceDCode.sl_no)
        .outerjoin(
            models.Currency, models.PurchaseOrder.cur_sl == models.Currency.sl_no
        )
        # Filter by the given document number
        .filter(models.PurchaseOrder.sl_no == po_sl_no)
        # Retrieve the first result
        .first()
    )

    return poResult


async def get_po2_print_values(po_sl_no: str, db: Session):
    """
    Retrieve the values from the po2 table for a given document number.

    Args:
        doc_no (str): The document number to query.
        db (Session): The active database session.

    Returns:
        A list of dictionaries containing the values from the po2 table.
    """
    # # Get the sl_no from the po table
    # poSl = (
    #     db.query(models.PurchaseOrder.sl_no)
    #     .where(models.PurchaseOrder.sl_no == po_sl_no)
    #     .scalar()
    # )

    # Query the po2 table and join it with the unit_of_measurement and imas tables
    # and filter the result by the sl_no from the po table
    po2result = (
        db.query(
            models.PurchaseOrder2.item_code,
            models.PurchaseOrder2.name.label("description"),
            models.PurchaseOrder2.qty,
            models.UnitOfMeasurement.code.label("uom"),
            models.PurchaseOrder2.rate.label("unit_price"),
            models.PurchaseOrder2.gst_pc,
            models.PurchaseOrder2.sch_date,
        )
        .join(
            models.UnitOfMeasurement,
            models.PurchaseOrder2.unit_sl == models.UnitOfMeasurement.sl_no,
        )
        .join(models.Imas, models.PurchaseOrder2.item_sl == models.Imas.sl_no)
        .where(models.PurchaseOrder2.po_sl == po_sl_no)
    )

    return po2result
