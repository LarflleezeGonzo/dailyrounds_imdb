from typing import Any
from app.core.db import get_db
from fastapi import APIRouter, Depends
from app.schemas import MovieQueryParams, MovieListResponse
from sqlalchemy.orm import Session
from app.movie_service import MovieService

router = APIRouter(tags=["Movies"])


@router.get("/movies")
def get_movies(
    params: MovieQueryParams = Depends(), db: Session = Depends(get_db)
) -> Any:
    """
    Get Movies.
    """

    movies, total = MovieService.get_movies(db=db, params=params)
    content = MovieListResponse(items=movies, total=total)
    return content
