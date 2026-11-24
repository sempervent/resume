"""Pydantic models for the canonical career inventory."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, model_validator

ID_PATTERN = r"^[a-z0-9]+(?:[_-][a-z0-9]+)*$"

ALLOWED_CATEGORIES = {
    "data-architecture",
    "data-engineering",
    "platform-engineering",
    "technical-leadership",
    "software-engineering",
    "geospatial-engineering",
    "scientific-computing",
    "research-software",
    "api-design",
    "distributed-systems",
    "developer-productivity",
    "quality-assurance",
    "data-governance",
    "open-source",
}

SECTION_NAMES = (
    "summary",
    "skills",
    "experience",
    "projects",
    "education",
    "publications",
)


class Visibility(StrEnum):
    public = "public"
    private = "private"
    restricted = "restricted"


class Precision(StrEnum):
    year = "year"
    month = "month"
    day = "day"


class VerificationStatus(StrEnum):
    source_supported = "source-supported"
    owner_verification_required = "owner-verification-required"
    independently_checked = "independently-checked"


class FuzzyDate(BaseModel):
    year: int = Field(ge=1900, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)
    precision: Precision

    @model_validator(mode="after")
    def precision_matches_fields(self) -> FuzzyDate:
        if self.precision == Precision.year and (self.month is not None or self.day is not None):
            raise ValueError("year precision cannot include a month or day")
        if self.precision == Precision.month:
            if self.month is None or self.day is not None:
                raise ValueError("month precision requires a month and no day")
        if self.precision == Precision.day and (self.month is None or self.day is None):
            raise ValueError("day precision requires a month and day")
        return self


class Verification(BaseModel):
    status: VerificationStatus
    sources: list[str] = Field(min_length=1)


class Metric(BaseModel):
    name: str
    value: str
    unit: str | None = None
    verification: Verification
    review_required: bool = False


class Link(BaseModel):
    label: str
    url: str


class Identity(BaseModel):
    name: str
    headline: str
    tagline: str
    location_display: str
    links: list[Link] = Field(min_length=1)


class Employment(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    organization: str
    organization_detail: str | None = None
    title: str
    start: FuzzyDate
    end: FuzzyDate | None = None
    employment_type: Literal[
        "employee",
        "contract",
        "subcontractor",
        "graduate-appointment",
        "owner",
        "unknown",
    ] = "unknown"
    location: str | None = None
    remote_status: Literal["onsite", "remote", "hybrid", "unknown"] = "unknown"
    responsibilities: list[str] = Field(default_factory=list)
    achievement_ids: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    sources: list[str] = Field(min_length=1)
    visibility: Visibility = Visibility.public
    disclosure_notes: str | None = None
    notes: str | None = None
    featured: bool = True

    @model_validator(mode="after")
    def end_is_not_before_start(self) -> Employment:
        if self.end is not None and start_tuple(self.start) > end_tuple(self.end):
            raise ValueError(f"{self.id}: start date is after end date")
        return self


class Achievement(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    employment_id: str = Field(pattern=ID_PATTERN)
    statement: str
    categories: list[str] = Field(min_length=1)
    technologies: list[str] = Field(default_factory=list)
    verification: Verification
    metrics: list[Metric] = Field(default_factory=list)
    visibility: Visibility = Visibility.public
    review_required: bool = False
    disclosure_notes: str | None = None


class SkillItem(BaseModel):
    name: str
    detail: str | None = None


class SkillGroup(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    label: str
    items: list[SkillItem] = Field(min_length=1)
    verification: Verification
    visibility: Visibility = Visibility.public


class Project(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    name: str
    url: str | None = None
    summary: str
    technologies: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    verification: Verification
    visibility: Visibility = Visibility.public
    ownership: Literal["independent", "employer", "mixed", "unknown"] = "unknown"
    license: str | None = None
    review_required: bool = False
    maturity_notes: str | None = None


class Education(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    credential: str
    field: str | None = None
    organization: str
    date_display: str
    gpa: str | None = None
    honors: str | None = None
    verification: Verification
    visibility: Visibility = Visibility.public


class Summary(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    text: str
    verification: Verification


class ProfileRole(BaseModel):
    employment_id: str = Field(pattern=ID_PATTERN)
    achievement_ids: list[str] = Field(min_length=1)


class Profile(BaseModel):
    id: str = Field(pattern=ID_PATTERN)
    label: str
    document_kind: Literal["resume", "academic_cv"]
    document_name: str
    output_stem: str
    page_limit: int | None = None
    summary_id: str
    sections: list[
        Literal["summary", "skills", "experience", "projects", "education", "publications"]
    ]
    skill_group_ids: list[str] = Field(min_length=1)
    roles: list[ProfileRole] = Field(min_length=1)
    project_ids: list[str] = Field(min_length=1)
    show_gpa: bool = True


class PrivateContact(BaseModel):
    email: str | None = None
    phone: str | None = None


def start_tuple(value: FuzzyDate) -> tuple[int, int, int]:
    if value.precision == Precision.year:
        return (value.year, 1, 1)
    if value.precision == Precision.month:
        return (value.year, value.month or 1, 1)
    return (value.year, value.month or 1, value.day or 1)


def end_tuple(value: FuzzyDate) -> tuple[int, int, int]:
    if value.precision == Precision.year:
        return (value.year, 12, 31)
    if value.precision == Precision.month:
        return (value.year, value.month or 12, 31)
    return (value.year, value.month or 12, value.day or 31)


def format_fuzzy(value: FuzzyDate) -> str:
    months = (
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
    if value.precision == Precision.year or value.month is None:
        return str(value.year)
    if value.precision == Precision.month or value.day is None:
        return f"{months[value.month]} {value.year}"
    return f"{months[value.month]} {value.day}, {value.year}"


def format_range(start: FuzzyDate, end: FuzzyDate | None, dash: str = "–") -> str:
    left = format_fuzzy(start)
    if end is None:
        return f"{left}{dash}Present"
    return f"{left}{dash}{format_fuzzy(end)}"
