from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.database import get_db
from app.purchase_order import schema as po_schema
from app.purchase_order import service as po_service
from app.shared import constants as global_constants
from app.shared import schema as global_schema
from app.shared import service as global_service
from app.shared.pagination import Paginated

router = APIRouter(
    prefix="/purchase",
    tags=["purchase order"],
    dependencies=[Depends(auth_service.get_current_user)],
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[po_schema.AllPoOutput],
)
async def get_po(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
):
    query = po_service.get_all_po(
        co_code=global_constants.global_co_code, search=search
    )

    try:
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving purchase order details",
        )


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_po(Values: po_schema.FormInput, db: Session = Depends(get_db)):
    # Begin a nested transaction to ensure that either all changes are committed or all are rolled back.
    db.begin_nested()
    try:
        await po_service.create_new_po(Values, db, global_constants.global_co_code)

    except Exception as e:
        print("Error:", e)
        print("rolling back")

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while creating the purchase order",
        )


# Endpoint to get all the values from the shipment.
@router.get(
    "/shipment",
    summary="Retrieve shipment Details",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[global_schema.Output],
)
async def get_shipment(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
) -> Paginated[global_schema.Output]:
    try:
        query = global_service.get_code_and_name(
            table_name="ship_to_view3",
            search=search,
            co_code=global_constants.global_co_code,
        )
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving shipment details",
        )


@router.get(
    "/supplier",
    summary="Retrieve supplier Details",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[global_schema.Output],
)
async def get_supplier_name(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
) -> Paginated[global_schema.Output]:
    try:
        query = global_service.get_code_and_name(table_name="supp_view", search=search)
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving supplier details",
        )


@router.get(
    "/inar",
    summary="Retrieve INAR Details",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[global_schema.Output],
)
async def get_inar_details(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
) -> Paginated[global_schema.Output]:
    try:
        query = global_service.get_code_and_name(table_name="inar", search=search)

        return paginate(db, query)

    except Exception:
        # error message set to the default error message.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving INAR details",
        )


@router.get(
    "/currency",
    summary="Retrieve Currency Details",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[global_schema.Output],
)
async def get_currency_details(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
) -> Paginated[global_schema.Output]:
    try:
        query = global_service.get_code_and_name(table_name="cur", search=search)
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving currency details",
        )


@router.get(
    "/document/{po_type_sl_no}",
    summary="Retrieve doc number and doc prefix",
    response_description="A response containing the document number and it's prefix",
    status_code=status.HTTP_200_OK,
    response_model=po_schema.DocInfoOutput,
)
async def get_document_details(
    po_type_sl_no: Annotated[
        str,
        Path(description="The 'sl_no' field returned from 'GET /dcode/240' query"),
    ],
    db: Session = Depends(get_db),
):
    try:
        doc_no, pref = await po_service.get_doc_number_and_pref(
            sl_no=po_type_sl_no, co_code=global_constants.global_co_code, db=db
        )

        print(doc_no, pref)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    if not doc_no or not pref:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document number or prefix not found",
        )

    return po_schema.DocInfoOutput(doc_no=str(doc_no), pref=pref)


@router.get("/items", response_model=Paginated[po_schema.PO2ItemsOutput])
def get_po2_details(
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
):
    try:
        query = po_service.get_po2_items_list(
            co_code=global_constants.global_co_code, search=search
        )
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while executing the query",
        )


@router.get("/items/spec/{item_sl}", response_model=Paginated[po_schema.SpecOutput])
def get_item_specs(
    item_sl: Annotated[
        str,
        Path(
            description="The item 'sl_no' field returned from '/purchase/items' query"
        ),
    ],
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
) -> Paginated[po_schema.SpecOutput]:
    try:
        query = po_service.get_po2_items_specs(item_sl=item_sl, search=search)
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error while executing the query",
        )


@router.get(
    "/{po_sl_no}",
    summary="Retrieves details to be inserted in PDF(bill)",
    status_code=status.HTTP_200_OK,
    response_model=po_schema.PoPrint,
)
async def get_po_details(
    po_sl_no: Annotated[
        str,
        Path(
            description="The purchase order 'sl_no' field returned from 'GET /purchase/' query"
        ),
    ],
    db: Session = Depends(get_db),
):
    poResult = await po_service.get_po1_print_values(po_sl_no=po_sl_no, db=db)
    po2result = await po_service.get_po2_print_values(po_sl_no=po_sl_no, db=db)

    if not poResult and not po2result:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    return {"po1": poResult, "po2": po2result}
