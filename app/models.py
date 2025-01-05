from sqlalchemy import (
    Column,
    Date,
    Float,
    Index,
    Integer,
    String,
    Text,
    BigInteger
)
from sqlalchemy.dialects.postgresql import ARRAY

from app.core.db import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    original_title = Column(String(255))
    original_language = Column(String(10))
    overview = Column(Text)
    release_date = Column(Date)
    budget = Column(BigInteger)
    revenue = Column(BigInteger)
    runtime = Column(Integer)
    status = Column(String(20))
    vote_average = Column(Float)
    vote_count = Column(Integer)
    languages = Column(ARRAY(String))
    homepage = Column(String(500))
    genre_id = Column(Integer)
    production_company_id = Column(Integer)
    __table_args__ = (
        Index("idx_movies_release_year_lang", release_date.desc(), original_language),
        Index("idx_movies_vote_average", vote_average.desc(), vote_count.desc()),
        Index("idx_movies_release_date", release_date.desc()),
        Index("idx_movies_original_language", original_language),
        Index("idx_movies_genre_id", genre_id),
        Index("idx_movies_production_company_id", production_company_id),
    )
