import numpy as np
from utils.constants import (
    INLET_DIAMETER,
    GRID_DIAMETER,
    CHAMBER_HEIGHT,
    GRID_HOLES,
    GRID_POSITIONS,
    INLET_TEMP,
    PRESSURE,
    INLET_VELOCITY,
    GRID_1_PLUGGING,
    HOLE_DIAMETER,
    PATTERN_RADIUS
)
from utils.helpers import (
    calculate_fluid_density,
    calculate_fluid_viscosity,
    calculate_discharge_coefficient,
    generate_radial_pattern
)

class FCCChamber:
    def __init__(self):
        # Chamber geometry (mm)
        self.inlet_diameter = INLET_DIAMETER
        self.grid_diameter = GRID_DIAMETER
        self.chamber_height = CHAMBER_HEIGHT
        self.grid_holes = GRID_HOLES
        self.grid_positions = GRID_POSITIONS
        self.hole_diameter = HOLE_DIAMETER
        self.pattern_radius = PATTERN_RADIUS

        # Operating conditions
        self.inlet_temp = INLET_TEMP
        self.pressure = PRESSURE
        self.inlet_velocity = INLET_VELOCITY

        # Calculate fluid properties
        self.fluid_density = calculate_fluid_density(self.pressure, self.inlet_temp)
        self.fluid_viscosity = calculate_fluid_viscosity(self.inlet_temp)

        # Turbulence parameters
        self.k_epsilon = 0.01
        self.turbulent_intensity = 0.1
        
        # Initialize grid state
        self.grid_states = self.initialize_grid_states()

    def initialize_grid_states(self):
        """Initialize the state of each grid including plugged holes"""
        grid_states = []
        for grid_idx, num_holes in enumerate(self.grid_holes):
            if grid_idx == 0:  # First grid
                # Use actual plugging data
                state = {
                    'total_holes': GRID_1_PLUGGING['total_holes'],
                    'open_holes': GRID_1_PLUGGING['open_holes'],
                    'plugged_refractory': GRID_1_PLUGGING['plugged_refractory'],
                    'plugged_deposit': GRID_1_PLUGGING['plugged_deposit'],
                    'hole_positions': self.get_grid_coordinates(grid_idx)
                }
            else:
                # Assume other grids are less plugged (example values)
                plugged_fraction = 0.2  # 20% plugging for other grids
                state = {
                    'total_holes': num_holes,
                    'open_holes': int(num_holes * (1 - plugged_fraction)),
                    'plugged_refractory': int(num_holes * 0.05),
                    'plugged_deposit': int(num_holes * 0.15),
                    'hole_positions': self.get_grid_coordinates(grid_idx)
                }
            grid_states.append(state)
        return grid_states

    def get_grid_coordinates(self, grid_idx):
        """Get coordinates of holes for a specific grid"""
        num_holes = self.grid_holes[grid_idx]
        coordinates = generate_radial_pattern(num_holes, self.pattern_radius)
        
        # Convert to list of tuples and add z-coordinate
        z_pos = self.grid_positions[grid_idx] * self.chamber_height
        return [(x, y, z_pos) for x, y in coordinates]

    def calculate_grid_flow_areas(self):
        """Calculate flow areas for each grid considering plugging"""
        hole_areas = []
        for state in self.grid_states:
            # Only consider open holes for flow area
            single_hole_area = np.pi * (self.hole_diameter / 2000) ** 2  # Convert to m²
            total_area = state['open_holes'] * single_hole_area
            hole_areas.append(total_area)
        return hole_areas

    def calculate_pressure_drop(self):
        """Calculate pressure drop across grids"""
        areas = self.calculate_grid_flow_areas()
        pressure_drops = []

        inlet_area = np.pi * (self.inlet_diameter / 2000) ** 2  # Convert to m²
        for area in areas:
            # Calculate velocity through open holes
            velocity = self.inlet_velocity * inlet_area / area
            
            # Calculate Reynolds number
            Re = (
                self.fluid_density
                * velocity
                * (self.hole_diameter / 1000)  # Use hole diameter for Re
                / self.fluid_viscosity
            )
            
            # Get discharge coefficient
            cd = calculate_discharge_coefficient(Re)
            
            # Calculate pressure drop
            dp = 0.5 * self.fluid_density * (velocity**2) * (1 - cd**2)
            pressure_drops.append(dp)

        return pressure_drops

    def get_plugging_statistics(self):
        """Get statistics about grid plugging"""
        stats = []
        for idx, state in enumerate(self.grid_states):
            total = state['total_holes']
            stats.append({
                'grid_number': idx + 1,
                'total_holes': total,
                'open_fraction': state['open_holes'] / total,
                'refractory_plugging': state['plugged_refractory'] / total,
                'deposit_plugging': state['plugged_deposit'] / total,
                'total_plugging': 1 - state['open_holes'] / total
            })
        return stats

    def check_hole_status(self, position):
        """Check if a given position corresponds to a plugged hole"""
        for grid_idx, state in enumerate(self.grid_states):
            for idx, hole_pos in enumerate(state['hole_positions']):
                # Check if position is near this hole
                distance = np.sqrt(sum((p1 - p2)**2 for p1, p2 in zip(position, hole_pos)))
                if distance < self.hole_diameter/1000:  # Convert mm to m for comparison
                    # Determine if hole is plugged
                    total_open = state['open_holes']
                    if idx >= total_open:
                        return True, grid_idx
        return False, None
