export type Reading = {
  id: number;
  temp_c: number;
  humidity: number;
  source: string;
  recorded_at: string;
};

export type DashboardReading = Reading & {
  isPlaceholder?: boolean;
};

export const placeholderReadings: DashboardReading[] = [
  {
    id: -1,
    temp_c: 22.8,
    humidity: 42.5,
    source: "placeholder",
    recorded_at: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    isPlaceholder: true,
  },
  {
    id: -2,
    temp_c: 23.1,
    humidity: 43.2,
    source: "placeholder",
    recorded_at: new Date(Date.now() - 4 * 60 * 1000).toISOString(),
    isPlaceholder: true,
  },
  {
    id: -3,
    temp_c: 22.6,
    humidity: 41.8,
    source: "placeholder",
    recorded_at: new Date(Date.now() - 6 * 60 * 1000).toISOString(),
    isPlaceholder: true,
  },
  {
    id: -4,
    temp_c: 22.9,
    humidity: 42.1,
    source: "placeholder",
    recorded_at: new Date(Date.now() - 8 * 60 * 1000).toISOString(),
    isPlaceholder: true,
  },
  {
    id: -5,
    temp_c: 23.3,
    humidity: 44.0,
    source: "placeholder",
    recorded_at: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
    isPlaceholder: true,
  },
];

export function formatReadingTime(value: string): string {
  return new Intl.DateTimeFormat("en", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(value));
}
