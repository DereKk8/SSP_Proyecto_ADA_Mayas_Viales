'use client';

import type { TSPResult } from '@/types';

interface MapLegendProps {
  networkLoaded: boolean;
  pointsLoaded: boolean;
  hasResults: boolean;
  results: {
    bruteforce?: boolean;
    heldkarp?: boolean;
    heuristic?: boolean;
  };
  tourData?: {
    bruteforce?: TSPResult;
    heldkarp?: TSPResult;
    heuristic?: TSPResult;
  };
}

export default function MapLegend({ 
  networkLoaded, 
  pointsLoaded, 
  hasResults,
  results,
  tourData
}: MapLegendProps) {
  return (
    <div className="absolute bottom-6 right-6 bg-white rounded-lg shadow-lg p-4 z-[1000] max-w-xs max-h-[80vh] overflow-y-auto">
      <h3 className="text-sm font-bold text-gray-900 mb-3 border-b pb-2 sticky top-0 bg-white">
        Map Legend
      </h3>
      
      <div className="space-y-2 text-xs">
        {/* Network */}
        {networkLoaded && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-0.5 bg-gray-400 flex-shrink-0" />
            <span className="text-gray-700">Road Network</span>
          </div>
        )}
        
        {/* Points */}
        {pointsLoaded && (
          <>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-blue-500 border-2 border-blue-800 flex-shrink-0" />
              <span className="text-gray-700">Input Points (TSV)</span>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-orange-500 border-2 border-orange-700 flex-shrink-0" />
              <span className="text-gray-700">Snapped Points (Calculated)</span>
            </div>
            
            {hasResults && (
              <>
                <div className="flex items-center gap-3 pl-2 mt-1">
                  <div className="w-3.5 h-3.5 rounded-full bg-orange-500 border-2 border-orange-700 flex-shrink-0" />
                  <span className="text-gray-700 text-xs">✓ Used in solution (bright)</span>
                </div>
                
                <div className="flex items-center gap-3 pl-2">
                  <div className="w-2.5 h-2.5 rounded-full bg-orange-300 border border-orange-400 opacity-50 flex-shrink-0" />
                  <span className="text-gray-700 text-xs">✗ Excluded (dimmed)</span>
                </div>
              </>
            )}
            
            <div className="flex items-center gap-3">
              <div className="w-8 h-0.5 border-t border-dashed border-gray-400 flex-shrink-0" />
              <span className="text-gray-700">Snap Connection</span>
            </div>
          </>
        )}
        
        {/* TSP Paths */}
        {hasResults && (
          <div className="border-t pt-2 mt-2">
            <p className="font-semibold text-gray-900 mb-2">TSP Solutions:</p>
            
            {results.bruteforce && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-1 bg-red-500 flex-shrink-0" />
                <span className="text-gray-700">Brute-Force</span>
              </div>
            )}
            
            {results.heldkarp && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-1 bg-green-500 flex-shrink-0" />
                <span className="text-gray-700">Held-Karp</span>
              </div>
            )}
            
            {results.heuristic && (
              <div className="flex items-center gap-3">
                <div className="w-8 h-1 bg-purple-500 flex-shrink-0" />
                <span className="text-gray-700">2-Opt Heuristic</span>
              </div>
            )}
            
            {/* Start/End marker */}
            <div className="flex items-center gap-3 mt-2 pt-2 border-t">
              <div className="relative w-4 h-4 flex-shrink-0">
                <div className="absolute inset-0 rounded-full bg-green-500 border-2 border-white" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-white" />
                </div>
              </div>
              <span className="text-gray-700 font-medium">Start/End Point</span>
            </div>
          </div>
        )}
        
        {/* Route Order Section */}
        {hasResults && tourData && (
          <div className="border-t pt-2 mt-2">
            <p className="font-semibold text-gray-900 mb-2">Route Order:</p>
            
            {tourData.bruteforce && results.bruteforce && (
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-1 bg-red-500 flex-shrink-0" />
                  <span className="text-xs font-semibold text-gray-800">Brute-Force:</span>
                </div>
                <div className="text-xs text-gray-600 leading-relaxed pl-5">
                  {tourData.bruteforce.tour.map((id, index) => (
                    <span key={index}>
                      <span className="font-mono font-semibold text-gray-800">{id}</span>
                      {index < tourData.bruteforce.tour.length - 1 && ' → '}
                    </span>
                  ))}
                  {' → '}
                  <span className="font-mono font-semibold text-green-600">{tourData.bruteforce.tour[0]}</span>
                </div>
                <div className="text-xs text-gray-500 pl-5 mt-1">
                  Length: {(tourData.bruteforce.length / 1000).toFixed(2)} km
                </div>
              </div>
            )}
            
            {tourData.heldkarp && results.heldkarp && (
              <div className="mb-3">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-1 bg-green-500 flex-shrink-0" />
                  <span className="text-xs font-semibold text-gray-800">Held-Karp:</span>
                </div>
                <div className="text-xs text-gray-600 leading-relaxed pl-5">
                  {tourData.heldkarp.tour.map((id, index) => (
                    <span key={index}>
                      <span className="font-mono font-semibold text-gray-800">{id}</span>
                      {index < tourData.heldkarp.tour.length - 1 && ' → '}
                    </span>
                  ))}
                  {' → '}
                  <span className="font-mono font-semibold text-green-600">{tourData.heldkarp.tour[0]}</span>
                </div>
                <div className="text-xs text-gray-500 pl-5 mt-1">
                  Length: {(tourData.heldkarp.length / 1000).toFixed(2)} km
                </div>
              </div>
            )}
            
            {tourData.heuristic && results.heuristic && (
              <div className="mb-2">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-3 h-1 bg-purple-500 flex-shrink-0" />
                  <span className="text-xs font-semibold text-gray-800">2-Opt Heuristic:</span>
                </div>
                <div className="text-xs text-gray-600 leading-relaxed pl-5">
                  {tourData.heuristic.tour.map((id, index) => (
                    <span key={index}>
                      <span className="font-mono font-semibold text-gray-800">{id}</span>
                      {index < tourData.heuristic.tour.length - 1 && ' → '}
                    </span>
                  ))}
                  {' → '}
                  <span className="font-mono font-semibold text-green-600">{tourData.heuristic.tour[0]}</span>
                </div>
                <div className="text-xs text-gray-500 pl-5 mt-1">
                  Length: {(tourData.heuristic.length / 1000).toFixed(2)} km
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Empty state */}
        {!networkLoaded && !pointsLoaded && (
          <p className="text-gray-500 text-center py-2">
            Upload files to see legend
          </p>
        )}
      </div>
    </div>
  );
}

