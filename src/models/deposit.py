import numpy as np
from dataclasses import dataclass
from typing import List, Tuple
import logging  # Add this import
from src.utils.constants import DEPOSIT_PROPERTIES, GRID_1_PLUGGING

logger = logging.getLogger(__name__)

@dataclass
class DepositPoint:
    position: Tuple[float, float, float]
    thickness: float
    strength: float
    removed: bool = False

class DepositModel:
    def __init__(self, chamber):
        logger.debug("Initializing DepositModel")
        self.chamber = chamber
        self.deposits: List[DepositPoint] = []
        self.initialize_deposits()
        
    def initialize_deposits(self):
        """Initialize deposit distribution based on inspection data"""
        logger.debug("Starting deposit initialization")
        # Generate deposits around plugged holes
        for grid_idx, grid_state in enumerate(self.chamber.grid_states):
            if grid_idx == 0:  # First grid
                hole_positions = grid_state['hole_positions']
                num_plugged = grid_state['plugged_deposit']
                logger.debug(f"Initializing {num_plugged} deposits for grid {grid_idx}")
                
                # Select random holes for plugging based on actual data
                plugged_indices = np.random.choice(
                    len(hole_positions), 
                    size=num_plugged, 
                    replace=False
                )
                
                for idx in plugged_indices:
                    x, y, z = hole_positions[idx]
                    self.add_deposit_cluster(x, y, z)

        logger.info(f"Deposit initialization complete. Total deposits: {len(self.deposits)}")
    
    def add_deposit_cluster(self, x: float, y: float, z: float):
        """Add a cluster of deposit points around a location"""
        num_points = np.random.randint(5, 15)
        radius = 0.025  # 25mm cluster radius
        
        for _ in range(num_points):
            # Random position within cluster
            dx = np.random.normal(0, radius/3)
            dy = np.random.normal(0, radius/3)
            dz = np.random.normal(0, radius/3)
            
            # Random thickness and strength based on fouling analysis
            thickness = np.random.uniform(*DEPOSIT_PROPERTIES['thickness_range'])
            
            # Adjust strength based on composition
            base_strength = DEPOSIT_PROPERTIES['adhesion_strength']
            strength_variation = base_strength * 0.1  # 10% variation
            
            # Higher strength where there's more silica content
            silica_factor = 1.0 + DEPOSIT_PROPERTIES['silica_content']
            strength = np.random.normal(
                base_strength * silica_factor,
                strength_variation
            )
            
            self.deposits.append(DepositPoint(
                position=(x + dx, y + dy, z + dz),
                thickness=thickness,
                strength=strength
            ))
    
    def check_impact(self, particle_position: Tuple[float, float, float], 
                    particle_velocity: Tuple[float, float, float],
                    particle_mass: float) -> bool:
        """Check if particle impact removes deposit"""
        # Calculate impact energy
        impact_energy = 0.5 * particle_mass * sum(v**2 for v in particle_velocity)
        impact_radius = 0.015  # 15mm impact effect radius
        
        deposits_removed = False
        for deposit in self.deposits:
            if deposit.removed:
                continue
                
            # Calculate distance to deposit
            dist = np.sqrt(sum((p1 - p2)**2 for p1, p2 in 
                             zip(particle_position, deposit.position)))
            
            if dist < impact_radius:
                # Impact energy decreases with distance
                local_energy = impact_energy * (1 - dist/impact_radius)
                
                # Consider deposit properties in removal calculation
                # Higher moisture content makes removal easier
                moisture_factor = 1.0 + DEPOSIT_PROPERTIES['moisture']
                
                # Thicker deposits are harder to remove
                thickness_factor = deposit.thickness / DEPOSIT_PROPERTIES['thickness_range'][0]
                
                removal_threshold = deposit.strength * thickness_factor / moisture_factor
                
                if local_energy > removal_threshold:
                    deposit.removed = True
                    deposits_removed = True
        
        return deposits_removed
    
    def get_deposit_stats(self):
        """Get statistics about deposit removal"""
        total_deposits = len(self.deposits)
        removed_deposits = sum(1 for d in self.deposits if d.removed)
        
        return {
            'total_deposits': total_deposits,
            'removed_deposits': removed_deposits,
            'removal_percentage': (removed_deposits / total_deposits * 100 
                                 if total_deposits > 0 else 0)
        }
