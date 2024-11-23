"""Helper functions for the FCC simulation."""
import numpy as np
from typing import List, Tuple
from .constants import (
    GAS_CONSTANT,
    REFERENCE_VISCOSITY,
    SUTHERLAND_TEMP,
    MIN_HOLES_PER_RING,
    PATTERN_SPACING
)

def calculate_fluid_density(pressure: float, temperature: float) -> float:
    """
    Calculate fluid density using ideal gas law.
    
    Args:
        pressure (float): Pressure in Pa
        temperature (float): Temperature in K
        
    Returns:
        float: Density in kg/m³
    """
    return pressure / (GAS_CONSTANT * temperature)

def calculate_fluid_viscosity(temperature: float) -> float:
    """
    Calculate fluid viscosity using Sutherland's law.
    
    Args:
        temperature (float): Temperature in K
        
    Returns:
        float: Dynamic viscosity in Pa·s
    """
    return REFERENCE_VISCOSITY * temperature**1.5 / (temperature + SUTHERLAND_TEMP)

def calculate_reynolds_number(velocity: float, diameter: float, density: float, viscosity: float) -> float:
    """
    Calculate Reynolds number for flow.
    
    Args:
        velocity (float): Flow velocity in m/s
        diameter (float): Characteristic diameter in m
        density (float): Fluid density in kg/m³
        viscosity (float): Fluid dynamic viscosity in Pa·s
        
    Returns:
        float: Reynolds number
    """
    return density * velocity * diameter / viscosity

def generate_radial_pattern(num_holes: int, radius: float) -> List[Tuple[float, float]]:
    """
    Generate hole coordinates in a radial pattern.
    
    Args:
        num_holes (int): Total number of holes
        radius (float): Maximum radius for pattern
        
    Returns:
        List[Tuple[float, float]]: List of (x, y) coordinates
    """
    coordinates = []
    num_rings = int(np.sqrt(num_holes))
    remaining_holes = num_holes
    
    for ring in range(num_rings):
        current_radius = radius * (ring + 1) / num_rings
        circumference = 2 * np.pi * current_radius
        
        # Calculate holes in this ring
        holes_in_ring = min(
            max(MIN_HOLES_PER_RING * (ring + 1), 
                int(circumference / (radius / num_rings) / PATTERN_SPACING)),
            remaining_holes
        )
        
        if holes_in_ring <= 0:
            break
            
        angular_step = 2 * np.pi / holes_in_ring
        for i in range(holes_in_ring):
            angle = i * angular_step
            x = current_radius * np.cos(angle)
            y = current_radius * np.sin(angle)
            coordinates.append((x, y))
            remaining_holes -= 1
            
    return coordinates

def calculate_discharge_coefficient(reynolds_number: float) -> float:
    """
    Calculate orifice discharge coefficient based on Reynolds number.
    
    Args:
        reynolds_number (float): Reynolds number of the flow
        
    Returns:
        float: Discharge coefficient
    """
    if reynolds_number < 2000:
        return 0.5
    elif reynolds_number > 20000:
        return 0.61
    else:
        return 0.5 + (reynolds_number - 2000) * (0.11 / 18000)
