"""
Test script for CLIP similarity module
"""

import os
from clip_similarity import CLIPImageSimilarity

def main():
    # Initialize the similarity evaluator
    evaluator = CLIPImageSimilarity()
    
    # Define directories (update these paths to your actual directories)
    generated_images_dir = "../generated_images"  # Default output directory
    ikea_images_dir = "../ikea_dataset"  # You need to create this with IKEA images
    
    # Check if directories exist
    if not os.path.exists(generated_images_dir):
        print(f"Warning: Generated images directory not found: {generated_images_dir}")
        print("Please generate some images first or update the path.")
        return
        
    # Note: We no longer require IKEA directory to exist, we'll just warn if it's missing
    
    try:
        # Compute similarity matrix
        similarity_matrix, generated_paths, ikea_paths = evaluator.compute_similarity_matrix(
            generated_images_dir, ikea_images_dir
        )
        
        # Find most similar pairs (only if we have IKEA images)
        if len(ikea_paths) > 0:
            top_pairs = evaluator.find_most_similar_pairs(
                similarity_matrix, generated_paths, ikea_paths, top_k=5
            )
            
            print("\nTop 5 most similar image pairs:")
            for i, (gen_path, ikea_path, similarity) in enumerate(top_pairs, 1):
                print(f"{i}. Similarity: {similarity:.4f}")
                print(f"   Generated: {os.path.basename(gen_path)}")
                print(f"   IKEA: {os.path.basename(ikea_path)}")
                print()
        else:
            print(f"Warning: No IKEA images found in directory: {ikea_images_dir}")
            print("Skipping similarity comparison.")
        
        # Save results
        evaluator.save_similarity_matrix(
            similarity_matrix, generated_paths, ikea_paths, 
            "../similarity_results"
        )
        
        print("Results saved successfully!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()