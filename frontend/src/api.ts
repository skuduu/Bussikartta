// File: /volume1/docker/hslbussit/repo/frontend/src/api.ts

// Base URL for API; ensure you set VITE_API_URL in .env or default to current origin
const BASE_URL = import.meta.env.VITE_API_URL ?? '';

/**
 * Vehicle data returned by the API
 */
export interface Vehicle {
  vehicle_id: string;
  label: string;
  lat: number;
  lon: number;
  speed: number;
  timestamp: string;
}

/**
 * Fetch list of vehicles from backend
 */
export async function fetchVehicles(): Promise<Vehicle[]> {
  const url = `${BASE_URL}/vehicles`;
  console.debug('[api] fetching vehicles from', url);

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Failed to fetch vehicles: ${res.status} ${res.statusText}`);
  }

  const data = await res.json();
  console.debug('[api] vehicles response:', data);
  return data;
}