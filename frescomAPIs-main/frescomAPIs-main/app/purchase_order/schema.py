from datetime import date
from enum import IntEnum
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.shared import schema as global_schema


class PO(BaseModel):
    type_sl: str = Field(max_length=30)
    doc_date: Optional[date] = date.today()
    quo_date: Optional[date] = date.today()
    quo_no: Optional[str] = Field(max_length=50, default=None)
    doc_pref: str = Field(max_length=50)
    party_sl: str = Field(max_length=50)
    shipto_sl: str = Field(max_length=30)
    pt_sl: Optional[str] = Field(max_length=30, default="")
    frt_sl: Optional[str] = Field(max_length=30, default="")
    pricetype_sl: Optional[str] = Field(max_length=30, default="")
    ins_sl: Optional[str] = Field(max_length=30, default="")
    desp_mode_sl: Optional[str] = Field(max_length=30, default="")
    transporter_sl: Optional[str] = Field(max_length=30, default="")
    pack_type_sl: Optional[str] = Field(max_length=50, default="")
    pl_sl: Optional[str] = Field(max_length=40, default="")
    pd_sl: Optional[str] = Field(max_length=40, default="")
    warr_sl: Optional[str] = Field(max_length=30, default="")
    inar_sl: Optional[str] = Field(max_length=30, default="")
    nar1: Optional[str] = Field(max_length=2000, default="")
    cur_sl: Optional[str] = Field(max_length=30, default="")
    exc_rate: Optional[float] = Field(ge=1.00, le=999999999.00, default=1.00)
    open_po: Optional[Literal[0, 1]] = 0
    tc_yn: Optional[Literal["Y", "N"]] = "N"
    pr_type: Optional[int] = 16
    # TODO: Check on the following values. They are set to some defaults in database.
    closed: Optional[int] = 0
    entry_date: Optional[date] = date.today()


class PO2(BaseModel):
    doc_date: date
    item_sl: str = Field(max_length=50)
    unit_sl: str = Field(max_length=30)
    item_code: Optional[str] = Field(max_length=50, default="")
    qty: int = Field(ge=1, le=99999999)
    make_sl: str = Field(max_length=75)
    rate: float = Field(gt=0.00, le=9999999999.00)
    per_unit: Optional[int] = Field(le=9999999, default=1)
    disc_pc: Optional[float] = Field(ge=0.000, le=999.999, default=0.000)
    gst_pc: Optional[float] = Field(ge=0.000, le=999.999, default=0.000)
    sch_date: Optional[date] = date.today()
    gross: float = Field(ge=0.00, le=9999999999.00)
    nar: Optional[str] = Field(max_length=100, default="")
    name: str = Field(max_length=500)
    closed: Optional[Literal[0, 1]] = 0
    entry_date: Optional[date] = date.today()
    our_qty: Optional[int] = None  # TODO: Add proper validations

    @model_validator(mode="before")
    @classmethod
    def validate_sch_date(cls, values):
        doc_date = values.get("doc_date")
        sch_date = values.get("sch_date")

        if doc_date and sch_date and sch_date < doc_date:
            raise ValueError("sch_date must be greater than or equal to doc_date")

        return values


class FormInput(BaseModel):
    po: PO
    po2: List[PO2]


class DcodeInput(IntEnum):
    po_type = (240,)
    payment = (6,)
    fr_type = (35,)
    inco = (134,)
    ins = (129,)
    dispatch_mode = (14,)
    trans_code = (62,)
    pack_type = (171,)
    port_load = (159,)
    port_disc = 160


class AllPoOutput(BaseModel, str_strip_whitespace=True):
    sl_no: int
    doc_no: int
    doc_date: date
    sup_code: str
    sup_name: str

    class Config:
        from_attributes = True


class DocInfoOutput(BaseModel, str_strip_whitespace=True):
    doc_no: str
    pref: str

    class Config:
        from_attributes = True


class SpecOutput(BaseModel):
    sl_no: int
    man_code: str
    man_name: str


class PO2ItemsOutput(global_schema.Output):
    sl_no: int
    unit_sl: int
    code: str
    name: str
    gst: Optional[float] = None
    gr_code: str
    uom_code: str
    sub_gr_code: str


class PurchaseOrderOnePrint(BaseModel):
    po_no: Optional[str]
    doc_date: Optional[date]
    supp_code: Optional[str]
    supp_name: Optional[str]
    supp_add1: Optional[str]
    supp_add2: Optional[str]
    supp_phone: Optional[str]
    supp_fax: Optional[str]
    supp_city_name: Optional[str]
    supp_pin: Optional[str]
    ship_to_name: Optional[str]
    ship_to_add1: Optional[str]
    ship_to_add2: Optional[str]
    ship_to_city_name: Optional[str]
    ship_to_pin: Optional[str]
    pay_terms_name: Optional[str]
    desp_mode_name: Optional[str]
    freight_name: Optional[str]
    pack_type_name: Optional[str]
    pl_code: Optional[str]
    pl_name: Optional[str]
    pd_code: Optional[str]
    pd_name: Optional[str]
    transporter_name: Optional[str]
    spl_ins_code: Optional[str]
    spl_ins_name: Optional[str]
    spl_remarks: Optional[str]
    inco_terms: Optional[str]
    insurance: Optional[str]
    test_cert: Optional[bool]
    currency_name: Optional[str]

    class Config:
        from_attributes = True


class PurchaseOrderTwoPrint(BaseModel):
    item_code: Optional[str]
    description: Optional[str]
    qty: Optional[float]
    uom: Optional[str]
    unit_price: Optional[float]
    gst_pc: Optional[float]
    sch_date: Optional[date]

    class Config:
        from_attributes = True


class PoPrint(BaseModel):
    po1: Optional[PurchaseOrderOnePrint]
    po2: Optional[List[PurchaseOrderTwoPrint]]
