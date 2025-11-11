'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import type { LatLngBounds } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { NetworkResponse, PointsResponse, TSPResult } from '@/types';

// Fix for default marker icon issue in Next.js
let defaultIconFixed = false;
if (typeof window !== 'undefined' && !defaultIconFixed) {
  const L = require('leaflet');
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  });
  defaultIconFixed = true;
}

interface MapBoundsUpdaterProps {
  bounds?: LatLngBounds;
}

function MapBoundsUpdater({ bounds }: MapBoundsUpdaterProps) {
  const map = useMap();
  
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);
  
  return null;
}

interface MapComponentProps {
  networkData: NetworkResponse | null;
  pointsData: PointsResponse | null;
  results: {
    bruteforce?: TSPResult;
    heldkarp?: TSPResult;
    heuristic?: TSPResult;
  };
}

export default function MapComponent({ networkData, pointsData, results }: MapComponentProps) {
  const [mapBounds, setMapBounds] = useState<LatLngBounds | undefined>(undefined);

  // Calculate bounds from network data when it changes
  useEffect(() => {
    if (networkData && typeof window !== 'undefined') {
      const L = require('leaflet');
      const { bounds } = networkData.stats;
      const newBounds = L.latLngBounds(
        [bounds.minLat, bounds.minLon],
        [bounds.maxLat, bounds.maxLon]
      );
      setMapBounds(newBounds);
    }
  }, [networkData]);

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={[0, 0]} // Generic world center - will auto-zoom to data bounds
        zoom={2} // World view initially
        className="h-full w-full"
        scrollWheelZoom={true}
        style={{ background: '#e0e0e0' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBoundsUpdater bounds={mapBounds} />

        {/* Network layer (gray) */}
        {networkData && (
          <GeoJSON
            key={`network-${JSON.stringify(networkData.stats)}`}
            data={networkData.geojson}
            style={{
              color: '#888888',
              weight: 2,
              opacity: 0.6,
            }}
          />
        )}

        {/* Points layer with different colors for original vs snapped */}
        {pointsData && (
          <GeoJSON
            key={`points-${pointsData.snapped_points.length}`}
            data={pointsData.geojson}
            pointToLayer={(feature, latlng) => {
              if (typeof window !== 'undefined') {
                const L = require('leaflet');
                const pointType = feature.properties?.type;
                
                // Different colors for original vs snapped points
                if (pointType === 'original') {
                  // Original points (from TSV) - Blue
                  return L.circleMarker(latlng, {
                    radius: 7,
                    fillColor: '#3b82f6',
                    color: '#1e40af',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.7,
                  });
                } else if (pointType === 'snapped') {
                  // Snapped points (calculated on road) - Orange/Amber
                  return L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: '#f97316',
                    color: '#ea580c',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9,
                  });
                }
                
                // Default fallback
                return L.circleMarker(latlng, {
                  radius: 5,
                  fillColor: '#6b7280',
                  color: '#374151',
                  weight: 1,
                  opacity: 1,
                  fillOpacity: 0.6,
                });
              }
              return null as any;
            }}
            style={(feature) => {
              // Style for snap lines (connecting original to snapped)
              if (feature?.properties?.type === 'snap_line') {
                return {
                  color: '#9ca3af',
                  weight: 1,
                  opacity: 0.5,
                  dashArray: '4, 4',
                };
              }
              return {};
            }}
          />
        )}

        {/* Brute-force path (red) */}
        {results.bruteforce && (
          <GeoJSON
            key={`bruteforce-${results.bruteforce.length}`}
            data={results.bruteforce.path_geojson}
            style={{
              color: '#ef4444',
              weight: 4,
              opacity: 0.8,
            }}
          />
        )}

        {/* Held-Karp path (green) */}
        {results.heldkarp && (
          <GeoJSON
            key={`heldkarp-${results.heldkarp.length}`}
            data={results.heldkarp.path_geojson}
            style={{
              color: '#22c55e',
              weight: 4,
              opacity: 0.8,
            }}
          />
        )}

        {/* Heuristic path (purple) */}
        {results.heuristic && (
          <GeoJSON
            key={`heuristic-${results.heuristic.length}`}
            data={results.heuristic.path_geojson}
            style={{
              color: '#a855f7',
              weight: 4,
              opacity: 0.8,
            }}
          />
        )}
      </MapContainer>
    </div>
  );
}

