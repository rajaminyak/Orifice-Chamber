"""Constants used throughout the FCC simulation."""
from dataclasses import dataclass
from typing import List, Tuple

# Chamber geometry constants (all dimensions in mm unless specified)
INLET_DIAMETER = 2558
GRID_DIAMETER = 3800
CHAMBER_HEIGHT = 12000

# Grid configuration
GRID_POSITIONS = [0.8, 0.6, 0.4, 0.2]  # Relative positions from top
GRID_HOLES = [285, 300, 315, 330]  # Number of holes per grid
HOLE_DIAMETER = 50.0  # mm
PATTERN_RADIUS = 1900  # mm

# Grid hole pattern parameters
MIN_HOLES_PER_RING = 8
PATTERN_SPACING = 1.5  # Relative spacing between holes

# Operating conditions
INLET_TEMP = 715 + 273.15  # K
PRESSURE = 1.52 * 98066.5  # Pa (converted from kg/cm²)
INLET_VELOCITY = 17.45  # m/s (average of 17.2-17.7 range)

# Fluid properties
GAS_CONSTANT = 287.05  # J/(kg·K)
REFERENCE_VISCOSITY = 1.458e-6  # Pa·s
SUTHERLAND_TEMP = 110.4  # K

# Walnut Shell Properties
WALNUT_PROPERTIES = {
    'density': 640.7,  # kg/m³ (converted from 40-50 lbs/ft³)
    'diameter': 0.005,  # m (typical size)
    'mohs_hardness': 4.75,  # Average from 4.5-5 range
    'moisture_content': 0.06,  # 6% average from 3-9% range
    'batch_mass': 40  # kg (from injection procedure)
}

# Deposit Properties (from fouling analysis)
DEPOSIT_PROPERTIES = {
    'moisture': 0.0085,  # 0.85%-wt
    'ash_content': 0.9826,  # 98.26%-wt
    'silica_content': 0.7591,  # 75.91%-wt
    'adhesion_strength': 150000,  # Pa (estimated based on composition)
    'thickness_range': (0.001, 0.005)  # m (estimated from images)
}

# Grid Plugging State (from inspection data)
GRID_1_PLUGGING = {
    'total_holes': 285,
    'plugged_refractory': 22,  # 8.8%
    'plugged_deposit': 133,    # 53.2%
    'open_holes': 130
}

# Simulation parameters
TIME_STEP = 0.001  # s
MAX_SIMULATION_TIME = 10.0  # s
GRAVITY = -9.81  # m/s²

# Initial conditions for particle simulation
INITIAL_POSITION = [0, 0, CHAMBER_HEIGHT]  # [x, y, z] in mm
INITIAL_VELOCITY = [1, 1, -5]  # [vx, vy, vz] in m/s
SIMULATION_TIME = 10  # seconds

# Visualization parameters
FIGURE_SIZE = (12, 8)
DPI = 100
GRID_COLOR = '#1f77b4'
PARTICLE_COLOR = '#d62728'
DEPOSIT_COLOR = '#8B4513'  # Brown for deposits
IMPACT_COLOR = '#FF4500'   # OrangeRed for impacts
CHAMBER_ALPHA = 0.1

@dataclass
class GridProperties:
    """Properties for each grid in the chamber."""
    position: float
    num_holes: int
    hole_diameter: float
    pattern_radius: float

# Define standard grid configurations
GRID_CONFIGS: List[GridProperties] = [
    GridProperties(pos, holes, HOLE_DIAMETER, PATTERN_RADIUS)
    for pos, holes in zip(GRID_POSITIONS, GRID_HOLES)
]

SIMULATION_TIME = 15.0  # simulation duration in seconds

#Cleaning Media Properties
CLEANING_MEDIA = {
    'walnut_shell': {
        'name': 'Walnut Shell',
        'density': 640.7,     # kg/m³
        'diameter': 0.005,    # m
        'restitution': 0.5,   # coefficient
        'hardness': 4.75,     # Mohs scale
        'cost_per_kg': 2.5,   # USD/kg
        'color': '#8B4513'    # for visualization
    },
    'ceramic_ball': {
        'name': 'Ceramic Ball',
        'density': 2500,      # kg/m³
        'diameter': 0.01,     # m
        'restitution': 0.7,
        'hardness': 9.0,
        'cost_per_kg': 5.0,
        'color': '#1E90FF'
    },
    'steel_shot': {
        'name': 'Steel Shot',
        'density': 7800,      # kg/m³
        'diameter': 0.008,    # m
        'restitution': 0.8,
        'hardness': 7.5,
        'cost_per_kg': 3.5,
        'color': '#808080'
    }
}

# Time Evolution Parameters
TIME_PARAMS = {
    'simulation_days': 30,
    'deposit_growth_rate': 0.1,  # mm/day
    'cleaning_interval': 7,      # days
    'operation_hours': 24        # hours/day
}

# Optimization Parameters
OPTIMIZATION_PARAMS = {
    'particle_size_range': (0.001, 0.02),     # m
    'velocity_range': (10, 30),               # m/s
    'angle_range': (0, 90),                   # degrees
    'density_range': (500, 8000),             # kg/m³
    'batch_size_range': (20, 100),            # kg
    'iterations': 100                         # optimization iterations
}

# Analysis Parameters
ANALYSIS_PARAMS = {
    'grid_resolution': 50,          # for heatmaps
    'impact_threshold': 100,        # J
    'removal_threshold': 0.8,       # efficiency threshold
    'coverage_threshold': 0.9       # minimum coverage
}
