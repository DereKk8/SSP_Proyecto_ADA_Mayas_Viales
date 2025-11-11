'use client';

import { useState, useCallback } from 'react';
import dynamic from 'next/dynamic';
import ControlPanel from '@/components/ControlPanel';
import MapLegend from '@/components/MapLegend';
import { api } from '@/utils/api';
import type { NetworkResponse, PointsResponse, TSPResult, AlgorithmType, AppState } from '@/types';

// Dynamically import Map component to avoid SSR issues with Leaflet
const MapComponent = dynamic(() => import('@/components/Map'), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-full bg-gray-100">
      <div className="text-gray-600">Loading map...</div>
    </div>
  ),
});

export default function Home() {
  const [state, setState] = useState<AppState>({
    networkData: null,
    pointsData: null,
    results: {},
    loading: {
      network: false,
      points: false,
      algorithm: false,
    },
    errors: {},
  });

  const handleLoadNetwork = useCallback(async (file: File) => {
    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, network: true },
      errors: { ...prev.errors, network: undefined },
      networkData: null,
      pointsData: null,
      results: {},
    }));

    try {
      const networkData = await api.loadNetwork(file);
      setState(prev => ({
        ...prev,
        networkData,
        loading: { ...prev.loading, network: false },
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, network: false },
        errors: { ...prev.errors, network: error instanceof Error ? error.message : 'Unknown error' },
      }));
    }
  }, []);

  const handleLoadPoints = useCallback(async (file: File) => {
    if (!state.networkData) return;

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, points: true },
      errors: { ...prev.errors, points: undefined },
      pointsData: null,
      results: {},
    }));

    try {
      const pointsData = await api.snapPoints(file);
      setState(prev => ({
        ...prev,
        pointsData,
        loading: { ...prev.loading, points: false },
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, points: false },
        errors: { ...prev.errors, points: error instanceof Error ? error.message : 'Unknown error' },
      }));
    }
  }, [state.networkData]);

  const handleRunAlgorithm = useCallback(async (algorithm: AlgorithmType) => {
    if (!state.pointsData || !state.networkData) return;

    setState(prev => ({
      ...prev,
      loading: { ...prev.loading, algorithm: true },
      errors: { ...prev.errors, algorithm: undefined },
    }));

    try {
      const pointIds = state.pointsData.snapped_points.map(p => p.id);
      const graphData = state.networkData.geojson;

      let result: TSPResult;
      switch (algorithm) {
        case 'bruteforce':
          result = await api.solveTSPBruteForce(pointIds, graphData);
          break;
        case 'heldkarp':
          result = await api.solveTSPHeldKarp(pointIds, graphData);
          break;
        case 'heuristic':
          result = await api.solveTSPHeuristic(pointIds, graphData);
          break;
      }

      setState(prev => ({
        ...prev,
        results: { ...prev.results, [algorithm]: result },
        loading: { ...prev.loading, algorithm: false },
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, algorithm: false },
        errors: { ...prev.errors, algorithm: error instanceof Error ? error.message : 'Unknown error' },
      }));
    }
  }, [state.pointsData, state.networkData]);

  return (
    <div className="flex h-screen">
      <ControlPanel
        onLoadNetwork={handleLoadNetwork}
        onLoadPoints={handleLoadPoints}
        onRunAlgorithm={handleRunAlgorithm}
        networkData={state.networkData}
        pointsData={state.pointsData}
        results={state.results}
        loading={state.loading}
        errors={state.errors}
      />
      <div className="flex-1 relative">
        <MapComponent
          networkData={state.networkData}
          pointsData={state.pointsData}
          results={state.results}
        />
        <MapLegend
          networkLoaded={!!state.networkData}
          pointsLoaded={!!state.pointsData}
          hasResults={Object.keys(state.results).length > 0}
          results={{
            bruteforce: !!state.results.bruteforce,
            heldkarp: !!state.results.heldkarp,
            heuristic: !!state.results.heuristic,
          }}
        />
      </div>
    </div>
  );
}
