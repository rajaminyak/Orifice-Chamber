import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches
from src.utils.constants import (
    FIGURE_SIZE,
    DPI,
    GRID_COLOR,
    PARTICLE_COLOR,
    DEPOSIT_COLOR,
    IMPACT_COLOR,
    CHAMBER_ALPHA,
)


class Visualizer:
    def __init__(self, chamber, particle_tracker):
        self.chamber = chamber
        self.particle_tracker = particle_tracker
        
        # Create custom colormaps for deposits and impacts
        self.deposit_cmap = LinearSegmentedColormap.from_list('deposit', 
            ['lightcoral', 'darkred'])
        self.impact_cmap = LinearSegmentedColormap.from_list('impact',
            ['yellow', 'orange', 'red'])

    def plot_chamber_and_trajectory(self, trajectory_data):
        """Create static 3D visualization of chamber and trajectory"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Get dimensions
        r = self.chamber.grid_diameter / 2000  # Convert to meters
        h = self.chamber.chamber_height / 1000
        grid_1_height = self.chamber.grid_positions[0] * h
        
        # Plot chamber outline
        theta = np.linspace(0, 2*np.pi, 100)
        z = np.linspace(0, h, 100)
        theta, z = np.meshgrid(theta, z)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        ax.plot_surface(x, y, z, alpha=0.1, color='gray')
        
        # Plot grids
        for height in self.chamber.grid_positions:
            z_grid = height * h
            x_grid = r * np.cos(theta[0])
            y_grid = r * np.sin(theta[0])
            ax.plot(x_grid, y_grid, [z_grid]*len(theta[0]), 
                   color='blue', alpha=0.7, linewidth=2)
        
        # Plot deposits
        deposits = self.particle_tracker.deposit_model.deposits
        positions = np.array([d.position for d in deposits if not d.removed]) / 1000
        thicknesses = np.array([d.thickness for d in deposits if not d.removed])
        
        if len(positions) > 0:
            scatter = ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                             c=thicknesses, cmap=self.deposit_cmap,
                             s=100, alpha=0.8, label='Deposits')
            plt.colorbar(scatter, label='Deposit Thickness (m)')
        
        # Plot particle trajectory
        ax.plot(trajectory_data[:, 0], trajectory_data[:, 1], trajectory_data[:, 2],
               color='black', linewidth=2, label='Trajectory')
        
        # Plot start and end points
        ax.scatter(trajectory_data[0, 0], trajectory_data[0, 1], trajectory_data[0, 2],
                  color='green', s=100, label='Start')
        ax.scatter(trajectory_data[-1, 0], trajectory_data[-1, 1], trajectory_data[-1, 2],
                  color='red', s=100, label='End')
        
        # Plot impacts
        if self.particle_tracker.impacts:
            impact_positions = np.array(self.particle_tracker.impacts)
            ax.scatter(impact_positions[:, 0], impact_positions[:, 1], 
                      impact_positions[:, 2], color='yellow', marker='*',
                      s=200, label='Impacts')
        
        # Set labels and limits
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('FCC Chamber with Particle Trajectory and Deposits')
        
        # Set consistent view limits
        ax.set_xlim(-r*1.2, r*1.2)
        ax.set_ylim(-r*1.2, r*1.2)
        ax.set_zlim(0, h)
        
        # Set view angle
        ax.view_init(elev=20, azim=45)
        
        # Add legend
        ax.legend(loc='upper right')
        
        plt.show()
        return fig, ax     

    def animate_trajectory(self, trajectory_data, interval=50):
        """Enhanced animation with better particle-deposit interaction visualization"""
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # Get dimensions
        r = self.chamber.grid_diameter / 2000
        h = self.chamber.chamber_height / 1000
        grid_1_height = self.chamber.grid_positions[0] * h
        
        # Create static elements
        theta = np.linspace(0, 2*np.pi, 100)
        z = np.linspace(0, h, 100)
        theta, z = np.meshgrid(theta, z)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        # Track removed deposits for visualization
        self.removed_deposits = []
        
        def update(frame):
            ax.cla()
            
            # Plot chamber
            ax.plot_surface(x, y, z, alpha=0.1, color='gray')
            
            # Plot grids
            for height in self.chamber.grid_positions:
                z_grid = height * h
                x_grid = r * np.cos(theta[0])
                y_grid = r * np.sin(theta[0])
                ax.plot(x_grid, y_grid, [z_grid]*len(theta[0]), 
                       color='blue', alpha=0.7, linewidth=2)
            
            # Get current particle position
            current_pos = trajectory_data[:frame+1]
            
            # Plot deposits with removal effect
            deposits = self.particle_tracker.deposit_model.deposits
            active_deposits = []
            removed_deposits = []
            
            for d in deposits:
                pos = np.array(d.position) / 1000  # Convert to meters
                if d.removed:
                    removed_deposits.append((pos, d.thickness))
                else:
                    active_deposits.append((pos, d.thickness))
            
            # Plot active deposits
            if active_deposits:
                positions, thicknesses = zip(*active_deposits)
                positions = np.array(positions)
                ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                         c=thicknesses, cmap=self.deposit_cmap,
                         s=100, alpha=0.8, label='Deposits')
            
            # Plot removed deposits with fade-out effect
            if removed_deposits:
                positions, _ = zip(*removed_deposits)
                positions = np.array(positions)
                ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2],
                         color='yellow', s=150, alpha=0.3, marker='*',
                         label='Removed Deposits')
            
            # Plot particle trajectory
            if len(current_pos) > 0:
                # Trajectory line
                ax.plot(current_pos[:, 0], current_pos[:, 1], current_pos[:, 2],
                       color='black', linewidth=2, label='Trajectory')
                
                # Current particle position
                pos = current_pos[-1]
                if pos[2] > grid_1_height:
                    # Particle above grid
                    ax.scatter(pos[0], pos[1], pos[2],
                             color='green', s=150, label='Particle')
                    
                    # Add direction arrow
                    if len(current_pos) > 1:
                        direction = pos - current_pos[-2]
                        ax.quiver(pos[0], pos[1], pos[2],
                                direction[0], direction[1], direction[2],
                                color='black', length=0.1, normalize=True)
                else:
                    # Show impact
                    ax.scatter(pos[0], pos[1], grid_1_height,
                             color='yellow', s=200, marker='*',
                             label='Impact', alpha=0.8)
                    
                    # Add impact waves
                    circle_theta = np.linspace(0, 2*np.pi, 50)
                    wave_r = 0.1 * (frame % 20) / 20
                    circle_x = pos[0] + wave_r * np.cos(circle_theta)
                    circle_y = pos[1] + wave_r * np.sin(circle_theta)
                    ax.plot(circle_x, circle_y, [grid_1_height]*50,
                           color='yellow', alpha=0.3)
            
            # Set labels and limits
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            ax.set_title('FCC Chamber Cleaning Simulation')
            
            # Set consistent view limits
            ax.set_xlim(-r*1.2, r*1.2)
            ax.set_ylim(-r*1.2, r*1.2)
            ax.set_zlim(0, h)
            
            # Rotate view for better perspective
            ax.view_init(elev=20, azim=45 + frame/2)
            
            # Add legend
            ax.legend(loc='upper right')
            
            # Add effectiveness meter
            if len(self.particle_tracker.impacts) > 0:
                removed_count = sum(1 for d in deposits if d.removed)
                total_count = len(deposits)
                effectiveness = removed_count / total_count * 100
                ax.text2D(0.02, 0.98, f'Cleaning Effectiveness: {effectiveness:.1f}%',
                         transform=ax.transAxes, fontsize=10,
                         bbox=dict(facecolor='white', alpha=0.7))
            
            return ax,
        
        anim = animation.FuncAnimation(
            fig, update,
            frames=len(trajectory_data),
            interval=interval,
            blit=False,
            repeat=True
        )
        
        plt.show()
        return fig, ax
        
    def animate_trajectory(self, trajectory_data, interval=50):
        """Create animation with proper initialization and scaling"""
        fig = plt.figure(figsize=FIGURE_SIZE)
        ax = fig.add_subplot(111, projection='3d')
        
        # Get grid height and chamber dimensions
        grid_1_height = self.chamber.grid_positions[0] * self.chamber.chamber_height/1000
        r = self.chamber.grid_diameter / 2000  # Convert to meters
        h = self.chamber.chamber_height / 1000  # Convert to meters
        
        # Create static elements
        theta = np.linspace(0, 2*np.pi, 100)
        z = np.linspace(0, h, 100)
        theta, z = np.meshgrid(theta, z)
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        def init():
            """Initialize the animation"""
            ax.cla()
            # Plot chamber wall
            ax.plot_surface(x, y, z, alpha=0.1, color='gray')
            
            # Plot grids
            for height in self.chamber.grid_positions:
                z_grid = height * h
                x_grid = r * np.cos(theta[0])
                y_grid = r * np.sin(theta[0])
                ax.plot(x_grid, y_grid, [z_grid]*len(theta[0]), 
                    color='blue', alpha=0.5)
            
            # Set initial view and limits
            ax.set_xlim(-r*1.2, r*1.2)
            ax.set_ylim(-r*1.2, r*1.2)
            ax.set_zlim(0, h)
            return ax,
        
        def update(frame):
            """Update animation frame"""
            ax.cla()
            
            # Plot chamber walls
            ax.plot_surface(x, y, z, alpha=0.1, color='gray')
            
            # Plot grids
            for height in self.chamber.grid_positions:
                z_grid = height * h
                x_grid = r * np.cos(theta[0])
                y_grid = r * np.sin(theta[0])
                ax.plot(x_grid, y_grid, [z_grid]*len(theta[0]), 
                    color='blue', alpha=0.5)
            
            # Plot deposits
            deposits = self.particle_tracker.deposit_model.deposits
            positions = np.array([d.position for d in deposits if not d.removed])
            if len(positions) > 0:
                ax.scatter(
                    positions[:, 0]/1000, positions[:, 1]/1000, positions[:, 2]/1000,
                    color='red', s=50, alpha=0.8, label='Deposits'
                )
            
            # Plot current trajectory
            current_pos = trajectory_data[:frame+1]
            if len(current_pos) > 0:
                # Trajectory line
                ax.plot(
                    current_pos[:, 0], current_pos[:, 1], current_pos[:, 2],
                    color='black', linewidth=2, label='Trajectory'
                )
                
                # Current particle position
                current_z = current_pos[-1, 2]
                if current_z > grid_1_height:
                    # Particle above grid
                    ax.scatter(
                        current_pos[-1, 0], current_pos[-1, 1], current_pos[-1, 2],
                        color='green', s=100, label='Particle'
                    )
                else:
                    # Particle at grid - show impact
                    ax.scatter(
                        current_pos[-1, 0], current_pos[-1, 1], grid_1_height,
                        color='yellow', s=150, marker='*', label='Impact'
                    )
            
            # Set labels and limits
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')
            ax.set_zlabel('Z (m)')
            ax.set_title('FCC Chamber Cleaning Simulation')
            
            # Set view limits
            ax.set_xlim(-r*1.2, r*1.2)
            ax.set_ylim(-r*1.2, r*1.2)
            ax.set_zlim(0, h)
            
            # Rotate view
            ax.view_init(elev=20, azim=frame % 360)
            
            # Add legend
            ax.legend()
            
            return ax,
        
        anim = animation.FuncAnimation(
            fig,
            update,
            init_func=init,
            frames=len(trajectory_data),
            interval=interval,
            blit=False,
            repeat=True
        )
        
        plt.show()
        return anim

    def save_animation(self, trajectory_data, filename, fps=20):
        """Save animation to file with progress bar"""
        try:
            from tqdm import tqdm
            print(f"Saving animation to {filename}...")
            
            # Create animation
            anim = self.animate_trajectory(trajectory_data)
            
            # Create writer
            writer = animation.PillowWriter(fps=fps)
            
            # Save animation with progress bar
            with tqdm(total=100, desc="Saving animation") as pbar:
                anim.save(
                    f'output/{filename}',
                    writer=writer,
                    progress_callback=lambda i, n: pbar.update(100/n)
                )
            
            print(f"Animation saved successfully to output/{filename}")
            
        except Exception as e:
            print(f"Error saving animation: {e}")
