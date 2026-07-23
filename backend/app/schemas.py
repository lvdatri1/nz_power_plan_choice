from datetime import datetime
import enum
from typing import Optional, Literal
from pydantic import BaseModel


class RateTypeEnum(str, enum.Enum):
    FLAT = "FLAT"
    TIERED = "TIERED"
    TOU = "TOU"


class RetailerBase(BaseModel):
    name: str
    slug: str
    website: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None


class RetailerCreate(RetailerBase):
    pass


class RetailerResponse(RetailerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FlatRateSchema(BaseModel):
    rate_per_kwh: float


class TierRateSchema(BaseModel):
    tier_min_kwh: float
    tier_max_kwh: float
    rate_per_kwh: float


class TouRateSchema(BaseModel):
    label: Optional[str] = None
    window_start: int
    window_end: int
    rate_per_kwh: float
    days_of_week: Optional[str] = "weekdays"


class PlanBase(BaseModel):
    name: str
    product_code: Optional[str] = None
    rate_type: RateTypeEnum
    description: Optional[str] = None
    daily_charge: float = 0.0
    is_solar: bool = False
    has_export: bool = False
    export_rate: Optional[float] = None
    active: bool = True


class PlanCreate(PlanBase):
    retailer_id: int
    flat_rates: list[FlatRateSchema] = []
    tier_rates: list[TierRateSchema] = []
    tou_rates: list[TouRateSchema] = []
    tou_export_rates: list[TouRateSchema] = []


class PlanResponse(PlanBase):
    id: int
    retailer_id: int
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    flat_rates: list[FlatRateSchema] = []
    tier_rates: list[TierRateSchema] = []
    tou_rates: list[TouRateSchema] = []
    tou_export_rates: list[TouRateSchema] = []
    retailer: Optional[RetailerResponse] = None

    class Config:
        from_attributes = True
        use_enum_values = True


class UsageRecord(BaseModel):
    timestamp: str
    kwh: float


class CostRequest(BaseModel):
    plan_id: int
    usage: list[UsageRecord]
    days: int = 0
    include_export: bool = False
    export_usage: list[UsageRecord] = []


class CostItem(BaseModel):
    label: str
    kwh: float
    rate: float
    cost: float


class CostBreakdown(BaseModel):
    import_cost: float
    export_credit: float = 0.0
    daily_charges: float = 0.0
    net_cost: float
    total_days: int
    items: list[CostItem] = []


class CostResponse(BaseModel):
    plan_id: int
    plan_name: str
    retailer_name: str
    rate_type: str
    breakdown: CostBreakdown
