'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap, CircleMarker, Popup } from 'react-leaflet';
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
                const pointId = feature.properties?.id;
                
                let marker;
                
                // Different colors for original vs snapped points
                if (pointType === 'original') {
                  // Original points (from TSV) - Blue
                  marker = L.circleMarker(latlng, {
                    radius: 7,
                    fillColor: '#3b82f6',
                    color: '#1e40af',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.7,
                  });
                } else if (pointType === 'snapped') {
                  // Snapped points (calculated on road) - Orange/Amber
                  marker = L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: '#f97316',
                    color: '#ea580c',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9,
                  });
                } else {
                  // Default fallback
                  marker = L.circleMarker(latlng, {
                    radius: 5,
                    fillColor: '#6b7280',
                    color: '#374151',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.6,
                  });
                }
                
                // Add tooltip with point ID (shows on hover)
                if (marker && pointId !== undefined) {
                  marker.bindTooltip(`Point ID: ${pointId}`, {
                    permanent: false,
                    direction: 'top',
                    className: 'point-tooltip',
                    offset: [0, -10]
                  });
                  
                  // Also add a popup for click (shows more info)
                  const snappedPoint = pointsData.snapped_points.find(p => p.id === pointId);
                  if (snappedPoint && pointType === 'snapped') {
                    const [lon, lat] = snappedPoint.snapped_coords;
                    const [origLon, origLat] = snappedPoint.original_coords;
                    const distance = Math.sqrt(
                      Math.pow(lon - origLon, 2) + Math.pow(lat - origLat, 2)
                    ) * 111000; // rough conversion to meters
                    
                    marker.bindPopup(`
                      <div style="text-align: center; min-width: 150px;">
                        <strong>Point ID: ${pointId}</strong><br/>
                        <span style="color: #f97316;">Snapped Point</span><br/>
                        <hr style="margin: 5px 0;"/>
                        <small>
                          Coords: ${lat.toFixed(6)}, ${lon.toFixed(6)}<br/>
                          Snap distance: ~${distance.toFixed(1)}m
                        </small>
                      </div>
                    `);
                  } else if (pointType === 'original') {
                    marker.bindPopup(`
                      <div style="text-align: center; min-width: 150px;">
                        <strong>Point ID: ${pointId}</strong><br/>
                        <span style="color: #3b82f6;">Original Point</span><br/>
                        <hr style="margin: 5px 0;"/>
                        <small>
                          From input TSV file<br/>
                          Coords: ${latlng.lat.toFixed(6)}, ${latlng.lng.toFixed(6)}
                        </small>
                      </div>
                    `);
                  }
                }
                
                return marker;
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

        {/* Start/End Point Markers for Brute Force */}
        {results.bruteforce && pointsData && typeof window !== 'undefined' && (() => {
          const L = require('leaflet');
          const startPointId = results.bruteforce.tour[0];
          const startPoint = pointsData.snapped_points.find(p => p.id === startPointId);
          if (startPoint) {
            const [lon, lat] = startPoint.snapped_coords;
            return (
              <>
                {/* Start/End marker (Green with white border) */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={10}
                  fillColor="#10b981"
                  color="#ffffff"
                  weight={3}
                  opacity={1}
                  fillOpacity={0.9}
                  eventHandlers={{
                    add: (e) => {
                      const marker = e.target;
                      marker.bindTooltip(`START/END (ID: ${startPointId})`, {
                        permanent: false,
                        direction: 'top',
                        className: 'point-tooltip',
                        offset: [0, -15]
                      });
                    }
                  }}
                >
                  <Popup>
                    <div className="text-center">
                      <strong>START/END POINT</strong><br/>
                      Point ID: {startPointId}<br/>
                      Algorithm: Brute Force<br/>
                      <small>Coords: {lat.toFixed(6)}, {lon.toFixed(6)}</small>
                    </div>
                  </Popup>
                </CircleMarker>
                {/* Inner dot for emphasis */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={4}
                  fillColor="#ffffff"
                  color="#10b981"
                  weight={1}
                  opacity={1}
                  fillOpacity={1}
                />
              </>
            );
          }
          return null;
        })()}

        {/* Start/End Point Markers for Held-Karp */}
        {results.heldkarp && pointsData && typeof window !== 'undefined' && (() => {
          const startPointId = results.heldkarp.tour[0];
          const startPoint = pointsData.snapped_points.find(p => p.id === startPointId);
          if (startPoint) {
            const [lon, lat] = startPoint.snapped_coords;
            return (
              <>
                {/* Start/End marker (Green with white border) */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={10}
                  fillColor="#10b981"
                  color="#ffffff"
                  weight={3}
                  opacity={1}
                  fillOpacity={0.9}
                  eventHandlers={{
                    add: (e) => {
                      const marker = e.target;
                      marker.bindTooltip(`START/END (ID: ${startPointId})`, {
                        permanent: false,
                        direction: 'top',
                        className: 'point-tooltip',
                        offset: [0, -15]
                      });
                    }
                  }}
                >
                  <Popup>
                    <div className="text-center">
                      <strong>START/END POINT</strong><br/>
                      Point ID: {startPointId}<br/>
                      Algorithm: Held-Karp<br/>
                      <small>Coords: {lat.toFixed(6)}, {lon.toFixed(6)}</small>
                    </div>
                  </Popup>
                </CircleMarker>
                {/* Inner dot for emphasis */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={4}
                  fillColor="#ffffff"
                  color="#10b981"
                  weight={1}
                  opacity={1}
                  fillOpacity={1}
                />
              </>
            );
          }
          return null;
        })()}

        {/* Start/End Point Markers for Heuristic */}
        {results.heuristic && pointsData && typeof window !== 'undefined' && (() => {
          const startPointId = results.heuristic.tour[0];
          const startPoint = pointsData.snapped_points.find(p => p.id === startPointId);
          if (startPoint) {
            const [lon, lat] = startPoint.snapped_coords;
            return (
              <>
                {/* Start/End marker (Green with white border) */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={10}
                  fillColor="#10b981"
                  color="#ffffff"
                  weight={3}
                  opacity={1}
                  fillOpacity={0.9}
                  eventHandlers={{
                    add: (e) => {
                      const marker = e.target;
                      marker.bindTooltip(`START/END (ID: ${startPointId})`, {
                        permanent: false,
                        direction: 'top',
                        className: 'point-tooltip',
                        offset: [0, -15]
                      });
                    }
                  }}
                >
                  <Popup>
                    <div className="text-center">
                      <strong>START/END POINT</strong><br/>
                      Point ID: {startPointId}<br/>
                      Algorithm: Heuristic<br/>
                      <small>Coords: {lat.toFixed(6)}, {lon.toFixed(6)}</small>
                    </div>
                  </Popup>
                </CircleMarker>
                {/* Inner dot for emphasis */}
                <CircleMarker
                  center={[lat, lon]}
                  radius={4}
                  fillColor="#ffffff"
                  color="#10b981"
                  weight={1}
                  opacity={1}
                  fillOpacity={1}
                />
              </>
            );
          }
          return null;
        })()}
      </MapContainer>
    </div>
  );
}

