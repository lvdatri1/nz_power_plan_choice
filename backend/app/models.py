from typing import Optional
from sqlalchemy import String, Float, Integer, Enum, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum

from app.db import Base


class RateType(str, enum.Enum):
    FLAT = "FLAT"
    TIERED = "TIERED"
    TOU = "TOU"


class Retailer(Base):
    __tablename__ = "retailers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    website: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    plans: Mapped[list["Plan"]] = relationship("Plan", back_populates="retailer", cascade="all, delete-orphan")


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    retailer_id: Mapped[int] = mapped_column(ForeignKey("retailers.id"))
    name: Mapped[str] = mapped_column(String(200))
    product_code: Mapped[Optional[str]] = mapped_column(String(50))
    rate_type: Mapped[RateType] = mapped_column(Enum(RateType))
    description: Mapped[Optional[str]] = mapped_column(String(2000))
    daily_charge: Mapped[float] = mapped_column(Float, default=0.0)
    is_solar: Mapped[bool] = mapped_column(Boolean, default=False)
    has_export: Mapped[bool] = mapped_column(Boolean, default=False)
    export_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    effective_from: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    effective_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="plans")
    flat_rates: Mapped[list["PlanRateFlat"]] = relationship("PlanRateFlat", back_populates="plan", cascade="all, delete-orphan")
    tier_rates: Mapped[list["PlanRateTier"]] = relationship("PlanRateTier", back_populates="plan", cascade="all, delete-orphan")
    tou_rates: Mapped[list["PlanRateTOU"]] = relationship("PlanRateTOU", back_populates="plan", cascade="all, delete-orphan")
    tou_export_rates: Mapped[list["PlanRateTOUExport"]] = relationship("PlanRateTOUExport", back_populates="plan", cascade="all, delete-orphan")


class PlanRateFlat(Base):
    __tablename__ = "plan_rates_flat"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    rate_per_kwh: Mapped[float] = mapped_column(Float)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="flat_rates")


class PlanRateTier(Base):
    __tablename__ = "plan_rates_tier"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    tier_min_kwh: Mapped[float] = mapped_column(Float)
    tier_max_kwh: Mapped[float] = mapped_column(Float)
    rate_per_kwh: Mapped[float] = mapped_column(Float)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="tier_rates")


class PlanRateTOU(Base):
    __tablename__ = "plan_rates_tou"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    label: Mapped[Optional[str]] = mapped_column(String(50))
    window_start: Mapped[int] = mapped_column(Integer)
    window_end: Mapped[int] = mapped_column(Integer)
    rate_per_kwh: Mapped[float] = mapped_column(Float)
    days_of_week: Mapped[Optional[str]] = mapped_column(String(50), default="weekdays")

    plan: Mapped["Plan"] = relationship("Plan", back_populates="tou_rates")


class PlanRateTOUExport(Base):
    __tablename__ = "plan_rates_tou_export"

    id: Mapped[int] = mapped_column(primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plans.id"))
    label: Mapped[Optional[str]] = mapped_column(String(50))
    window_start: Mapped[int] = mapped_column(Integer)
    window_end: Mapped[int] = mapped_column(Integer)
    rate_per_kwh: Mapped[float] = mapped_column(Float)
    days_of_week: Mapped[Optional[str]] = mapped_column(String(50), default="weekdays")

    plan: Mapped["Plan"] = relationship("Plan", back_populates="tou_export_rates")
