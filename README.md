# Flight Price Tracker

`Flight Price Tracker` is a Python-based application for real-time monitoring of flight prices. It scrapes the web for flight information, tracks price changes, and stores the data for analysis. Integrating with Google Sheets, it offers an accessible interface for users to view and manage their tracked flights.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

---

## Project Structure

The application is organized into modular components within the `app` directory for clarity and maintainability.

### `main.py`

The heart of the application that initiates the service components and manages the flow of data.

### Configuration (`config.py`)

Centralized configuration settings for the application, including environmental variables and constants used across the application.

### Database Module (`app/database`)

Manages all data persistence and retrieval operations.

- `connection.py`: Facilitates database connectivity, utilizing SQLAlchemy for ORM support.
- `models/`: Contains SQLAlchemy ORM models.
  - `flight.py`: Represents a flight entity with attributes like price, date, and destination.
- `repository/`: Encapsulates the logic required to access data from the database.
  - `flight_repository.py`: Provides an abstraction layer to interact with `flight` data.

### Services Module (`app/services`)

Core business logic for the application's functionality.

- `scraping_service.py`: The service responsible for web scraping to gather flight price data.
- `sheets_service.py`: Handles operations related to Google Sheets, allowing for data export and visualization.

### Utilities Module (`app/utils`)

Auxiliary functions and classes supporting the application's operations.

- `chrome_driver.py`: Manages the ChromeDriver instance for web scraping, ensuring proper setup and teardown.
- `logger.py`: Configures application-wide logging, aiding in debugging and monitoring.
- `utils.py`: A collection of utility functions for string manipulation, data conversion, and other common tasks.

---

## Getting Started

To set up the project:

1. Clone the repository.
2. Ensure Docker is installed on your machine.
3. Navigate to the root directory of the project and run `docker-compose up` to build and start the services.
4. Modify the `.env` file with your configuration parameters (e.g., database URI, Google Sheets credentials).

---

## Usage

After setup, execute `main.py` to start the application. The tracker will begin scraping based on the intervals set in `config.py` and output data to the specified Google Sheets document.

---

## Contributing

We encourage community contributions. Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -am 'Add some amazing feature'`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a new Pull Request.

Before contributing, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed instructions on how to contribute to the project.

---

## License

This project is open-sourced under the MIT License. See the [LICENSE.md](LICENSE.md) file for full license text.

---
