# Tempest

Reliable Indoor Climate Telemetry.

Tempest is an indoor climate monitoring project that connects physical hardware to a backend system and a web dashboard. The project reads temperature and humidity from a sensor, sends that data into software, and organizes it so it can be stored, viewed, and used by other parts of the application.

The hardware side uses an Arduino Uno R3 connected to a DHT11 temperature and humidity sensor and a 16x2 LCD display. The Arduino reads the sensor data and shows the current room conditions on the LCD.

The backend side is the main software focus of the project. It is where the sensor readings can be received, validated, stored, and served through an API. Through Tempest, I am learning how backend systems work with real-world data instead of only static examples.

The frontend side uses Next.js to display the climate data in a web dashboard. This gives the project a simple full-stack structure: hardware collects the data, the backend processes it, and the frontend shows it to the user.

## Hardware

- Arduino Uno R3
- DHT11 temperature and humidity sensor
- 16x2 LCD display
- Breadboard and jumper wires

## Wiring

- DHT11 data -> Arduino D2
- LCD RS -> Arduino D7
- LCD Enable -> Arduino D8
- LCD D4 -> Arduino D3
- LCD D5 -> Arduino D4
- LCD D6 -> Arduino D5
- LCD D7 -> Arduino D6
- LCD RW -> GND

## Software and Skills

- C++ for Arduino firmware
- Arduino framework for reading sensors and controlling hardware
- Python for backend development
- FastAPI for building API endpoints
- Pydantic for validating incoming sensor data
- SQLAlchemy for working with database models
- PostgreSQL for storing temperature and humidity readings
- Docker for running backend services in a consistent environment
- Next.js for building the web dashboard
- React for creating frontend components
- TypeScript for safer frontend code
- REST API design for sending data between the hardware, backend, and dashboard
- Sensor data handling for real temperature and humidity readings
- LCD output for displaying live measurements
- Git and GitHub for version control and project organization

Tempest combines embedded systems, backend development, databases, and basic electronics into one hands-on project.
