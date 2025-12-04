from typing import Literal

from pydantic import BaseModel, Field

# List out all the financial metrics that could be refered to as dependencies by any
# other metric
type FINANCIAL_METRIC = Literal["Gross Profit", "Cost of Sales"]


class MaterialChange(BaseModel):
    metric: FINANCIAL_METRIC = Field(
        ...,
        description="The financial metric that has undergone a material change",
    )
    material_change: str = Field(
        ...,
        description="Description of the material change that should be included in the FA",
    )
    dependencies: list[FINANCIAL_METRIC] = Field(
        ...,
        description="List of financial metrics that are dependencies for this material change",
    )


class MaterialChangesReport(BaseModel):
    material_changes: list[MaterialChange]
