from sqlalchemy.orm import Session

from app.database.models.flight import Flight


class FlightRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def generate_flight_id(self, departure_date, return_date):
        departure_str = departure_date.strftime("%Y%m%d")
        return_str = return_date.strftime("%Y%m%d")
        return int(departure_str + return_str)

    def insert_or_update_flight(self, flight_data):
        # Tu implementación de insert_or_update_flight aquí
        flight_id = self.generate_flight_id(
            flight_data['departure_date'],
            flight_data['return_date']
        )
        flight = self.db_session.query(Flight).get(flight_id)
        if flight:
            # Upgrades existing flight
            for key, value in flight_data.items():
                setattr(flight, key, value)
            self.db_session.commit()
        else:
            # Insert a new flight
            flight = Flight(id=flight_id, **flight_data)
            self.db_session.add(flight)
            self.db_session.commit()
        return flight
