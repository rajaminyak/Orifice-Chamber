import numpy as np
from scipy.integrate import odeint
import logging
from src.utils.constants import (
    WALNUT_PROPERTIES,
    GRAVITY,
    SIMULATION_TIME
)
from src.models.deposit import DepositModel

logger = logging.getLogger(__name__)

class ParticleTracker:
    def __init__(self, chamber):
        logger.debug("Initializing ParticleTracker")
        self.chamber = chamber
        self.deposit_model = DepositModel(chamber)
        
        # Particle properties
        self.current_media = WALNUT_PROPERTIES
        self.update_particle_properties(self.current_media)
        
        # Track impacts and effectiveness
        self.impacts = []
        self.impact_times = []
        self.impact_energies = []
        self.removal_effectiveness = []
        
        # Track complete trajectory
        self.current_trajectory = None
        
    def update_particle_properties(self, media_properties):
        """Update particle properties based on cleaning media"""
        self.particle_density = media_properties['density']
        self.particle_diameter = media_properties['diameter']
        self.particle_mass = (np.pi * self.particle_diameter**3 * 
                            self.particle_density / 6)
        self.restitution_coeff = media_properties.get('restitution', 0.7)
        
    def generate_initial_conditions(self, targeting_strategy='spiral'):
        """Generate initial conditions to target deposits"""
        # Always start from top
        z = self.chamber.chamber_height / 1000  # Convert to meters
        
        if targeting_strategy == 'spiral':
            # Start from top with smaller radius for better targeting
            radius = self.chamber.grid_diameter / 16000  # Use 1/16 of grid diameter
            angle = np.random.uniform(0, 2*np.pi)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            
             # Target first grid height
            grid_1_z = self.chamber.grid_positions[0] * self.chamber.chamber_height / 1000
        
            # Calculate drop time considering gravity
            drop_height = z - grid_1_z
            time_to_target = np.sqrt(2 * drop_height / abs(GRAVITY))
        
            # Set velocities for targeting
            vz = -np.sqrt(2 * GRAVITY * drop_height)  # Initial velocity to reach target
            vx = self.chamber.inlet_velocity * 0.2 * np.cos(angle)
            vy = self.chamber.inlet_velocity * 0.2 * np.sin(angle)
        
            logger.debug(f"Starting from top: ({x:.2f}, {y:.2f}, {z:.2f})")
            logger.debug(f"Initial velocities: ({vx:.2f}, {vy:.2f}, {vz:.2f})")
        
            return [x, y, z], [vx, vy, vz]
    
        return self.generate_random_initial_conditions()
    
    def generate_random_initial_conditions(self):
        """Generate random initial conditions from top"""
        # Always start from top
        x = np.random.uniform(-self.chamber.grid_diameter/8000, self.chamber.grid_diameter/8000)
        y = np.random.uniform(-self.chamber.grid_diameter/8000, self.chamber.grid_diameter/8000)
        z = self.chamber.chamber_height / 1000
        
        # Strong downward velocity with some spread
        vx = np.random.normal(0, self.chamber.inlet_velocity * 0.3)
        vy = np.random.normal(0, self.chamber.inlet_velocity * 0.3)
        vz = -self.chamber.inlet_velocity * 3.0  # Increased downward velocity
        
        return [x, y, z], [vx, vy, vz]

    def particle_motion(self, state, t):
        """Enhanced particle motion with grid impact and deposit removal"""
        x, y, z, vx, vy, vz = state
        
        # Get first grid height
        grid_1_height = self.chamber.grid_positions[0] * self.chamber.chamber_height/1000
        
        # Check if particle has reached first grid
        if z > grid_1_height and vz < 0:  # Approaching grid from above
            # Calculate relative velocity and energy
            v_rel = np.sqrt(vx**2 + vy**2 + vz**2)
            impact_energy = 0.5 * self.particle_mass * v_rel**2
            
            # Check for deposit impacts
            position = (x, y, z)
            velocity = (vx, vy, vz)
            impact = self.check_deposit_impact(position, velocity, t)
            
            if impact:
                logger.debug(f"Impact with deposit at t={t}, energy={impact_energy}")
                # Bounce back with energy loss
                vz = -vz * self.restitution_coeff
                vx *= 0.8  # Reduce horizontal motion
                vy *= 0.8
                # Record impact
                self.impacts.append(position)
                self.impact_times.append(t)
                self.impact_energies.append(impact_energy)
        
        # Regular motion equations when not impacting
        v_rel = np.sqrt((vx)**2 + (vy)**2 + (vz - self.chamber.inlet_velocity)**2)
        Re_p = (self.chamber.fluid_density * v_rel * 
                self.particle_diameter / self.chamber.fluid_viscosity)
        
        if Re_p < 0.1:
            Cd = 24 / Re_p
        elif Re_p < 1000:
            Cd = 24 / Re_p * (1 + 0.15 * Re_p**0.687)
        else:
            Cd = 0.44
        
        # Drag force
        Fd_coeff = (3 * self.chamber.fluid_density * Cd * v_rel / 
                    (4 * self.particle_density * self.particle_diameter))
        
        # Motion equations
        dx_dt = vx
        dy_dt = vy
        dz_dt = vz
        dvx_dt = -Fd_coeff * vx
        dvy_dt = -Fd_coeff * vy
        dvz_dt = GRAVITY - Fd_coeff * (vz - self.chamber.inlet_velocity)
        
        # Stop vertical motion at grid
        if abs(z - grid_1_height) < 0.01 and vz < 0:
            dz_dt = 0
            dvz_dt = 0
        
        return [dx_dt, dy_dt, dz_dt, dvx_dt, dvy_dt, dvz_dt]

    def check_deposit_impact(self, position, velocity, t):
        """Check and record deposit impacts with visualization data"""
        impact = self.deposit_model.check_impact(
            position, velocity, self.particle_mass)
        
        if impact:
            logger.debug(f"Deposit impact at time {t}")
            self.impacts.append(position)
            self.impact_times.append(t)
            impact_energy = 0.5 * self.particle_mass * sum(v**2 for v in velocity)
            self.impact_energies.append(impact_energy)
            self.removal_effectiveness.append(True)
            return True, [0, 0, 1]
        
        return False, [0, 0, 0]

    def simulate_trajectory(self, initial_position, initial_velocity, time_span):
        """Simulate particle trajectory with visualization data"""
        logger.info(f"Starting trajectory simulation from top: {initial_position}")
        initial_state = [*initial_position, *initial_velocity]
        t = np.linspace(0, time_span, 1000)
        
        try:
            solution = odeint(
                self.particle_motion, 
                initial_state, 
                t, 
                rtol=1e-8, 
                atol=1e-8
            )
            logger.debug("Trajectory calculation completed")
            
            # Store complete trajectory for visualization
            self.current_trajectory = solution
            
            return t, solution
            
        except Exception as e:
            logger.error(f"Error in trajectory calculation: {str(e)}")
            raise
    def simulate_multiple_particles(self, num_particles, targeting_strategy='spiral'):
        """Simulate multiple particles with different initial conditions"""
        logger.info(f"Simulating {num_particles} particles with {targeting_strategy} strategy")
        all_trajectories = []
        
        for i in range(num_particles):
            # Generate different initial conditions for each particle
            initial_position, initial_velocity = self.generate_initial_conditions(targeting_strategy)
            
            logger.debug(f"Particle {i+1}: Start pos={initial_position}, vel={initial_velocity}")
            
            # Simulate trajectory
            t, trajectory = self.simulate_trajectory(initial_position, initial_velocity, SIMULATION_TIME)
            all_trajectories.append((t, trajectory))
            
            logger.debug(f"Particle {i+1} simulation completed")
        
        return all_trajectories
    
    def get_cleaning_effectiveness(self):
        """Calculate cleaning effectiveness metrics"""
        total_impacts = len(self.impacts)
        if total_impacts == 0:
            return {
                'total_impacts': 0,
                'average_impact_energy': 0,
                'removal_efficiency': 0,
                'impact_locations': [],
                'impact_energies': [],
                'trajectory': self.current_trajectory  # Added for visualization
            }
            
        total_energy = sum(self.impact_energies)
        deposits_removed = sum(1 for e in self.removal_effectiveness if e)
        
        return {
            'total_impacts': total_impacts,
            'average_impact_energy': total_energy/total_impacts,
            'removal_efficiency': deposits_removed/total_impacts,
            'impact_locations': self.impacts,
            'impact_energies': self.impact_energies,
            'trajectory': self.current_trajectory  # Added for visualization
        }
