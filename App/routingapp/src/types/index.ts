// TypeScript interfaces for the application

export interface NetworkStats {
    nodes: number;
    edges: number;
    bounds: {
        minLat: number;
        maxLat: number;
        minLon: number;
        maxLon: number;
    };
}

export interface NetworkResponse {
    stats: NetworkStats;
    geojson: GeoJSON.FeatureCollection;
}

export interface Point {
    id: number;
    x: number;
    y: number;
}

export interface SnappedPoint {
    id: number;
    original_coords: [number, number];
    snapped_coords: [number, number];
    nearest_edge: [number, number];
}

export interface PointsResponse {
    snapped_points: SnappedPoint[];
    geojson: GeoJSON.FeatureCollection;
}

export interface TSPResult {
    tour: number[];
    length: number;
    runtime_ms: number;
    path_geojson: GeoJSON.Feature<GeoJSON.LineString>;
    warning?: string;
}

export type AlgorithmType = "bruteforce" | "heldkarp" | "heuristic";

export interface AlgorithmResult {
    algorithm: AlgorithmType;
    result?: TSPResult;
    error?: string;
}

export interface AppState {
    networkData: NetworkResponse | null;
    pointsData: PointsResponse | null;
    results: {
        bruteforce?: TSPResult;
        heldkarp?: TSPResult;
        heuristic?: TSPResult;
    };
    loading: {
        network: boolean;
        points: boolean;
        algorithm: boolean;
    };
    errors: {
        network?: string;
        points?: string;
        algorithm?: string;
    };
}
