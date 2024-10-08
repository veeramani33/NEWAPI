from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from app.auth import schema as auth_schema
from app.auth import service as auth_service
from app.database import get_db
from app.purchase_order import schema as po_schema
from app.shared import schema as global_schema
from app.shared import service as global_service
from app.shared.pagination import Paginated

router = APIRouter(
    tags=["Global Dcode"],
)


@router.get(
    "/dcode/{code}",
    summary="Retrieve DCode Details",
    status_code=status.HTTP_200_OK,
    response_model=Paginated[global_schema.Output],
)
async def get_dcode_details(
    code: Annotated[
        po_schema.DcodeInput, Path(description="The code to get dcode data")
    ],
    db: Session = Depends(get_db),
    search: Annotated[Optional[str], Query()] = "",
    user: auth_schema.User = Depends(auth_service.get_current_user),
):
    try:
        query = global_service.get_code_and_name(
            table_name="dcode",
            type=code,
            co_code=user.co_code,
            search=search,
        )
        return paginate(db, query)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while retrieving dcode details",
        )
