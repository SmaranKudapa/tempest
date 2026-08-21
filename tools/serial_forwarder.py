import argparse
import json
import sys
import time
from dataclasses import dataclass
from typing import TextIO
from urllib.error import URLError
from urllib.request import Request, urlopen


DEFAULT_BACKEND_URL = "http://127.0.0.1:8000/readings"
DEFAULT_BAUD_RATE = 9600


@dataclass(frozen=True)
class SensorReading:
    temp_c: float
    humidity: float


def parse_sensor_line(line: str) -> SensorReading | None:
    values: dict[str, str] = {}

    for field in line.strip().split(","):
        if "=" not in field:
            continue

        key, value = field.split("=", 1)
        values[key.strip()] = value.strip()

    if values.get("status") != "ok":
        return None

    try:
        return SensorReading(
            temp_c=float(values["temp_c"]),
            humidity=float(values["humidity"]),
        )
    except (KeyError, ValueError):
        return None


def post_reading(reading: SensorReading, backend_url: str, timeout_seconds: float) -> int:
    payload = json.dumps(
        {
            "temp_c": reading.temp_c,
            "humidity": reading.humidity,
            "source": "arduino-uno-dht11",
        }
    ).encode("utf-8")

    request = Request(
        backend_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=timeout_seconds) as response:
        return response.status


def forward_lines(
    input_stream: TextIO,
    backend_url: str,
    timeout_seconds: float,
    retry_delay_seconds: float,
) -> None:
    for raw_line in input_stream:
        line = raw_line.strip()
        if not line:
            continue

        reading = parse_sensor_line(line)
        if reading is None:
            print(f"ignored: {line}")
            continue

        while True:
            try:
                status = post_reading(reading, backend_url, timeout_seconds)
                print(
                    "sent: "
                    f"temp_c={reading.temp_c:.1f},"
                    f"humidity={reading.humidity:.1f},"
                    f"status={status}"
                )
                break
            except URLError as error:
                print(f"backend unavailable: {error}. retrying...", file=sys.stderr)
                time.sleep(retry_delay_seconds)


def open_serial_port(port: str, baud_rate: int, timeout_seconds: float) -> TextIO:
    try:
        import serial
    except ImportError as error:
        raise SystemExit(
            "pyserial is required for serial mode. Install it with "
            "`python -m pip install -r tools/requirements.txt`."
        ) from error

    return serial.Serial(port, baud_rate, timeout=timeout_seconds)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read Tempest Arduino Serial output and forward readings to the backend."
    )
    parser.add_argument("--port", help="Arduino serial port, for example COM3 on Windows.")
    parser.add_argument("--baud-rate", type=int, default=DEFAULT_BAUD_RATE)
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--retry-delay-seconds", type=float, default=2.0)
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read lines from stdin instead of a serial port. Useful for local testing.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.stdin:
        forward_lines(
            sys.stdin,
            args.backend_url,
            args.timeout_seconds,
            args.retry_delay_seconds,
        )
        return

    if not args.port:
        raise SystemExit("Provide --port, or use --stdin for local testing.")

    with open_serial_port(args.port, args.baud_rate, args.timeout_seconds) as serial_port:
        forward_lines(
            serial_port,
            args.backend_url,
            args.timeout_seconds,
            args.retry_delay_seconds,
        )


if __name__ == "__main__":
    main()
