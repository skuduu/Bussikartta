import React, { useRef, useEffect } from 'react';
import mapboxgl from 'mapbox-gl';

// Ensure your Mapbox token is set in REACT_APP_MAPBOX_TOKEN
mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN!;

const OverviewMap: React.FC = () => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const mapInstance = useRef<mapboxgl.Map | null>(null);

  useEffect(() => {
    // Initialize map once
    if (!mapInstance.current && mapContainer.current) {
      mapInstance.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/streets-v11',
        center: [0, 0], // [lng, lat]
        zoom: 1,        // world view
      });

      // Add zoom & rotation controls (navigation)
      mapInstance.current.addControl(new mapboxgl.NavigationControl());
      // Add scale bar
      mapInstance.current.addControl(new mapboxgl.ScaleControl({ unit: 'metric' }));
    }

    // Clean up on unmount
    return () => mapInstance.current?.remove();
  }, []);

  return (
    <div
      ref={mapContainer}
      className="w-full h-full"
      style={{ minHeight: '400px' }}
    />
  );
};

export default OverviewMap;
