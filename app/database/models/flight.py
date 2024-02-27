from sqlalchemy import Column, BigInteger, Date, Integer, Numeric, String, Text, TIMESTAMP, func

from app.database.models.base import Base


class Flight(Base):
    __tablename__ = 'flights'

    id = Column(BigInteger, primary_key=True)
    departure_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=False)
    days_count = Column(Integer, nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)
    average_price_per_day = Column(Numeric(10, 2), nullable=False)
    average_duration = Column(String(255), nullable=False)
    search_link = Column(Text, nullable=False)
    updated_at = Column(TIMESTAMP, default=func.now(), onupdate=func.now())
