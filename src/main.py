import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('simulation.log')
    ]
)

logger = logging.getLogger(__name__)

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

try:
    logger.debug("Attempting imports...")
    from src.models.chamber import FCCChamber
    from src.models.particle import ParticleTracker
    from src.visualization.plotter import Visualizer
    from src.utils.constants import (
        SIMULATION_TIME,
        WALNUT_PROPERTIES,
        CLEANING_MEDIA,  # Add this
        TIME_PARAMS,     # Add this
    )
    # Add new analysis imports
    from src.analysis.analyzer import (
        DepositAnalyzer,
        TimeEvolutionAnalyzer,
        OptimizationEngine,
        TechnicalReportGenerator
    )
    from src.visualization.advanced_plotter import AdvancedVisualizer
    logger.debug("Imports successful")
except ImportError as e:
    logger.debug(f"First import attempt failed: {e}")
    try:
        # Fallback imports if needed
        from models.chamber import FCCChamber
        from models.particle import ParticleTracker
        from visualization.plotter import Visualizer
        from utils.constants import (
            SIMULATION_TIME,
            WALNUT_PROPERTIES,
            CLEANING_MEDIA,
            TIME_PARAMS
        )
        from analysis.analyzer import (
            DepositAnalyzer,
            TimeEvolutionAnalyzer,
            OptimizationEngine,
            TechnicalReportGenerator
        )
        from visualization.advanced_plotter import AdvancedVisualizer
        logger.debug("Alternative imports successful")
    except ImportError as e:
        logger.error(f"All import attempts failed: {e}")
        raise

def run_single_particle_simulation(chamber, particle_tracker, visualizer, save_animation=True):
    """Run simulation for a single particle"""
    # Generate initial conditions with targeting
    initial_position, initial_velocity = particle_tracker.generate_initial_conditions('spiral')
    
    logger.info(f"Starting simulation with initial position: {initial_position}")
    t, trajectory = particle_tracker.simulate_trajectory(initial_position, initial_velocity, SIMULATION_TIME)
    
    # Plot static visualization
    visualizer.plot_chamber_and_trajectory(trajectory)
    
    # Save animation if requested
    if save_animation:
        logger.info("Saving animation...")
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        visualizer.save_animation(trajectory, "simulation.gif")
        logger.info("Animation saved to output/simulation.gif")
    
    # Print pressure drops
    pressure_drops = chamber.calculate_pressure_drop()
    print("\nPressure drops across grids (Pa):")
    for i, dp in enumerate(pressure_drops):
        print(f"Grid {i+1}: {dp:.2f}")
    
    return t, trajectory

def run_comprehensive_analysis(chamber, particle_tracker, visualizer):  # Add visualizer parameter
    """Run comprehensive analysis with all features"""
    # Initialize analyzers
    deposit_analyzer = DepositAnalyzer(chamber, particle_tracker)
    time_analyzer = TimeEvolutionAnalyzer()
    optimizer = OptimizationEngine()
    advanced_viz = AdvancedVisualizer()
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Run analyses
    cleaning_results = {}
    for media_name, media_props in CLEANING_MEDIA.items():
        logger.info(f"\nTesting {media_name}...")
        # Update particle properties
        particle_tracker.update_particle_properties(media_props)
        
        # Run simulation
        t, trajectory = run_single_particle_simulation(
            chamber, particle_tracker, visualizer, save_animation=False)
        
        # Store results
        cleaning_results[media_name] = deposit_analyzer.analyze_removal_patterns()
    
    # Generate visualizations
    logger.info("Generating comparison visualizations...")
    advanced_viz.plot_cleaning_media_comparison(cleaning_results)
    
    # Generate time evolution
    logger.info("Generating time evolution analysis...")
    time_data = time_analyzer.simulate_time_evolution(TIME_PARAMS['simulation_days'])
    advanced_viz.plot_time_evolution(time_data)
    
    # Generate technical report
    logger.info("Generating technical report...")
    report_gen = TechnicalReportGenerator(
        chamber, particle_tracker, deposit_analyzer, 
        time_analyzer, optimizer)
    report_gen.save_report()
    
    logger.info("Analysis complete. Check output folder for reports and visualizations.")

def main():
    """Main function to run the FCC simulation"""
    try:
        # Initialize components
        chamber = FCCChamber()
        particle_tracker = ParticleTracker(chamber)
        visualizer = Visualizer(chamber, particle_tracker)
        
        if len(sys.argv) > 1 and sys.argv[1] == '--comprehensive':
            run_comprehensive_analysis(chamber, particle_tracker, visualizer)
        else:
            t, trajectory = run_single_particle_simulation(
                chamber, particle_tracker, visualizer)
        
        return 0
    except Exception as e:
        logger.error(f"Error during simulation: {str(e)}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
