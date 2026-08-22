import { NextResponse } from "next/server";

const backendBaseUrl = process.env.TEMPEST_BACKEND_BASE_URL ?? "http://127.0.0.1:8000";

export async function GET() {
  try {
    const response = await fetch(`${backendBaseUrl}/readings/latest`, {
      cache: "no-store",
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: "Backend latest-reading endpoint returned an error." },
        { status: 502 },
      );
    }

    return NextResponse.json(await response.json());
  } catch {
    return NextResponse.json(
      { error: "Backend latest-reading endpoint is unavailable." },
      { status: 502 },
    );
  }
}
