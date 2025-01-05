from typing import List, Tuple

from fastapi import HTTPException
from sqlalchemy import asc, desc, extract
from sqlalchemy.orm import Query, Session

from app.models import Movie
from app.schemas import MovieQueryParams


class MovieService:
    """Service layer for movie-related operations."""

    SORT_CONFIGS = {
        "vote_average": {
            "secondary_sort": ("vote_count", "desc"),
            "default_direction": "desc",
        },
        "release_date": {"default_direction": "desc"},
        "revenue": {"secondary_sort": ("budget", "desc"), "default_direction": "desc"},
    }
    DEFAULT_SORT_FIELD = "release_date"

    @staticmethod
    def get_movies(db: Session, params: MovieQueryParams) -> Tuple[List[Movie], int]:
        """
        Get movies based on query parameters.

        Args:
            db: Database session
            params: Query parameters

        Returns:
            Tuple containing:
                - List of movies for current page
                - Total number of movies matching filters
        """
        try:
            query = db.query(Movie)
            query = MovieService._apply_filters(query, params)
            query = MovieService._apply_dynamic_sorting(
                query, params.sort_by.value, params.sort_order.value
            )

            total = query.count()
            movies = (
                query.offset((params.page - 1) * params.page_size)
                .limit(params.page_size)
                .all()
            )

            return movies, total

        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error retrieving movies: {str(e)}"
            )

    @staticmethod
    def _apply_filters(query: Query, params: MovieQueryParams) -> Query:
        """Apply filters to query based on parameters."""
        if params.release_year:
            query = query.filter(
                extract("year", Movie.release_date) == params.release_year
            )

        if params.language:
            query = query.filter(Movie.original_language == params.language)

        return query

    @staticmethod
    def _get_sort_direction(direction: str):
        """Get sort direction function based on string value."""
        return desc if direction == "desc" else asc

    @staticmethod
    def _get_column_or_default(field: str) -> str:
        """Get valid column name or fall back to default."""
        return field if hasattr(Movie, field) else MovieService.DEFAULT_SORT_FIELD

    @staticmethod
    def _apply_dynamic_sorting(query: Query, sort_field: str, sort_order: str) -> Query:
        """
        Dynamically apply sorting to query with fallback and secondary sort support.

        Args:
            query: SQLAlchemy query
            sort_field: Field to sort by
            sort_order: Sort direction ('asc' or 'desc')

        Returns:
            Sorted query
        """

        sort_config = MovieService.SORT_CONFIGS.get(
            sort_field, {"default_direction": "desc"}
        )

        direction = sort_order or sort_config.get("default_direction")
        direction_func = MovieService._get_sort_direction(direction)

        primary_field = MovieService._get_column_or_default(sort_field)
        primary_col = getattr(Movie, primary_field)
        order_clauses = [direction_func(primary_col)]

        secondary_sort = sort_config.get("secondary_sort")
        if secondary_sort:
            sec_field, sec_direction = secondary_sort
            if hasattr(Movie, sec_field):
                sec_col = getattr(Movie, sec_field)
                sec_direction_func = MovieService._get_sort_direction(sec_direction)
                order_clauses.append(sec_direction_func(sec_col))

        return query.order_by(*order_clauses)
