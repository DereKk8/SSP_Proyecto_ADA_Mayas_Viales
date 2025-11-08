from fastapi import APIRouter

router = APIRouter()

# Placeholders - will be implemented in Phases 4-6
@router.post("/bruteforce")
async def solve_bruteforce():
    return {"message": "Brute-force TSP endpoint - to be implemented in Phase 4"}

@router.post("/heldkarp")
async def solve_heldkarp():
    return {"message": "Held-Karp TSP endpoint - to be implemented in Phase 5"}

@router.post("/heuristic")
async def solve_heuristic():
    return {"message": "Heuristic TSP endpoint - to be implemented in Phase 6"}

