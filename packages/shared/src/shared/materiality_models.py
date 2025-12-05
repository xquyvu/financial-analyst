from typing import Literal

from pydantic import BaseModel, Field

# List out all the financial metrics that could be refered to as dependencies by any
# other metric. Some examples are below.
type FINANCIAL_METRIC = Literal[
    "Capital Expenditure",
    "Change in Working Capital",
    "EBITDA",
    "Net Profit",
    "TFD/EBITDA (x)",
]


class MaterialChange(BaseModel):
    name: FINANCIAL_METRIC = Field(
        ...,
        description="The financial metric that has undergone a material change",
    )
    latest_yoy_pct: float = Field(
        ...,
        description="The year-over-year percentage change for the latest period",
    )


type MaterialChangesReport = list[MaterialChange]
