import numpy as np
from src.utils.constants import GAS_CONSTANT
from src.utils.helpers import (
    calculate_fluid_density,
    calculate_fluid_viscosity,
    calculate_reynolds_number,
)


class FluidProperties:
    def __init__(self, temperature, pressure):
        self.temperature = temperature
        self.pressure = pressure
        self.update_properties()

    def update_properties(self):
        """Update fluid properties based on current conditions"""
        self.density = calculate_fluid_density(self.pressure, self.temperature)
        self.viscosity = calculate_fluid_viscosity(self.temperature)

    def calculate_flow_properties(self, velocity, characteristic_length):
        """Calculate flow properties for given conditions"""
        reynolds = calculate_reynolds_number(
            velocity, characteristic_length, self.density, self.viscosity
        )

        return {
            "reynolds_number": reynolds,
            "density": self.density,
            "viscosity": self.viscosity,
        }
