from typing import TypeVar

from fastapi_pagination import Page
from fastapi_pagination.customization import (
    CustomizedPage,
    UseFieldsAliases,
    UseParamsFields,
)

T = TypeVar("T")

Paginated = CustomizedPage[
    Page[T],
    UseParamsFields(size=10),
    UseFieldsAliases(items="data"),
]
