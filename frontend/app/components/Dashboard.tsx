"use client";

import { useEffect, useMemo, useState } from "react";

import {
  type DashboardReading,
  type Reading,
  formatReadingTime,
  placeholderReadings,
} from "../lib/readings";

type DashboardState = {
  readings: DashboardReading[];
  mode: "loading" | "live" | "placeholder";
  message: string;
};

const refreshMs = 5000;

async function fetchJson<T>(url: string): Promise<T> {
  const response = await fetch(url, { cache: "no-store" });

  if (!response.ok) {
    throw new Error(`Request failed with ${response.status}`);
  }

  return response.json() as Promise<T>;
}

function normalizeReadings(readings: Reading[]): DashboardReading[] {
  return readings.map((reading) => ({ ...reading, isPlaceholder: false }));
}

function useDashboardReadings(): DashboardState {
  const [state, setState] = useState<DashboardState>({
    readings: placeholderReadings,
    mode: "loading",
    message: "Waiting for backend readings...",
  });

  useEffect(() => {
    let active = true;

    async function loadReadings() {
      try {
        const readings = await fetchJson<Reading[]>("/api/readings");

        if (!active) {
          return;
        }

        if (readings.length === 0) {
          setState({
            readings: placeholderReadings,
            mode: "placeholder",
            message: "No stored readings yet. Showing placeholder data.",
          });
          return;
        }

        setState({
          readings: normalizeReadings(readings),
          mode: "live",
          message: "Live data from Tempest backend.",
        });
      } catch {
        if (!active) {
          return;
        }

        setState({
          readings: placeholderReadings,
          mode: "placeholder",
          message: "Backend unavailable. Showing placeholder data.",
        });
      }
    }

    loadReadings();
    const interval = window.setInterval(loadReadings, refreshMs);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return state;
}

function getComfortLabel(tempC: number, humidity: number): string {
  if (tempC < 18) {
    return "Cool";
  }

  if (tempC > 27 || humidity > 65) {
    return "Needs attention";
  }

  if (humidity < 30) {
    return "Dry";
  }

  return "Comfortable";
}

function getTrend(readings: DashboardReading[], field: "temp_c" | "humidity"): string {
  if (readings.length < 2) {
    return "Stable";
  }

  const latest = readings[0][field];
  const previous = readings[Math.min(readings.length - 1, 4)][field];
  const delta = latest - previous;

  if (Math.abs(delta) < 0.2) {
    return "Stable";
  }

  return delta > 0 ? "Rising" : "Falling";
}

function HistoryChart({ readings }: { readings: DashboardReading[] }) {
  const points = useMemo(() => [...readings].reverse().slice(-12), [readings]);
  const temperatures = points.map((reading) => reading.temp_c);
  const humidities = points.map((reading) => reading.humidity);
  const minTemp = Math.min(...temperatures) - 1;
  const maxTemp = Math.max(...temperatures) + 1;
  const minHumidity = Math.min(...humidities) - 4;
  const maxHumidity = Math.max(...humidities) + 4;

  function pathFor(values: number[], min: number, max: number): string {
    const width = 560;
    const height = 180;
    const range = Math.max(max - min, 1);

    return values
      .map((value, index) => {
        const x = values.length === 1 ? width : (index / (values.length - 1)) * width;
        const y = height - ((value - min) / range) * height;
        return `${index === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
      })
      .join(" ");
  }

  return (
    <section className="panel chart-panel" aria-label="Reading history chart">
      <div className="panel-header">
        <div>
          <p className="eyebrow">History</p>
          <h2>Recent climate movement</h2>
        </div>
        <div className="legend" aria-label="Chart legend">
          <span><i className="temp-key" />Temperature</span>
          <span><i className="humidity-key" />Humidity</span>
        </div>
      </div>
      <svg viewBox="0 0 560 180" role="img" aria-label="Temperature and humidity line chart">
        <path className="grid-line" d="M 0 45 L 560 45" />
        <path className="grid-line" d="M 0 90 L 560 90" />
        <path className="grid-line" d="M 0 135 L 560 135" />
        <path className="temp-line" d={pathFor(temperatures, minTemp, maxTemp)} />
        <path className="humidity-line" d={pathFor(humidities, minHumidity, maxHumidity)} />
      </svg>
    </section>
  );
}

export default function Dashboard() {
  const { readings, mode, message } = useDashboardReadings();
  const latest = readings[0];
  const isPlaceholder = mode !== "live";
  const comfort = getComfortLabel(latest.temp_c, latest.humidity);

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Tempest</p>
          <h1>Indoor climate dashboard</h1>
        </div>
        <div className={`status-pill ${isPlaceholder ? "placeholder" : "live"}`}>
          <span />
          {isPlaceholder ? "Placeholder data" : "Live backend"}
        </div>
      </header>

      <section className="summary-band" aria-label="Current conditions">
        <div className="metric-card primary">
          <p>Temperature</p>
          <strong>{latest.temp_c.toFixed(1)} C</strong>
          <span>{getTrend(readings, "temp_c")}</span>
        </div>
        <div className="metric-card">
          <p>Humidity</p>
          <strong>{latest.humidity.toFixed(1)}%</strong>
          <span>{getTrend(readings, "humidity")}</span>
        </div>
        <div className="metric-card">
          <p>Room state</p>
          <strong>{comfort}</strong>
          <span>{formatReadingTime(latest.recorded_at)}</span>
        </div>
      </section>

      <div className="notice" role="status">
        {message}
      </div>

      <div className="content-grid">
        <HistoryChart readings={readings} />

        <section className="panel readings-panel" aria-label="Recent readings">
          <div className="panel-header compact">
            <div>
              <p className="eyebrow">Log</p>
              <h2>Recent readings</h2>
            </div>
          </div>
          <div className="reading-list">
            {readings.slice(0, 8).map((reading) => (
              <div className="reading-row" key={reading.id}>
                <div>
                  <strong>{formatReadingTime(reading.recorded_at)}</strong>
                  <span>{reading.source}</span>
                </div>
                <p>{reading.temp_c.toFixed(1)} C</p>
                <p>{reading.humidity.toFixed(1)}%</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}
