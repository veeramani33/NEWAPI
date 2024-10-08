from typing import Optional

from sqlalchemy import or_, select

from app.purchase_order.schema import DcodeInput
from app.shared import models


def get_code_and_name(
    table_name: str,
    type: Optional[DcodeInput] = None,
    co_code: Optional[str] = None,
    search: Optional[str] = "",
):
    """
    Retrieves a query object based on the provided table name and optional filters.

    Args:
        table_name (str): The name of the table to query. This is used to dynamically
            select the correct table using SQLAlchemy's `Table` object.
        type (Optional[DcodeInput]): An optional filter by the 'type' column in the table.
            This is an enumeration of different types of codes in the table.
        co_code (Optional[str]): An optional filter by the 'co_code' column in the table.
            This is a company code that is used to further filter the results.
        search (Optional[str]): An optional search query that will be used to filter the
            results. The query will be used to search both the 'code' and 'name' columns in
            the table.

    Returns:
        A SQLAlchemy query object that filters the table based on the provided parameters.
    """
    # Dynamically select the correct table based on the provided table name
    TableClass = models.create_dynamic_table(table_name)

    # Build the query object
    query = select(TableClass).filter(
        or_(TableClass.code.ilike(f"{search}%"), TableClass.name.ilike(f"{search}%")),
    )

    # Filter the query by company code if one was provided
    if co_code:
        query = query.where(TableClass.co_code == co_code)

    # Filter the query by the type if one was provided
    if type:
        query = query.where(TableClass.type == type)

    # Return the query object
    return query
