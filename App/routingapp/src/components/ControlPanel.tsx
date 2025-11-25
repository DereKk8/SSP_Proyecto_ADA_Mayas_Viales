"use client";

import { useState } from "react";
import FileUpload from "./FileUpload";
import type {
    NetworkResponse,
    PointsResponse,
    TSPResult,
    AlgorithmType,
} from "@/types";

interface ControlPanelProps {
    onLoadNetwork: (file: File) => Promise<void>;
    onLoadPoints: (file: File) => Promise<void>;
    onRunAlgorithm: (algorithm: AlgorithmType) => Promise<void>;
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

export default function ControlPanel({
    onLoadNetwork,
    onLoadPoints,
    onRunAlgorithm,
    networkData,
    pointsData,
    results,
    loading,
    errors,
}: ControlPanelProps) {
    const [networkFile, setNetworkFile] = useState<File | null>(null);
    const [pointsFile, setPointsFile] = useState<File | null>(null);
    const [selectedAlgorithm, setSelectedAlgorithm] =
        useState<AlgorithmType>("bruteforce");

    const handleNetworkFileSelect = async (file: File) => {
        setNetworkFile(file);
        await onLoadNetwork(file);
    };

    const handlePointsFileSelect = async (file: File) => {
        setPointsFile(file);
        await onLoadPoints(file);
    };

    const handleRunAlgorithm = async () => {
        if (selectedAlgorithm) {
            await onRunAlgorithm(selectedAlgorithm);
        }
    };

    const formatRuntime = (ms: number) => {
        if (ms < 1) return `${(ms * 1000).toFixed(2)} μs`;
        if (ms < 1000) return `${ms.toFixed(2)} ms`;
        return `${(ms / 1000).toFixed(2)} s`;
    };

    const formatLength = (length: number) => {
        if (length < 1000) return `${length.toFixed(2)} m`;
        return `${(length / 1000).toFixed(2)} km`;
    };

    return (
        <div className="h-full w-96 bg-white shadow-lg overflow-y-auto flex flex-col">
            <div className="p-6 flex-1">
                <h1 className="text-2xl font-bold text-gray-900 mb-6">
                    TSP Routing App
                </h1>

                {/* File Upload Section */}
                <div className="space-y-4 mb-6">
                    <FileUpload
                        label="1. Upload OSM Network"
                        accept=".osm,.pbf"
                        onFileSelect={handleNetworkFileSelect}
                        disabled={loading.network}
                        currentFileName={networkFile?.name}
                    />

                    {loading.network && (
                        <div className="flex items-center gap-2 text-blue-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            <span className="text-sm">Loading network...</span>
                        </div>
                    )}

                    {errors.network && (
                        <div className="text-red-600 text-sm bg-red-50 p-3 rounded">
                            {errors.network}
                        </div>
                    )}

                    {networkData && (
                        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <p className="font-medium text-gray-900 mb-1">
                                Network loaded:
                            </p>
                            <p>
                                Nodes:{" "}
                                {networkData.stats.nodes.toLocaleString()}
                            </p>
                            <p>
                                Edges:{" "}
                                {networkData.stats.edges.toLocaleString()}
                            </p>
                        </div>
                    )}

                    <FileUpload
                        label="2. Upload Points (TSV/CSV)"
                        accept=".tsv,.csv"
                        onFileSelect={handlePointsFileSelect}
                        disabled={!networkData || loading.points}
                        currentFileName={pointsFile?.name}
                    />

                    {loading.points && (
                        <div className="flex items-center gap-2 text-blue-600">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600" />
                            <span className="text-sm">Snapping points...</span>
                        </div>
                    )}

                    {errors.points && (
                        <div className="text-red-600 text-sm bg-red-50 p-3 rounded">
                            {errors.points}
                        </div>
                    )}

                    {pointsData && (
                        <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                            <p className="font-medium text-gray-900 mb-1">
                                Points snapped:
                            </p>
                            <p>Count: {pointsData.snapped_points.length}</p>
                        </div>
                    )}
                </div>

                {/* Algorithm Selection */}
                {pointsData && (
                    <div className="border-t pt-6 mt-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            3. Run TSP Algorithm
                        </h2>

                        <div className="space-y-3 mb-4">
                            <label className="flex items-center gap-3 p-3 border rounded cursor-pointer hover:bg-gray-50">
                                <input
                                    type="radio"
                                    name="algorithm"
                                    value="bruteforce"
                                    checked={selectedAlgorithm === "bruteforce"}
                                    onChange={(e) =>
                                        setSelectedAlgorithm(
                                            e.target.value as AlgorithmType
                                        )
                                    }
                                    className="w-4 h-4"
                                />
                                <div>
                                    <p className="font-medium text-gray-900">
                                        Brute-Force
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        Exact, n ≤ 12
                                    </p>
                                </div>
                            </label>

                            <label className="flex items-center gap-3 p-3 border rounded cursor-pointer hover:bg-gray-50">
                                <input
                                    type="radio"
                                    name="algorithm"
                                    value="heldkarp"
                                    checked={selectedAlgorithm === "heldkarp"}
                                    onChange={(e) =>
                                        setSelectedAlgorithm(
                                            e.target.value as AlgorithmType
                                        )
                                    }
                                    className="w-4 h-4"
                                />
                                <div>
                                    <p className="font-medium text-gray-900">
                                        Held-Karp DP
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        Exact, n ≤ 20
                                    </p>
                                </div>
                            </label>

                            <label className="flex items-center gap-3 p-3 border rounded cursor-pointer hover:bg-gray-50">
                                <input
                                    type="radio"
                                    name="algorithm"
                                    value="heuristic"
                                    checked={selectedAlgorithm === "heuristic"}
                                    onChange={(e) =>
                                        setSelectedAlgorithm(
                                            e.target.value as AlgorithmType
                                        )
                                    }
                                    className="w-4 h-4"
                                />
                                <div>
                                    <p className="font-medium text-gray-900">
                                        2-Opt Heuristic
                                    </p>
                                    <p className="text-xs text-gray-500">
                                        Approximate, scalable
                                    </p>
                                </div>
                            </label>
                        </div>

                        <button
                            onClick={handleRunAlgorithm}
                            disabled={loading.algorithm}
                            className="w-full bg-blue-600 text-white py-2 px-4 rounded font-medium
                       hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed
                       transition-colors"
                        >
                            {loading.algorithm
                                ? "Computing..."
                                : "Run Algorithm"}
                        </button>

                        {errors.algorithm && (
                            <div className="text-red-600 text-sm bg-red-50 p-3 rounded mt-4">
                                {errors.algorithm}
                            </div>
                        )}
                    </div>
                )}

                {/* Results Display */}
                {(results.bruteforce ||
                    results.heldkarp ||
                    results.heuristic) && (
                    <div className="border-t pt-6 mt-6">
                        <h2 className="text-lg font-semibold text-gray-900 mb-4">
                            Results
                        </h2>

                        <div className="space-y-3">
                            {results.bruteforce && (
                                <div className="bg-red-50 p-3 rounded border-l-4 border-red-500">
                                    <p className="font-medium text-gray-900">
                                        Brute-Force
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Length:{" "}
                                        {formatLength(
                                            results.bruteforce.length
                                        )}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Time:{" "}
                                        {formatRuntime(
                                            results.bruteforce.runtime_ms
                                        )}
                                    </p>
                                    {results.bruteforce.warning && (
                                        <div className="mt-2 p-2 bg-yellow-100 border border-yellow-300 rounded text-xs text-yellow-900">
                                            {results.bruteforce.warning}
                                        </div>
                                    )}
                                </div>
                            )}

                            {results.heldkarp && (
                                <div className="bg-green-50 p-3 rounded border-l-4 border-green-500">
                                    <p className="font-medium text-gray-900">
                                        Held-Karp
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Length:{" "}
                                        {formatLength(results.heldkarp.length)}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Time:{" "}
                                        {formatRuntime(
                                            results.heldkarp.runtime_ms
                                        )}
                                    </p>
                                </div>
                            )}

                            {results.heuristic && (
                                <div className="bg-purple-50 p-3 rounded border-l-4 border-purple-500">
                                    <p className="font-medium text-gray-900">
                                        2-Opt Heuristic
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Length:{" "}
                                        {formatLength(results.heuristic.length)}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Time:{" "}
                                        {formatRuntime(
                                            results.heuristic.runtime_ms
                                        )}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Info Footer */}
            <div className="border-t p-4 bg-gray-50">
                <p className="text-xs text-gray-600">
                    💡 <span className="font-medium">Tip:</span> The legend on
                    the map shows all visualization elements.
                </p>
            </div>
        </div>
    );
}
