import unittest

from tools.serial_forwarder import SensorReading, parse_sensor_line


class ParseSensorLineTests(unittest.TestCase):
    def test_parses_valid_sensor_reading(self) -> None:
        reading = parse_sensor_line("status=ok,temp_c=23.4,humidity=41.0")

        self.assertEqual(reading, SensorReading(temp_c=23.4, humidity=41.0))

    def test_parses_valid_sensor_reading_with_whitespace(self) -> None:
        reading = parse_sensor_line(" status=ok, temp_c=23.4, humidity=41.0 ")

        self.assertEqual(reading, SensorReading(temp_c=23.4, humidity=41.0))

    def test_ignores_sensor_errors(self) -> None:
        reading = parse_sensor_line("status=error,error=sensor_read_failed")

        self.assertIsNone(reading)

    def test_ignores_malformed_readings(self) -> None:
        reading = parse_sensor_line("status=ok,temp_c=nope,humidity=41.0")

        self.assertIsNone(reading)


if __name__ == "__main__":
    unittest.main()

