// src/components/MapView.tsx
import React, { useEffect, useRef } from 'react';
import maplibregl, { Map as MLMap, Marker } from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';

export interface Vehicle {
  id: string;
  coordinates: [number, number];
  speed: number;
}

interface MapViewProps {
  vehicles: Vehicle[];
}

const STREET_STYLE = 'https://demotiles.maplibre.org/style.json';

const MapView: React.FC<MapViewProps> = ({ vehicles }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MLMap>();
  const markersRef = useRef<Marker[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: STREET_STYLE,
      center: [24.94, 60.17],
      zoom: 12,
    });

    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    map.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-right');

    mapRef.current = map;
    return () => map.remove();
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    vehicles.forEach(v => {
      const el = document.createElement('div');
      el.className = 'marker';
      el.style.width = '16px';
      el.style.height = '16px';
      el.style.background = 'red';
      el.style.borderRadius = '50%';
      el.title = `${v.id} — ${v.speed.toFixed(1)} km/h`;

      const marker = new maplibregl.Marker(el)
        .setLngLat(v.coordinates)
        .addTo(map);

      markersRef.current.push(marker);
    });
  }, [vehicles]);

  return (
    <div
      ref={containerRef}
      className="w-full h-full"
      style={{ position: 'relative' }}
    />
  );
};

export default MapView;
