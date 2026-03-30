"""
CLIP Embedding and Similarity Evaluation Module

This module provides functionality to compute CLIP embeddings for images and calculate
similarity matrices between two sets of images (e.g., generated interior designs and IKEA products).
"""

from typing import List, Tuple, Optional, Any
import numpy as np
import os

try:
    import torch
    import clip
    from PIL import Image
    from pathlib import Path
    from sklearn.metrics.pairwise import cosine_similarity
    CLIP_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CLIP dependencies not available: {e}")
    CLIP_AVAILABLE = False

class CLIPImageSimilarity:
    """
    A class to compute CLIP embeddings and similarity between image sets.
    """

    def __init__(self, model_name: str = "ViT-B/32", device: Optional[str] = None):
        """
        Initialize the CLIP model.

        Args:
            model_name (str): Name of the CLIP model to use. Default is "ViT-B/32".
            device (str, optional): Device to run the model on. If None, will auto-detect.
        """
        if not CLIP_AVAILABLE:
            raise ImportError("CLIP dependencies not available. Please install requirements.txt")
            
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"Loading CLIP model '{model_name}' on device '{self.device}'...")
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        self.model.eval()
        print("CLIP model loaded successfully.")

    def preprocess_image(self, image_path: str) -> Any:
        """
        Preprocess an image for CLIP model input.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Any: Preprocessed image tensor.
        """
        image = Image.open(image_path).convert("RGB")
        return self.preprocess(image).unsqueeze(0).to(self.device)

    def compute_embedding(self, image_path: str) -> Optional[np.ndarray]:
        """
        Compute CLIP embedding for a single image.

        Args:
            image_path (str): Path to the image file.

        Returns:
            Optional[np.ndarray]: Normalized CLIP embedding vector.
        """
        try:
            image_tensor = self.preprocess_image(image_path)
            with torch.no_grad():
                embedding = self.model.encode_image(image_tensor)
                # Normalize the embedding
                embedding = embedding / embedding.norm(dim=-1, keepdim=True)
                return embedding.cpu().numpy()
        except Exception as e:
            print(f"Error processing image {image_path}: {str(e)}")
            return None

    def compute_embeddings_batch(self, image_paths: List[str]) -> Tuple[np.ndarray, List[str]]:
        """
        Compute CLIP embeddings for a batch of images.

        Args:
            image_paths (List[str]): List of paths to image files.

        Returns:
            Tuple[np.ndarray, List[str]]: Normalized CLIP embeddings matrix and valid paths.
        """
        embeddings: List[np.ndarray] = []
        valid_paths: List[str] = []
        
        print(f"Computing embeddings for {len(image_paths)} images...")
        
        for i, image_path in enumerate(image_paths):
            if not os.path.exists(image_path):
                print(f"Warning: Image file not found: {image_path}")
                continue
                
            try:
                embedding = self.compute_embedding(image_path)
                if embedding is not None:
                    embeddings.append(embedding)
                    valid_paths.append(image_path)
                else:
                    print(f"Warning: Failed to process image: {image_path}")
            except Exception as e:
                print(f"Error processing image {image_path}: {str(e)}")
                
            # Progress indicator
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1}/{len(image_paths)} images...")
        
        if not embeddings:
            raise ValueError("No valid embeddings were computed.")
            
        # Stack embeddings into a matrix
        embeddings_matrix = np.vstack(embeddings)
        print(f"Successfully computed {len(embeddings)} embeddings.")
        return embeddings_matrix, valid_paths

    def load_image_paths(self, directory: str, extensions: Tuple[str, ...] = (".png", ".jpg", ".jpeg")) -> List[str]:
        """
        Load image paths from a directory.

        Args:
            directory (str): Path to the directory containing images.
            extensions (Tuple[str, ...]): Tuple of valid image file extensions.

        Returns:
            List[str]: List of image file paths.
        """
        image_paths: List[str] = []
        path = Path(directory)
        
        if not path.exists():
            print(f"Warning: Directory not found: {directory}")
            return image_paths  # Return empty list instead of raising exception
            
        for ext in extensions:
            # Convert Path objects to strings directly
            image_paths.extend([str(p) for p in path.glob(f"*{ext}")])
            
        print(f"Found {len(image_paths)} images in {directory}")
        return image_paths

    def compute_similarity_matrix(self, generated_images_dir: str, ikea_images_dir: str) -> Tuple[np.ndarray, List[str], List[str]]:
        """
        Compute cosine similarity matrix between generated images and IKEA images.

        Args:
            generated_images_dir (str): Directory containing generated interior design images.
            ikea_images_dir (str): Directory containing IKEA product images.

        Returns:
            Tuple[np.ndarray, List[str], List[str]]: Similarity matrix and corresponding image paths.
        """
        # Load image paths
        generated_paths = self.load_image_paths(generated_images_dir)
        ikea_paths = self.load_image_paths(ikea_images_dir)
        
        if not generated_paths:
            raise ValueError(f"No images found in generated images directory: {generated_images_dir}")
            
        # If no IKEA images found, that's okay - we'll return an empty matrix
        if not ikea_paths:
            print(f"Warning: No images found in IKEA images directory: {ikea_images_dir}")
            # Return empty matrix with proper dimensions
            empty_matrix = np.zeros((len(generated_paths), 0))
            return empty_matrix, generated_paths, ikea_paths
        
        # Compute embeddings
        print("Computing embeddings for generated images...")
        generated_embeddings, valid_generated_paths = self.compute_embeddings_batch(generated_paths)
        
        print("Computing embeddings for IKEA images...")
        ikea_embeddings, valid_ikea_paths = self.compute_embeddings_batch(ikea_paths)
        
        # Compute cosine similarity matrix
        print("Computing cosine similarity matrix...")
        similarity_matrix = cosine_similarity(generated_embeddings, ikea_embeddings)
        
        print(f"Similarity matrix computed with shape: {similarity_matrix.shape}")
        return similarity_matrix, valid_generated_paths, valid_ikea_paths

    def find_most_similar_pairs(self, similarity_matrix: np.ndarray, 
                              generated_paths: List[str], ikea_paths: List[str], 
                              top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        Find the most similar image pairs based on the similarity matrix.

        Args:
            similarity_matrix (np.ndarray): Cosine similarity matrix.
            generated_paths (List[str]): List of generated image paths.
            ikea_paths (List[str]): List of IKEA image paths.
            top_k (int): Number of top similar pairs to return.

        Returns:
            List[Tuple[str, str, float]]: List of (generated_path, ikea_path, similarity_score) tuples.
        """
        # If no IKEA images, return empty list
        if similarity_matrix.shape[1] == 0:
            return []
            
        # Flatten the matrix and get indices of top-k values
        flat_indices = np.argpartition(similarity_matrix.flatten(), -top_k)[-top_k:]
        top_indices = np.unravel_index(flat_indices, similarity_matrix.shape)
        
        # Sort by similarity score (descending)
        similarities = similarity_matrix[top_indices]
        sorted_indices = np.argsort(similarities)[::-1]
        
        # Create result list
        result: List[Tuple[str, str, float]] = []
        for i in sorted_indices:
            gen_idx, ikea_idx = top_indices[0][i], top_indices[1][i]
            similarity = similarity_matrix[gen_idx, ikea_idx]
            result.append((generated_paths[gen_idx], ikea_paths[ikea_idx], float(similarity)))
            
        return result

    def save_similarity_matrix(self, similarity_matrix: np.ndarray, 
                              generated_paths: List[str], ikea_paths: List[str],
                              output_path: str) -> None:
        """
        Save the similarity matrix and corresponding image paths to files.

        Args:
            similarity_matrix (np.ndarray): Cosine similarity matrix.
            generated_paths (List[str]): List of generated image paths.
            ikea_paths (List[str]): List of IKEA image paths.
            output_path (str): Path to save the output files (without extension).
        """
        # Save similarity matrix
        np.save(f"{output_path}_matrix.npy", similarity_matrix)
        
        # Save image paths
        with open(f"{output_path}_generated_paths.txt", "w") as f:
            f.write("\n".join(generated_paths))
            
        with open(f"{output_path}_ikea_paths.txt", "w") as f:
            f.write("\n".join(ikea_paths))
            
        print(f"Similarity matrix and paths saved to {output_path}*")


def main() -> None:
    """
    Main function to demonstrate usage of the CLIPImageSimilarity class.
    """
    if not CLIP_AVAILABLE:
        print("Error: CLIP dependencies not available. Please install requirements.txt")
        return
        
    # Example usage
    try:
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
            print("No IKEA images found. Skipping similarity comparison.")
        
        # Save results
        evaluator.save_similarity_matrix(
            similarity_matrix, generated_paths, ikea_paths, 
            "../similarity_results"
        )
        
    except Exception as e:
        print(f"Error in main execution: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()