# SOMA — Phase 0: Data Acquisition & Derivation Guide

> **Purpose:** This document is the single reference for all data that must be **downloaded** before pipeline development begins, and how every **derived product** in the SOMA pipeline traces back to these raw inputs.

---

## Table of Contents

1. [Data Acquisition Summary](#1-data-acquisition-summary)
2. [Dataset Details](#2-dataset-details)
   - 2.1 [DFSAR L-band Polarimetric Data](#21-dfsar-l-band-polarimetric-data)
   - 2.2 [DFSAR S-band Polarimetric Data](#22-dfsar-s-band-polarimetric-data)
   - 2.3 [LOLA DEM (Global / Regional)](#23-lola-dem-global--regional)
   - 2.4 [TMC-2 Stereo DEM](#24-tmc-2-stereo-dem)
   - 2.5 [OHRC Imagery](#25-ohrc-imagery)
   - 2.6 [OHRC Stereo DEM](#26-ohrc-stereo-dem)
   - 2.7 [Pre-computed PSR Maps (LRO LOLA/Diviner)](#27-pre-computed-psr-maps-lro-loladiviner)
   - 2.8 [Crater Database (USGS / IAU)](#28-crater-database-usgs--iau)
3. [Derived Products Map](#3-derived-products-map)
4. [Data Flow Diagram](#4-data-flow-diagram)
5. [Pre-processing Requirements](#5-pre-processing-requirements)
6. [Directory Structure for Raw Data](#6-directory-structure-for-raw-data)
7. [Region of Interest](#7-region-of-interest)
8. [Checklist](#8-checklist)

---

## 1. Data Acquisition Summary

| # | Dataset | Source | Format | Approx. Resolution | Priority |
|---|---------|--------|--------|---------------------|----------|
| 1 | DFSAR L-band polarimetric data | ISRO PRADAN / ISSDC | PDS4 (.img / .xml) | ~2–75 m/pixel | **Critical** |
| 2 | DFSAR S-band polarimetric data | ISRO PRADAN / ISSDC | PDS4 (.img / .xml) | ~2–75 m/pixel | High |
| 3 | LOLA DEM | PDS Geosciences Node | GeoTIFF / IMG | ~5–20 m/pixel (LOLA) | **Critical** |
| 4 | TMC-2 stereo DEM | ISRO PRADAN / ISSDC | PDS4 | ~5 m/pixel | Medium |
| 5 | OHRC imagery | ISRO PRADAN / ISSDC | PDS4 (.img) | ~0.25 m/pixel | **Critical** |
| 6 | OHRC stereo DEM | ISRO PRADAN / ISSDC | PDS4 | ~1–2 m/pixel | Medium |
| 7 | Pre-computed PSR maps | PDS (LRO LOLA/Diviner) | GeoTIFF / IMG | ~20–240 m/pixel | **Critical** |
| 8 | Crater database | USGS / IAU Gazetteer | CSV / Shapefile | N/A (vector) | High |

> [!IMPORTANT]
> All raw datasets must be manually converted to **Cloud-Optimized GeoTIFFs (COGs)** before ingestion into the SOMA pipeline. The backend does **not** parse PDS4 archives directly. Use QGIS, GDAL CLI, or MIDAS for conversion.

---

## 2. Dataset Details

---

### 2.1 DFSAR L-band Polarimetric Data

**Instrument:** Chandrayaan-2 Dual Frequency Synthetic Aperture Radar (DFSAR)
**Frequency:** L-band (~1.25 GHz, ~24 cm wavelength)
**Penetration Depth:** Up to ~3–5 meters into lunar regolith

#### Source & Download

| Portal | URL |
|--------|-----|
| ISRO PRADAN | https://pradan.issdc.gov.in |
| ISRO ISSDC CHO-2 Archive | https://www.issdc.gov.in/cho2.html |

**How to find the data:**
1. Go to PRADAN → Search by instrument → Select "DFSAR"
2. Filter by region: Lunar South Pole (latitude < -80°)
3. Filter by product level: Look for Level-1 or Level-2 polarimetric products
4. Download the full-polarimetric (quad-pol) data if available, or hybrid-pol data
5. Each product will contain multiple polarimetric channels (HH, HV, VH, VV or hybrid-pol equivalents)

**What's inside the data:**
- Polarimetric backscatter channels (complex or intensity)
- Same-sense circular polarization (SC) backscatter power
- Opposite-sense circular polarization (OC) backscatter power
- Stokes parameters (S0, S1, S2, S3) — either provided directly or derivable from the polarimetric channels

#### What is derived from this dataset

| Derived Product | How It's Computed | Phase | Purpose in SOMA |
|----------------|-------------------|-------|-----------------|
| **CPR Map** | CPR = S_SC / S_OC (Same-sense / Opposite-sense circular polarization ratio) | Phase 2 | Primary indicator for subsurface ice. CPR > 1.0 indicates anomalous volume scattering consistent with ice inclusions in regolith. |
| **DoP Map** | DoP = √(S1² + S2² + S3²) / S0 (from Stokes parameters) | Phase 2 | Secondary ice discriminator. DoP < 0.13 indicates depolarized returns from volumetric scattering by subsurface inclusions (ice). Helps distinguish ice from surface roughness (which also elevates CPR). |
| **Radar Backscatter Maps** | Direct extraction of calibrated backscatter intensity per channel | Phase 2 | Used in ice concentration estimation (Phase 5) via dielectric mixing models. Also provides context for radar signature interpretation. |
| **Radar Confidence Layers** | Signal-to-noise ratio, look-count analysis | Phase 2 | Quantifies reliability of CPR/DoP values per pixel. Low-confidence areas are downweighted in ice detection fusion. |
| **Speckle-filtered Products** | Lee filter or Frost filter (5×5 window default) applied to raw backscatter | Phase 2 | Reduces multiplicative speckle noise inherent in SAR data before CPR/DoP computation. |

> [!NOTE]
> **CPR and DoP are NOT separate downloads.** They are both computed from the same DFSAR polarimetric product. You download the raw polarimetric data once, and the SOMA radar processing engine (Phase 2) computes CPR, DoP, and all derived radar products from it.

#### Integration into SOMA

```
DFSAR L-band (raw download)
    │
    ├─→ Speckle Filtering (Lee/Frost)
    │       │
    │       ├─→ CPR Computation ─→ CPR Map (GeoTIFF)
    │       │       └─→ Used in: Ice Detection (Phase 4), Ice Volume Estimation (Phase 5)
    │       │
    │       └─→ DoP Computation ─→ DoP Map (GeoTIFF)
    │               └─→ Used in: Ice Detection (Phase 4)
    │
    ├─→ Radar Backscatter Maps ─→ Used in: Ice Concentration Modeling (Phase 5)
    │
    └─→ Radar Confidence Layers ─→ Used in: Ice Detection Confidence (Phase 4)
```

---

### 2.2 DFSAR S-band Polarimetric Data

**Instrument:** Chandrayaan-2 DFSAR
**Frequency:** S-band (~2.5 GHz, ~12 cm wavelength)
**Penetration Depth:** Up to ~1–2 meters into lunar regolith

#### Source & Download

Same portals as L-band (PRADAN / ISSDC). Search for S-band products specifically.

**Why S-band in addition to L-band:**
- Shorter wavelength provides shallower penetration — acts as a **depth discriminator**
- If both L-band and S-band show elevated CPR, the scattering source extends from surface to several meters deep
- If only L-band shows elevated CPR but S-band does not, the ice is likely at **deeper levels** (>1 m)
- Cross-frequency comparison strengthens ice detection confidence

#### What is derived from this dataset

| Derived Product | How It's Computed | Phase | Purpose in SOMA |
|----------------|-------------------|-------|-----------------|
| **S-band CPR Map** | Same computation as L-band CPR, applied to S-band channels | Phase 2 | Cross-validation of L-band ice signatures |
| **S-band DoP Map** | Same computation as L-band DoP, applied to S-band Stokes parameters | Phase 2 | Cross-validation of depolarization signatures |
| **Dual-frequency Ratio Maps** | L-band CPR / S-band CPR per pixel | Phase 2 | Depth discrimination — identifies whether scattering is surface or subsurface |

#### Integration into SOMA

S-band products follow the exact same processing pipeline as L-band. The dual-frequency analysis adds a **cross-validation layer** to the ice detection fusion (Phase 4), increasing confidence in ice identification.

> [!WARNING]
> S-band DFSAR data availability for the south polar region may be limited. Check PRADAN for coverage. If unavailable, the project can proceed with L-band only — the pipeline is designed to work with single-frequency data.

---

### 2.3 LOLA DEM (Global / Regional)

**Instrument:** Lunar Reconnaissance Orbiter — Lunar Orbiter Laser Altimeter (LOLA)
**Coverage:** Global (with densest coverage at poles)
**Resolution:** ~5 m/pixel (polar gridded), ~20 m/pixel (global gridded)

#### Source & Download

| Portal | Product | URL |
|--------|---------|-----|
| PDS Geosciences Node | LOLA Gridded DEM (GDR) | https://ode.rsl.wustl.edu/moon/ |
| LOLA PDS Archive | Polar gridded products | https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/ |
| USGS Astrogeology | SLDEM2015 (LOLA + SELENE merged) | https://astrogeology.usgs.gov/search/map/Moon/LRO/LOLA/Lunar_LRO_LOLA_Global_LDEM_118m_Mar2014 |

**Recommended products:**
- **LOLA Polar Gridded DEM** at 5 m/pixel — best resolution for south pole study area
- **SLDEM2015** (LOLA + SELENE Kaguya terrain camera merged) — provides smoother global baseline at ~59 m/pixel if needed for wider context

**How to find the right tiles:**
1. Go to the PDS Orbital Data Explorer (ODE): https://ode.rsl.wustl.edu/moon/
2. Select Product Type → LOLA → RDR → GDR (Gridded Data Record)
3. Draw your region of interest on the south pole (latitude < -80°)
4. Download the polar stereographic gridded DEM tiles

#### What is derived from this dataset

| Derived Product | How It's Computed | Phase | Purpose in SOMA |
|----------------|-------------------|-------|-----------------|
| **Slope Map** | Gradient magnitude of DEM: slope = arctan(√(dz/dx² + dz/dy²)) | Phase 3 | Landing site safety (slope < 15°), rover traversability (slope < 25°), hazard assessment |
| **Aspect Map** | Gradient direction of DEM: aspect = atan2(dz/dy, dz/dx) | Phase 3 | Illumination geometry analysis, terrain orientation characterization |
| **Roughness Map** | RMS height deviation within a sliding window, or Terrain Ruggedness Index (TRI) | Phase 3 | Surface safety for landing, rover mobility assessment, hazard mapping |
| **Hazard Map** | Weighted composite: w₁·slope + w₂·roughness + w₃·boulder_density | Phase 3 | Composite safety assessment for landing and rover operations |
| **Mobility / Traversability Map** | Combined slope + roughness filtering against rover max tolerances | Phase 3 | Rover cost surface generation — input to path planning |
| **Cost Map (for Rover)** | Multi-factor weighted surface: slope + roughness + hazard + illumination penalty | Phase 5 | Direct input to A* / Dijkstra pathfinding algorithm for rover route generation |
| **Local Shadow Analysis** | Ray-tracing on small DEM subsets for specific craters (supplementary to pre-computed PSR) | Phase 3 | Refine shadow boundaries at high resolution for doubly-shadowed crater detection |
| **Doubly-Shadowed Crater Detection** | Analysis of crater-within-crater geometry using DEM morphology + PSR overlay | Phase 3 | Identifies craters that receive neither direct nor reflected sunlight — highest ice preservation potential |

> [!IMPORTANT]
> The DEM is the **most versatile dataset** in the project. It feeds into terrain analysis (Phase 3), landing site evaluation (Phase 4), and rover traverse planning (Phase 5). Resolution directly impacts the accuracy of all downstream products.

#### Integration into SOMA

```
LOLA DEM (raw download)
    │
    ├─→ Slope Computation ─────────┐
    ├─→ Aspect Computation ────────┤
    ├─→ Roughness Computation ─────┤
    │                              ▼
    │                    Hazard Map (composite)
    │                         │
    │                         ├─→ Landing Site Safety Scoring (Phase 4)
    │                         └─→ Rover Cost Map (Phase 5) ─→ A* Pathfinding
    │
    ├─→ Mobility Map ─────────────→ Rover Cost Map (Phase 5)
    │
    ├─→ Local Shadow Analysis ────→ Doubly-Shadowed Crater Detection (Phase 3)
    │                                    └─→ Ice Detection Fusion (Phase 4)
    │
    └─→ Crater Morphometry ───────→ Crater Catalog (Phase 3)
                                        └─→ Doubly-Shadowed Analysis
```

---

### 2.4 TMC-2 Stereo DEM

**Instrument:** Chandrayaan-2 Terrain Mapping Camera (TMC-2)
**Coverage:** Regional strips over south pole
**Resolution:** ~5 m/pixel

#### Source & Download

| Portal | URL |
|--------|-----|
| ISRO PRADAN | https://pradan.issdc.gov.in |
| ISRO ISSDC | https://www.issdc.gov.in/cho2.html |

**How to find the data:**
1. PRADAN → Search by instrument → Select "TMC-2"
2. Filter by region: South Pole
3. Look for DEM/DTM products (stereo-derived topographic products)
4. May be listed under Level-4 or higher processing levels

#### Purpose in SOMA

TMC-2 DEMs provide **regional-scale elevation enhancement** over the LOLA baseline. Where available, TMC-2 DEMs offer:
- Better spatial detail than LOLA in regional coverage
- Independent elevation validation against LOLA
- Improved terrain characterization in specific south polar areas

#### Integration into SOMA

TMC-2 DEM tiles are **merged with the LOLA DEM** to create a multi-resolution terrain model:
- LOLA provides the global/regional baseline
- TMC-2 fills in enhanced detail where its coverage overlaps
- The merge is done during Phase 0 pre-processing (QGIS/GDAL)

All derived products (slope, aspect, roughness, hazard, mobility, cost maps) benefit from the improved elevation accuracy in TMC-2-covered areas.

> [!NOTE]
> TMC-2 DEM availability for the south polar region may be limited. If not available, the project proceeds with LOLA DEM only — this is perfectly acceptable.

---

### 2.5 OHRC Imagery

**Instrument:** Chandrayaan-2 Orbiter High Resolution Camera
**Coverage:** Narrow swaths over targeted areas
**Resolution:** ~0.25 m/pixel (highest resolution lunar imagery from India)

#### Source & Download

| Portal | URL |
|--------|-----|
| ISRO PRADAN | https://pradan.issdc.gov.in |
| ISRO ISSDC | https://www.issdc.gov.in/cho2.html |

**How to find the data:**
1. PRADAN → Search by instrument → Select "OHRC"
2. Filter by region: South Pole (latitude < -80°)
3. Download imagery products (Level-1 or Level-2 radiometrically calibrated)
4. Note: OHRC has very narrow swath width (~3 km), so coverage is limited to specific targeted passes

**Important considerations:**
- OHRC imagery covers **very small areas** at extremely high resolution
- You will likely have only a few swaths over your study area
- Prioritize swaths that overlap with DFSAR coverage and candidate ice regions

#### What is derived from this dataset

| Derived Product | How It's Computed | Phase | Purpose in SOMA |
|----------------|-------------------|-------|-----------------|
| **Boulder Detection Map** | Morphological filtering, local contrast analysis, blob detection on high-res imagery | Phase 3 | Identify surface boulders that pose hazards for landing and rover traversal |
| **Boulder Density Map** | Count boulders per unit area within sliding window | Phase 3 | Quantitative hazard input for landing site evaluation |
| **Surface Texture Analysis** | Statistical texture metrics (variance, entropy) from pixel neighborhoods | Phase 3 | Surface roughness validation at sub-meter scale |
| **Visual Crater Analysis** | High-res morphological inspection of crater interiors | Phase 3 | Detailed assessment of doubly-shadowed crater floors |

> [!NOTE]
> OHRC is primarily a **visual inspection and hazard assessment** tool. It does NOT contribute to radar analysis or ice detection directly. Its role is to answer: "Is the surface physically safe for landing/roving at this specific location?"

#### Integration into SOMA

```
OHRC Imagery (raw download)
    │
    ├─→ Boulder Detection ──→ Boulder Density Map
    │                              │
    │                              └─→ Hazard Map (contributes boulder weight)
    │                                      │
    │                                      ├─→ Landing Site Safety (Phase 4)
    │                                      └─→ Rover Cost Map (Phase 5)
    │
    ├─→ Surface Texture Analysis ──→ Sub-meter Roughness Validation
    │
    └─→ Visual Crater Inspection ──→ Doubly-Shadowed Crater Detail Analysis (Phase 3)
```

---

### 2.6 OHRC Stereo DEM

**Instrument:** Chandrayaan-2 OHRC (stereo pairs from adjacent orbits)
**Coverage:** Very limited — only where stereo pair geometry exists
**Resolution:** ~1–2 m/pixel

#### Source & Download

Same portals as OHRC imagery (PRADAN / ISSDC). Look for stereo-derived DEM products specifically.

#### Purpose in SOMA

OHRC stereo DEMs provide the **highest resolution elevation data** available for the project:
- Sub-meter to 2-meter elevation detail within specific craters
- Critical for accurate doubly-shadowed crater analysis at fine scale
- Enables precise slope/roughness assessment at landing site resolution

#### Integration into SOMA

OHRC stereo DEMs are used as the **top tier** of the multi-resolution DEM hierarchy:

```
Elevation Data Hierarchy (coarse → fine):
    LOLA DEM (~5-20 m)  →  TMC-2 DEM (~5 m)  →  OHRC Stereo DEM (~1-2 m)
         │                      │                        │
         Global baseline        Regional detail          Local high-res
```

Where OHRC stereo DEMs exist, they replace/refine the LOLA/TMC-2 elevation data for that specific area, providing the most accurate terrain products.

> [!WARNING]
> OHRC stereo DEM availability is very limited. This is a "nice-to-have" dataset. If unavailable, the project proceeds with LOLA + TMC-2 without any loss of core functionality.

---

### 2.7 Pre-computed PSR Maps (LRO LOLA/Diviner)

**Instruments:** LRO LOLA (topography-derived illumination) + LRO Diviner (thermal measurements)
**Coverage:** Lunar south pole region
**Resolution:** ~20–240 m/pixel depending on product

#### Source & Download

| Portal | Product | URL |
|--------|---------|-----|
| PDS Geosciences Node | LOLA-derived illumination/PSR maps | https://pds-geosciences.wustl.edu/lro/lro-l-lola-3-rdr-v1/lrolol_1xxx/ |
| PDS Geosciences Node | Diviner polar resource products | https://pds-geosciences.wustl.edu/lro/lro-l-dlre-4-rdr-v1/lrodlr_1001/ |
| NASA LROC PSR Atlas | Permanently Shadowed Regions | http://lroc.sese.asu.edu/psr/ |
| Lunar QuickMap | Interactive PSR overlay | https://quickmap.lroc.asu.edu |

**Recommended products:**
- **LOLA-based illumination maps:** Computed from LOLA topography via ray-tracing over a full lunar year — shows percentage of time each pixel receives sunlight
- **Diviner maximum/average temperature maps:** Bolometric brightness temperature → regions consistently below ~110K are cold enough to trap water ice
- **Combined PSR binary mask:** Regions with 0% annual illumination

**What to download specifically:**
1. South polar illumination condition map (annual average, from LOLA ray-tracing)
2. PSR boundary polygons or raster mask (binary: permanently shadowed = 1, illuminated = 0)
3. Shadow persistence map (fraction of time in shadow over one lunar year)

#### Why pre-computed instead of self-generated

> [!IMPORTANT]
> Computing PSR maps from scratch requires ray-tracing solar illumination over an entire lunar year at high angular resolution against a DEM — this is **computationally prohibitive** for a hackathon timeline. The LRO team has already done this with validated methodology. Using their pre-computed products is both scientifically sound and time-efficient.

#### What is derived from this dataset

| Derived Product | How It's Computed | Phase | Purpose in SOMA |
|----------------|-------------------|-------|-----------------|
| **PSR Binary Mask** | Threshold on illumination map: pixels with 0% annual illumination → PSR = 1 | Phase 3 | Core input to ice detection — ice can only persist in permanently shadowed regions |
| **Shadow Persistence Map** | Directly from illumination condition data | Phase 3 | Graduated shadow assessment — regions with 99% shadow vs. 100% shadow have different ice preservation potential |
| **Shadow Confidence Map** | Uncertainty quantification based on DEM resolution and solar geometry accuracy | Phase 3 | Weights PSR contribution in ice detection fusion |
| **Doubly-Shadowed Crater Identification** | PSR mask + DEM crater morphometry → identify craters-within-craters that are always in shadow, even from indirect/reflected light | Phase 3 | Highest-confidence ice preservation locations — doubly-shadowed regions are the coldest, most thermally stable areas |

#### Integration into SOMA

```
Pre-computed PSR Maps (raw download)
    │
    ├─→ PSR Binary Mask ──────────────────→ Ice Detection Fusion (Phase 4)
    │                                            │
    │                                            └─→ Regions flagged as ice candidates
    │                                                  ONLY if within PSR
    │
    ├─→ Shadow Persistence Map ───────────→ Ice Probability Weighting (Phase 4)
    │                                            │
    │                                            └─→ Longer shadow duration → higher
    │                                                  ice preservation probability
    │
    ├─→ Shadow Confidence Map ────────────→ Ice Detection Confidence (Phase 4)
    │
    └─→ (Combined with DEM) ──────────────→ Doubly-Shadowed Crater Detection (Phase 3)
              │
              └─→ DEM morphometry identifies crater-in-crater geometry
                   PSR mask confirms permanent shadow status
                   Together → doubly-shadowed = highest ice confidence
```

---

### 2.8 Crater Database (USGS / IAU)

**Source:** USGS Astrogeology / International Astronomical Union (IAU) Gazetteer of Planetary Nomenclature
**Coverage:** Named craters across the entire lunar surface
**Format:** CSV, Shapefile, or online query

#### Source & Download

| Portal | URL |
|--------|-----|
| IAU Gazetteer | https://planetarynames.wr.usgs.gov/Page/MOON/target |
| USGS Planetary Nomenclature | https://planetarynames.wr.usgs.gov |
| Robbins Lunar Crater Database | https://astrogeology.usgs.gov/search/map/Moon/Research/Craters/lunar_crater_database_robbins_2018 |
| LPI Lunar South Pole Atlas | https://www.lpi.usra.edu/lunar/lunar-south-pole-atlas/ |

**What to download:**
1. **IAU Named Craters:** Official names, center coordinates, diameters for all named south polar craters
2. **Robbins (2018) Crater Database:** Comprehensive catalog of ~1.3 million craters with morphometric parameters (diameter, depth, d/D ratio, rim height, floor elevation)
3. **South Pole specific subset:** Filter for craters at latitude < -80°

#### Purpose in SOMA

| Usage | Phase | How It's Used |
|-------|-------|---------------|
| **Reference identification** | All phases | Associate coordinates with known crater names (e.g., "Shackleton," "Haworth," "Faustini," "Cabeus") |
| **Crater morphometry validation** | Phase 3 | Validate SOMA's crater detection algorithm against known catalog |
| **Doubly-shadowed candidate selection** | Phase 3 | Cross-reference large craters (which may contain smaller interior craters) for doubly-shadowed analysis |
| **Landing site context** | Phase 4 | Provide geographical context for landing site recommendations ("Site A is on the rim of Shackleton crater") |
| **Report generation** | Phase 4-6 | Human-readable reports reference crater names instead of raw coordinates |

#### Integration into SOMA

The crater database is loaded as a **GeoPandas GeoDataFrame** and serves as a reference layer throughout the project. It does NOT feed into any computation directly — it provides **context, validation, and labeling**.

---

## 3. Derived Products Map

This table shows every product generated by the SOMA pipeline, which raw dataset(s) it depends on, and in which phase it's produced.

### Phase 2 — Radar Processing (derived from DFSAR)

| Product | Raw Input(s) | Computation |
|---------|-------------|-------------|
| Speckle-filtered channels | DFSAR L-band, DFSAR S-band | Lee/Frost filter, 5×5 window |
| CPR Map | DFSAR (SC, OC channels) | CPR = S_SC / S_OC |
| DoP Map | DFSAR (Stokes S0-S3) | DoP = √(S1² + S2² + S3²) / S0 |
| Radar Backscatter Maps | DFSAR (all channels) | Calibrated intensity extraction |
| Radar Confidence Layers | DFSAR (SNR, look count) | SNR + look-count composite |
| Dual-frequency Ratio | DFSAR L-band + S-band | L-CPR / S-CPR per pixel |

### Phase 3 — Terrain & PSR (derived from DEMs + OHRC + PSR)

| Product | Raw Input(s) | Computation |
|---------|-------------|-------------|
| Slope Map | DEM (LOLA/TMC-2/OHRC) | arctan(√(dz/dx² + dz/dy²)) |
| Aspect Map | DEM | atan2(dz/dy, dz/dx) |
| Roughness Map | DEM | RMS height or TRI in sliding window |
| Boulder Density Map | OHRC imagery | Morphological detection + density counting |
| Crater Catalog | DEM + Crater Database | Automated detection + catalog cross-reference |
| Hazard Map | DEM + OHRC | w₁·slope + w₂·roughness + w₃·boulders |
| Mobility Map | DEM | Slope + roughness vs. rover max tolerances |
| PSR Binary Mask | Pre-computed PSR maps | Threshold on illumination = 0% |
| Shadow Persistence Map | Pre-computed PSR maps | Fraction of time in shadow |
| Doubly-Shadowed Craters | DEM + PSR maps | Crater geometry + shadow analysis |

### Phase 4 — Ice Detection & Landing Sites (derived from Phase 2 + 3 products)

| Product | Input Products | Computation |
|---------|---------------|-------------|
| Ice Probability Map | CPR + DoP + PSR mask + slope + roughness | Multi-criteria weighted fusion |
| Ice Confidence Map | Radar confidence + shadow confidence + data quality | Multi-layer agreement scoring |
| Candidate Ice Zones | Ice probability map | Threshold → connected components → polygons |
| Landing Suitability Surface | Hazard + ice proximity + solar access + slope | Multi-criteria weighted scoring |
| Ranked Landing Sites | Suitability surface | Local maxima extraction + safety filtering |
| Landing Site Reports | All above | Per-site detailed assessment JSON |

### Phase 5 — Rover Planning & Ice Volume (derived from Phase 3 + 4 products)

| Product | Input Products | Computation |
|---------|---------------|-------------|
| Cost Map | Slope + roughness + hazard + illumination | Multi-factor weighted surface |
| Rover Routes | Cost map + start/end coordinates | A* / Dijkstra pathfinding |
| Route Metrics | Routes + terrain data | Distance, energy, time, risk per segment |
| Ice Area Estimates | Ice probability map | Threshold-based area delineation |
| Ice Volume Estimates | Area + depth assumption + concentration | V = A × d × c; m = V × 917 kg/m³ |
| Uncertainty Intervals | Volume estimates | Monte Carlo over depth/concentration ranges |

---

## 4. Data Flow Diagram

```
╔══════════════════════════════════════════════════════════════════════╗
║                    RAW DATA (Phase 0 Downloads)                      ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  DFSAR L-band ──┐    LOLA DEM ──────┐    Pre-computed     Crater    ║
║  DFSAR S-band ──┤    TMC-2 DEM ─────┤    PSR Maps ───┐   Database  ║
║                 │    OHRC DEM ──────┤               │      │       ║
║                 │    OHRC Imagery ──┤               │      │       ║
╚════════╤════════╧════════╤══════════╧═══════════╤═══╧══════╤═══════╝
         │                 │                      │          │
         ▼                 ▼                      ▼          ▼
  ┌─────────────┐  ┌──────────────┐       ┌──────────┐  ┌────────┐
  │  Phase 2    │  │   Phase 3    │       │  Phase 3 │  │Reference│
  │  RADAR      │  │   TERRAIN    │       │   PSR    │  │  Layer  │
  │             │  │              │       │          │  │         │
  │ • CPR Map   │  │ • Slope      │       │ • PSR    │  │ • Names │
  │ • DoP Map   │  │ • Aspect     │       │   Mask   │  │ • Coords│
  │ • Backsctr  │  │ • Roughness  │       │ • Shadow │  │ • Sizes │
  │ • Confidence│  │ • Boulders   │       │   Persist│  │         │
  │             │  │ • Hazard     │       │ • Doubly │  │         │
  │             │  │ • Mobility   │       │   Shadow │  │         │
  └──────┬──────┘  └──────┬───────┘       └────┬─────┘  └────┬────┘
         │                │                     │             │
         └────────┬───────┴─────────┬───────────┘             │
                  │                 │                          │
                  ▼                 ▼                          │
          ┌──────────────┐  ┌──────────────┐                  │
          │   Phase 4    │  │   Phase 4    │                  │
          │ ICE DETECT   │  │ LANDING SITE │◄─────────────────┘
          │              │  │              │
          │ • Probability│  │ • Suitability│
          │ • Confidence │  │ • Ranked     │
          │ • Candidate  │  │   Sites      │
          │   Zones      │  │ • Reports    │
          └──────┬───────┘  └──────┬───────┘
                 │                 │
                 └────────┬────────┘
                          │
                          ▼
                 ┌────────────────┐
                 │    Phase 5     │
                 │ ROVER + VOLUME │
                 │                │
                 │ • Cost Map     │
                 │ • Routes (A*)  │
                 │ • Route Metrics│
                 │ • Ice Volume   │
                 │ • Uncertainty  │
                 └────────────────┘
```

---

## 5. Pre-processing Requirements

All raw datasets must be converted to **Cloud-Optimized GeoTIFFs (COGs)** before the SOMA backend can ingest them.

### Conversion Steps (for each dataset)

| Step | Tool | Command Example |
|------|------|-----------------|
| 1. Inspect raw data | `gdalinfo` | `gdalinfo raw_file.img` |
| 2. Convert to GeoTIFF | `gdal_translate` | `gdal_translate -of GTiff raw_file.img output.tif` |
| 3. Assign/verify CRS | `gdal_translate` or QGIS | Lunar CRS — typically IAU:30100 or custom south polar stereographic |
| 4. Reproject to common CRS | `gdalwarp` | `gdalwarp -t_srs "+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=1737400 +b=1737400 +units=m" input.tif reprojected.tif` |
| 5. Convert to COG | `gdal_translate` | `gdal_translate -of COG -co COMPRESS=DEFLATE reprojected.tif output_cog.tif` |
| 6. Validate | `gdalinfo` | `gdalinfo output_cog.tif` — check CRS, extent, resolution, band count |

### Common CRS for SOMA

All data should be reprojected to **Lunar South Polar Stereographic**:

```
+proj=stere +lat_0=-90 +lon_0=0 +k=1 +x_0=0 +y_0=0 +a=1737400 +b=1737400 +units=m +no_defs
```

- Centered on the south pole
- Lunar radius: 1,737,400 m (mean)
- Units: meters

### MIDAS for DFSAR

ISRO's MIDAS software may be required for initial DFSAR PDS4 extraction before GDAL conversion. Workflow:

```
DFSAR PDS4 Archive → MIDAS (extract/calibrate) → GeoTIFF → GDAL (reproject/COG) → SOMA
```

---

## 6. Directory Structure for Raw Data

All downloaded data should be placed into the following directory structure:

```
data/
└── raw/
    ├── dfsar/
    │   ├── l_band/
    │   │   ├── <orbit_id>_lband_sc.tif       # Same-sense circular pol
    │   │   ├── <orbit_id>_lband_oc.tif       # Opposite-sense circular pol
    │   │   ├── <orbit_id>_lband_s0.tif       # Stokes S0
    │   │   ├── <orbit_id>_lband_s1.tif       # Stokes S1
    │   │   ├── <orbit_id>_lband_s2.tif       # Stokes S2
    │   │   └── <orbit_id>_lband_s3.tif       # Stokes S3
    │   └── s_band/
    │       └── (same structure as l_band)
    │
    ├── ohrc/
    │   ├── imagery/
    │   │   └── <orbit_id>_ohrc.tif           # High-res imagery
    │   └── dem/
    │       └── <orbit_id>_ohrc_dem.tif        # Stereo-derived DEM (if available)
    │
    ├── dem/
    │   ├── lola/
    │   │   └── lola_south_pole_dem.tif        # LOLA gridded DEM
    │   ├── tmc2/
    │   │   └── tmc2_south_pole_dem.tif        # TMC-2 DEM (if available)
    │   └── merged/
    │       └── merged_south_pole_dem.tif       # Multi-resolution merged DEM
    │
    └── psr/
        ├── psr_mask.tif                        # Binary PSR mask
        ├── illumination_map.tif                # Annual illumination fraction
        └── shadow_persistence.tif              # Shadow duration fraction
```

> [!TIP]
> The `data/raw/dem/merged/` directory will contain the final multi-resolution DEM created by merging LOLA + TMC-2 + OHRC DEMs during pre-processing. This merged product is what the SOMA pipeline ingests.

---

## 7. Region of Interest

### Primary Study Area

**Lunar South Pole:** Latitude < -80°S

### Key Craters of Interest

| Crater | Latitude | Longitude | Diameter (km) | Significance |
|--------|----------|-----------|----------------|--------------|
| Shackleton | -89.9° | 0.0° | 21 | Interior permanently shadowed, rim nearly continuously illuminated |
| Haworth | -87.4° | -2.2° | 51 | Large PSR, LCROSS-related studies |
| Faustini | -87.3° | 77.0° | 39 | Deep PSR, possible ice deposits |
| de Gerlache | -88.5° | -87.1° | 32 | Adjacent to Shackleton, partial PSR |
| Cabeus | -85.3° | -35.7° | 98 | LCROSS impact site, confirmed water detection |
| Shoemaker | -88.1° | 44.9° | 50 | Large PSR, ice candidate |
| Sverdrup | -88.5° | -145.0° | 33 | Near south pole, PSR candidate |
| Amundsen | -84.5° | 82.8° | 105 | Large crater, Chandrayaan-3 vicinity |

### Coverage Considerations

- **DFSAR:** Check PRADAN for specific orbit passes covering these craters
- **OHRC:** Very narrow swath — likely only 1-2 craters will have OHRC coverage
- **LOLA DEM:** Full south polar coverage available
- **PSR Maps:** Full south polar coverage available

---

## 8. Checklist

### Downloads

- [ ] DFSAR L-band polarimetric data (south pole passes) from PRADAN
- [ ] DFSAR S-band polarimetric data (south pole passes) from PRADAN (if available)
- [ ] LOLA Polar Gridded DEM (~5 m/pixel) from PDS
- [ ] TMC-2 stereo DEM (south pole strips) from PRADAN (if available)
- [ ] OHRC imagery (south pole swaths) from PRADAN
- [ ] OHRC stereo DEM from PRADAN (if available)
- [ ] Pre-computed PSR maps (LRO LOLA illumination products) from PDS
- [ ] Diviner temperature maps from PDS (if available — not required)
- [ ] Crater database (Robbins 2018 + IAU named craters) from USGS

### Pre-processing

- [ ] Install MIDAS for DFSAR extraction (if needed)
- [ ] Convert all datasets to GeoTIFF using GDAL
- [ ] Reproject all datasets to Lunar South Polar Stereographic CRS
- [ ] Convert all GeoTIFFs to Cloud-Optimized GeoTIFFs (COGs)
- [ ] Merge multi-resolution DEMs (LOLA + TMC-2 + OHRC) where overlapping
- [ ] Validate all COGs with `gdalinfo` — check CRS, extent, resolution, NoData
- [ ] Place all processed files into `data/raw/` directory structure
- [ ] Create a 256×256 crop of each dataset for `backend/tests/data/golden/`

### Validation

- [ ] Open each COG in QGIS — visually confirm correct geolocation
- [ ] Verify PSR mask overlays correctly on DEM in QGIS
- [ ] Verify DFSAR coverage overlaps with study area craters
- [ ] Verify OHRC coverage and identify which craters have imagery
- [ ] Document any data gaps or missing coverage in this file

---

> [!CAUTION]
> **Data access note:** ISRO PRADAN may require registration and data request approval. Start the data request process early — access may not be instant. PDS (NASA) data is publicly accessible without registration.

---

*Last updated: 2026-06-19*
