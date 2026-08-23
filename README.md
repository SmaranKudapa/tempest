# Tempest

Reliable Indoor Climate Telemetry.

![Tempest dashboard screenshot](docs/dashboard.png)

Tempest is a full-stack indoor climate monitoring project that connects a physical temperature/humidity sensor to a backend API, PostgreSQL database, and web dashboard. The system reads live room conditions from a DHT11 sensor, moves those readings through a small software pipeline, stores them, and displays them in a browser.

## Project Goal

The goal of Tempest is to demonstrate how real-world sensor data moves through a complete application stack:

```text
DHT11 sensor
-> Arduino Uno R3
-> USB Serial
-> Python serial forwarder
-> FastAPI backend
-> PostgreSQL database
-> Next.js dashboard
```

This project is designed to be both practical and explainable. It combines embedded systems, backend API design, database persistence, and frontend visualization in one end-to-end workflow.

## Architecture

Tempest is split into six main parts:

| Layer | Technology | Responsibility |
| --- | --- | --- |
| Sensor | DHT11 | Measures room temperature and humidity. |
| Firmware | Arduino C++ | Reads the sensor, updates the LCD, and prints structured readings over USB Serial. |
| Bridge | Python | Reads Serial output from the Arduino and forwards valid readings to the backend. |
| Backend | FastAPI, Pydantic, SQLAlchemy | Validates readings, exposes API endpoints, and saves data. |
| Storage | PostgreSQL | Stores climate readings so they survive backend restarts. |
| Frontend | Next.js, React, TypeScript | Displays current conditions, recent readings, and a history chart. |

The Arduino does not call the web API directly. Instead, it sends simple text over USB Serial because an Arduino Uno R3 does not have built-in Wi-Fi or Ethernet. A Python bridge runs on the computer connected to the Arduino, parses those Serial lines, and sends HTTP requests to the FastAPI backend.

The backend is the boundary between raw device data and the rest of the application. It validates incoming readings, stores them in PostgreSQL, and serves them through API endpoints that the dashboard can read.

The dashboard talks to local Next.js API routes, and those routes proxy requests to FastAPI. This keeps the browser-facing frontend simple and avoids browser CORS issues during local development.

## Data Flow

A successful reading moves through the system like this:

1. The DHT11 measures temperature and humidity.
2. The Arduino reads the sensor every 2 seconds.
3. The Arduino prints a structured Serial line:

```text
status=ok,temp_c=23.4,humidity=41.0
```

4. The Python forwarder reads the Serial line and parses it into numbers.
5. The forwarder sends the reading to the backend:

```http
POST /readings
```

6. FastAPI validates the request body with Pydantic.
7. SQLAlchemy saves the reading into PostgreSQL.
8. The Next.js dashboard fetches recent readings and updates the UI.

If the sensor read fails, the Arduino prints an error line instead. The Python bridge ignores failed sensor lines so bad readings are not stored.

## API Endpoints

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/health` | `GET` | Confirms the backend is running. |
| `/readings` | `POST` | Stores a new temperature/humidity reading. |
| `/readings` | `GET` | Returns recent readings. |
| `/readings/latest` | `GET` | Returns the newest stored reading. |

Example reading payload:

```json
{
  "temp_c": 23.4,
  "humidity": 41.0,
  "source": "arduino-uno-dht11"
}
```

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

## Run Locally

Run these commands from the project folder:

```powershell
cd "C:\Users\smara\Documents\Projects\tempest"
```

Install backend dependencies:

```powershell
python -m pip install -r backend/requirements.txt
```

Start PostgreSQL:

```powershell
docker compose up -d postgres
```

Start the backend:

```powershell
python -m uvicorn backend.app.main:app --reload
```

In a second terminal, install frontend dependencies and start the dashboard:

```powershell
cd frontend
npm install
npm run dev
```

Open the dashboard:

```text
http://localhost:3000
```

## Arduino Live Mode

Upload the firmware in `firmware/tempest_sensor_node/tempest_sensor_node.ino` to the Arduino. Then install the serial bridge dependency:

```powershell
python -m pip install -r tools/requirements.txt
```

Run the bridge, replacing `COM3` with the Arduino port shown by the Arduino IDE:

```powershell
python tools/serial_forwarder.py --port COM3
```

When readings are forwarded successfully, the bridge prints output like:

```text
sent: temp_c=23.4,humidity=41.0,status=201
```

## Demo Mode

The dashboard can still run when the backend is unavailable or no readings have been stored yet. In that case, it shows clearly labeled placeholder readings instead of a broken screen. This makes the frontend useful during development and easier to demo while the hardware is disconnected.

You can also test the bridge without the Arduino:

```powershell
'status=ok,temp_c=23.4,humidity=41.0' | python tools/serial_forwarder.py --stdin
```

Then check the latest reading:

```powershell
curl http://127.0.0.1:8000/readings/latest
```

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
- Serial output for sending hardware readings to software
- Git and GitHub for version control and project organization

## Interview Summary

Tempest is an end-to-end telemetry project. The embedded layer collects real sensor data, the bridge translates USB Serial output into HTTP requests, the backend validates and persists readings, and the frontend visualizes the data. The design separates responsibilities clearly: hardware measures, the bridge transports, the backend owns data integrity, the database provides durability, and the dashboard presents the information to the user.

