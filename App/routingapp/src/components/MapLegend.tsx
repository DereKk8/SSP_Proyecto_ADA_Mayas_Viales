'use client';

interface MapLegendProps {
  networkLoaded: boolean;
  pointsLoaded: boolean;
  hasResults: boolean;
  results: {
    bruteforce?: boolean;
    heldkarp?: boolean;
    heuristic?: boolean;
  };
}

export default function MapLegend({ 
  networkLoaded, 
  pointsLoaded, 
  hasResults,
  results 
}: MapLegendProps) {
  return (
    <div className="absolute bottom-6 right-6 bg-white rounded-lg shadow-lg p-4 z-[1000] max-w-xs">
      <h3 className="text-sm font-bold text-gray-900 mb-3 border-b pb-2">
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

