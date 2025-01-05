from typing import Optional, List
from datetime import date
from pydantic import BaseModel, Field
from enum import Enum


class SortField(str, Enum):
    """Valid fields for sorting movies."""

    RELEASE_DATE = "release_date"
    RATINGS = "vote_average"


class SortOrder(str, Enum):
    """Valid sort orders."""

    ASC = "asc"
    DESC = "desc"


class MovieQueryParams(BaseModel):
    """Query parameters for movie endpoints."""

    page: int = Field(1, gt=0, description="Page number")
    page_size: int = Field(10, gt=0, le=100, description="Items per page")
    release_year: Optional[int] = Field(None, description="Filter by release year")
    language: Optional[str] = Field(None, description="Filter by original language")
    sort_by: SortField = Field(SortField.RELEASE_DATE, description="Field to sort by")
    sort_order: SortOrder = Field(SortOrder.DESC, description="Sort order")


class MovieResponse(BaseModel):
    id: Optional[int] = None
    title: Optional[str] = None
    original_title: Optional[str] = None
    original_language: Optional[str] = None
    overview: Optional[str] = None
    release_date: Optional[date] = None
    budget: Optional[int] = None
    revenue: Optional[int] = None
    runtime: Optional[int] = None
    status: Optional[str] = None
    vote_average: Optional[float] = None
    vote_count: Optional[int] = None
    languages: Optional[List[str]] = None
    homepage: Optional[str] = None
    genre_id: Optional[int] = None
    production_company_id: Optional[int] = None

    class Config:
        from_attributes = True
        arbitrary_types_allowed = True
        validate_assignment = False

class MovieListResponse(BaseModel):
    items: List[MovieResponse]
    total: int


