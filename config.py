YEAR = 2026
GRAND_PRIX = "British"
CACHE_DIR = "cache"

# 2026 race fuel is about 70 kg per secondary sources (f1chronicle, planetf1); not checked against the fia pdf
FUEL_START_KG = 70.0
# 0.03 s/kg comes from analyses of the heavier 2025 cars, treat as an assumption
FUEL_EFFECT_S_PER_KG = 0.03
FUEL_EFFECT_SENSITIVITY = (0.02, 0.03, 0.04)

QUICKLAP_THRESHOLD = 1.07
MIN_STINT_LAPS = 5
MIN_STINTS_PER_COMPOUND = 5

# stage 2
QUALI_SESSION = "Q"
FULL_THROTTLE_PCT = 99
LIFT_COAST_MIN_M = 20
APEX_WINDOW_M = 75
BRAKE_ONSET_SEARCH_M = 400
PICKUP_SEARCH_M = 500
