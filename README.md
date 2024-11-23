 # FCC Orifice Chamber Cleaning Simulation

A Python-based simulation tool for analyzing and optimizing the cleaning process of Fluid Catalytic Cracking (FCC) orifice chambers using various cleaning media.

## Overview

This project simulates and analyzes the effectiveness of different cleaning methods for FCC orifice chambers, focusing on deposit removal and cleaning optimization. It combines fluid dynamics, particle tracking, and impact analysis to provide comprehensive insights into the cleaning process.

### Key Features
- 3D simulation of chamber geometry and fluid flow
- Particle trajectory tracking with deposit interaction
- Multiple cleaning media comparison (walnut shells, ceramic balls, steel shot)
- Real-time visualization and animation
- Deposit removal effectiveness analysis
- Technical report generation
- Time-dependent deposit evolution modeling

## Technical Specifications

### Chamber Geometry
- Inlet Diameter: 2558 mm
- Grid Diameter: 3800 mm
- Chamber Height: 12000 mm
- Grid Configuration:
  - Grid 1: 285 holes
  - Grid 2: 300 holes
  - Grid 3: 315 holes
  - Grid 4: 330 holes

### Operating Conditions
- Temperature: 715°C
- Pressure: 1.52 kg/cm²
- Flow Velocity: 17.2-17.7 m/s

## Installation

1. Clone the repository:
```bash
git clone https://github.com/rajaminyak/fcc_simulation.git
cd fcc_simulation
```

2. Create and activate virtual environment:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Usage

### Basic Simulation
```bash
python src/main.py
```

### Comprehensive Analysis
```bash
python src/main.py --comprehensive
```

### Multiple Particle Simulation
```bash
python src/main.py --multi 10
```

## Analysis Features

1. Cleaning Media Comparison
   - Walnut shells
   - Ceramic balls
   - Steel shot

2. Performance Metrics
   - Removal efficiency
   - Impact energy distribution
   - Coverage patterns
   - Cost analysis

3. Time Evolution Analysis
   - Deposit accumulation modeling
   - Cleaning cycle optimization
   - Maintenance scheduling

## Visualization

The simulation provides:
- 3D chamber visualization
- Particle trajectory animation
- Deposit removal visualization
- Impact pattern analysis
- Time evolution plots

## Project Structure
```
fcc_simulation/
├── src/
│   ├── analysis/
│   │   └── analyzer.py
│   ├── models/
│   │   ├── chamber.py
│   │   ├── particle.py
│   │   └── deposit.py
│   ├── utils/
│   │   ├── constants.py
│   │   └── helpers.py
│   ├── visualization/
│   │   └── plotter.py
│   └── main.py
├── tests/
├── docs/
└── output/
```

## Author
- Ridho Edistyo
- Email: ridho.ramadhan@pertamina.com

## License and Usage Rights

© 2024 Pertamina. All rights reserved.

This project was developed as part of work at PT Pertamina (Persero). All rights are reserved, and usage, modification, or distribution requires explicit permission from Pertamina and the author.

For inquiries about usage or collaboration, please contact:
- Author: Ridho Edistyo
- Email: ridho.ramadhan@pertamina.com
- Organization: PT Pertamina (Persero)

**Note**: This is proprietary software and is not open source. Any use without proper authorization is prohibited.
