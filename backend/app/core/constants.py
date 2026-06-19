"""
SOMA Scientific and System Constants.

All thresholds and physical constants used across the processing pipeline.
Each value includes a brief rationale; see docs/scientific_assumptions.md
for full literature references once that document is created.
"""

# ── Physical Constants ───────────────────────────────────────

# Density of pure water ice (kg/m³)
ICE_DENSITY_KG_M3: float = 917.0

# Mean lunar radius (m) — IAU 2015 value
LUNAR_RADIUS_M: float = 1_737_400.0

# ── Radar Thresholds ────────────────────────────────────────

# Circular Polarization Ratio threshold for ice-indicative anomalous scattering.
# CPR > 1.0 suggests volume scattering consistent with subsurface ice or
# very rough surfaces; must be correlated with PSR and DOP for confirmation.
CPR_ICE_THRESHOLD: float = 1.0

# Degree of Polarization threshold for depolarized (ice-consistent) returns.
# DOP < 0.13 indicates depolarization from subsurface inclusions such as
# ice lenses within regolith.
DOP_ICE_THRESHOLD: float = 0.13

# ── Terrain Safety Thresholds ───────────────────────────────

# Maximum surface slope (degrees) considered safe for spacecraft landing.
MAX_LANDING_SLOPE_DEG: float = 15.0

# Maximum surface slope (degrees) a rover can traverse.
MAX_ROVER_SLOPE_DEG: float = 25.0

# ── Ice Estimation Assumptions ──────────────────────────────

# Assumed depth of ice-bearing regolith layer (m).
# Based on DFSAR L-band penetration depth (~5 m into dry regolith).
ICE_DEPTH_ASSUMPTION_M: float = 5.0

# Default ice concentration range for uncertainty analysis (fraction, 0-1).
ICE_CONCENTRATION_MIN: float = 0.01   # 1%
ICE_CONCENTRATION_MAX: float = 0.30   # 30%

# ── Coordinate Reference Systems ────────────────────────────

# Lunar south polar stereographic projection.
# Used as the common CRS for all aligned raster products.
# EPSG-equivalent for Moon; uses IAU 2015 lunar sphere.
LUNAR_SOUTH_POLAR_STEREO_PROJ4: str = (
    "+proj=stere +lat_0=-90 +lon_0=0 +k=1 "
    "+x_0=0 +y_0=0 +R=1737400 +units=m +no_defs"
)

# Standard lunar geographic CRS (longitude/latitude on a sphere).
LUNAR_LONLAT_PROJ4: str = (
    "+proj=longlat +R=1737400 +no_defs"
)
