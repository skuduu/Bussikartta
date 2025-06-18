import React, { useState, useEffect } from 'react';
import MapView, { type Vehicle } from './components/MapView';

interface ApiVehicle {
  vehicle_id: string;
  label: string;
  lat: number | null;
  lon: number | null;
  speed: number | null;
}

const backendHost = window.location.hostname;
const backendPort = 8007;

const App: React.FC = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);

  useEffect(() => {
    const fetchVehicles = () => {
      fetch(`http://${backendHost}:${backendPort}/vehicles`)
        .then(res => {
          if (!res.ok) throw new Error('HTTP ' + res.status);
          return res.json() as Promise<ApiVehicle[]>;
        })
        .then(data => {
          const mapped = data
            .map<Vehicle | null>(d => {
              if (d.lat == null || d.lon == null || d.speed == null) return null;
              return {
                id: d.label,
                coordinates: [d.lon, d.lat],
                speed: d.speed,
              };
            })
            .filter((v): v is Vehicle => v !== null);

          console.log(`[poll] ${new Date().toISOString()} – received ${mapped.length} vehicles`);
          if (mapped.length > 0) {
            console.log('example:', mapped[0]);
          }

          setVehicles(mapped);
        })
        .catch(err => console.error('Failed to load vehicles:', err));
    };

    fetchVehicles();
    const interval = setInterval(fetchVehicles, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex h-screen">
      <aside className="w-64 bg-gray-100">
        <div className="p-4 font-bold">Bussikartta Controls</div>
      </aside>
      <main className="flex-1">
        <MapView vehicles={vehicles} />
      </main>
    </div>
  );
};

export default App;
