"""
Test script for the CLIP evaluation visualizer
"""

import numpy as np
import os

def create_sample_data():
    """Create sample similarity data for testing the visualizer."""
    # Create sample similarity matrix (5 generated images x 3 IKEA images)
    similarity_matrix = np.random.rand(5, 3) * 0.5 + 0.3  # Values between 0.3 and 0.8
    
    # Create sample image paths
    generated_paths = [
        "../generated_images/design_1.png",
        "../generated_images/design_2.png",
        "../generated_images/design_3.png",
        "../generated_images/design_4.png",
        "../generated_images/design_5.png"
    ]
    
    ikea_paths = [
        "../ikea_dataset/ikea_sofa_1.jpg",
        "../ikea_dataset/ikea_table_1.jpg",
        "../ikea_dataset/ikea_chair_1.jpg"
    ]
    
    # Save sample data
    np.save("../similarity_results_matrix.npy", similarity_matrix)
    
    with open("../similarity_results_generated_paths.txt", "w") as f:
        f.write("\n".join(generated_paths))
        
    with open("../similarity_results_ikea_paths.txt", "w") as f:
        f.write("\n".join(ikea_paths))
    
    print("Sample data created successfully!")

def test_visualizer():
    """Test the visualizer with sample data."""
    try:
        # Check if sample data exists
        if not os.path.exists("../similarity_results_matrix.npy"):
            print("Creating sample data...")
            create_sample_data()
        
        # Run the visualizer
        import subprocess
        result = subprocess.run([
            "python", "clip_eval_visualizer.py",
            "--results_path", "../similarity_results",
            "--output_dir", "../clip_eval_results",
            "--top_k", "5"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Visualizer test completed successfully!")
            print("Results saved to ../clip_eval_results/")
        else:
            print("Error running visualizer:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error testing visualizer: {e}")

if __name__ == "__main__":
    test_visualizer()