"""
CLIP Evaluation Results Visualizer

This script loads CLIP similarity results and generates visualizations including:
- Heatmap of similarity matrix
- Bar charts of top similar pairs
- Scatter plots of similarity distributions
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
from typing import List, Tuple, Dict, Any
import argparse

def load_similarity_data(results_path: str) -> Tuple[np.ndarray, List[str], List[str]]:
    """
    Load similarity matrix and image paths from saved files.
    
    Args:
        results_path (str): Path to the results files (without extension)
        
    Returns:
        Tuple[np.ndarray, List[str], List[str]]: Similarity matrix and image paths
    """
    # Load similarity matrix
    matrix_path = f"{results_path}_matrix.npy"
    generated_paths_path = f"{results_path}_generated_paths.txt"
    ikea_paths_path = f"{results_path}_ikea_paths.txt"
    
    if not os.path.exists(matrix_path):
        raise FileNotFoundError(f"Similarity matrix not found: {matrix_path}")
        
    similarity_matrix = np.load(matrix_path)
    
    # Load image paths
    with open(generated_paths_path, 'r') as f:
        generated_paths = [line.strip() for line in f.readlines()]
        
    with open(ikea_paths_path, 'r') as f:
        ikea_paths = [line.strip() for line in f.readlines()]
        
    return similarity_matrix, generated_paths, ikea_paths

def plot_similarity_heatmap(similarity_matrix: np.ndarray, 
                          generated_paths: List[str], 
                          ikea_paths: List[str],
                          output_path: str) -> None:
    """
    Plot heatmap of similarity matrix.
    
    Args:
        similarity_matrix (np.ndarray): Cosine similarity matrix
        generated_paths (List[str]): List of generated image paths
        ikea_paths (List[str]): List of IKEA image paths
        output_path (str): Path to save the heatmap image
    """
    plt.figure(figsize=(12, 8))
    
    # Create heatmap
    sns.heatmap(similarity_matrix, 
                xticklabels=[os.path.basename(path) for path in ikea_paths[:10]],  # Limit labels
                yticklabels=[os.path.basename(path) for path in generated_paths[:10]],  # Limit labels
                cmap='viridis',
                cbar_kws={'label': 'Cosine Similarity'})
    
    plt.title('CLIP Similarity Matrix: Generated Images vs IKEA Products')
    plt.xlabel('IKEA Products')
    plt.ylabel('Generated Images')
    
    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Heatmap saved to: {output_path}")

def plot_top_similar_pairs(similarity_matrix: np.ndarray,
                          generated_paths: List[str],
                          ikea_paths: List[str],
                          top_k: int,
                          output_path: str) -> None:
    """
    Plot bar chart of top similar image pairs.
    
    Args:
        similarity_matrix (np.ndarray): Cosine similarity matrix
        generated_paths (List[str]): List of generated image paths
        ikea_paths (List[str]): List of IKEA image paths
        top_k (int): Number of top pairs to display
        output_path (str): Path to save the bar chart image
    """
    # Flatten the matrix to get all similarity scores
    flat_similarities = similarity_matrix.flatten()
    
    # Adjust top_k to not exceed the number of available elements
    actual_top_k = min(top_k, len(flat_similarities))
    
    # Handle case where there are no similarities
    if actual_top_k == 0:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No similarity data available', ha='center', va='center', 
                transform=plt.gca().transAxes, fontsize=16)
        plt.title('Top Similar Pairs')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Top similar pairs chart saved to: {output_path}")
        return
    
    # Find top similar pairs
    flat_indices = np.argpartition(flat_similarities, -actual_top_k)[-actual_top_k:]
    top_indices = np.unravel_index(flat_indices, similarity_matrix.shape)
    
    # Sort by similarity score (descending)
    similarities = similarity_matrix[top_indices]
    sorted_indices = np.argsort(similarities)[::-1]
    
    # Create labels and values for bar chart
    labels = []
    values = []
    
    for i in sorted_indices:
        gen_idx, ikea_idx = top_indices[0][i], top_indices[1][i]
        similarity = similarity_matrix[gen_idx, ikea_idx]
        
        gen_name = os.path.basename(generated_paths[gen_idx])
        ikea_name = os.path.basename(ikea_paths[ikea_idx])
        
        # Truncate long names
        gen_name = gen_name[:15] + "..." if len(gen_name) > 15 else gen_name
        ikea_name = ikea_name[:15] + "..." if len(ikea_name) > 15 else ikea_name
        
        labels.append(f"{gen_name}\nvs\n{ikea_name}")
        values.append(float(similarity))
    
    # Create bar chart
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(labels)), values, color='skyblue')
    
    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, values)):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.xlabel('Image Pairs')
    plt.ylabel('Cosine Similarity')
    plt.title(f'Top {actual_top_k} Most Similar Image Pairs')
    plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Top similar pairs chart saved to: {output_path}")

def plot_similarity_distribution(similarity_matrix: np.ndarray,
                               output_path: str) -> None:
    """
    Plot distribution of similarity scores.
    
    Args:
        similarity_matrix (np.ndarray): Cosine similarity matrix
        output_path (str): Path to save the distribution plot
    """
    # Flatten the matrix to get all similarity scores
    similarities = similarity_matrix.flatten()
    
    # Handle case where there are no similarities
    if len(similarities) == 0:
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, 'No similarity data available', ha='center', va='center', 
                transform=plt.gca().transAxes, fontsize=16)
        plt.title('Distribution of CLIP Similarity Scores')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"Similarity distribution plot saved to: {output_path}")
        return
    
    plt.figure(figsize=(10, 6))
    plt.hist(similarities, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
    plt.xlabel('Cosine Similarity')
    plt.ylabel('Frequency')
    plt.title('Distribution of CLIP Similarity Scores')
    plt.grid(True, alpha=0.3)
    
    # Add statistics
    mean_sim = float(np.mean(similarities))
    std_sim = float(np.std(similarities))
    plt.axvline(mean_sim, color='red', linestyle='--', 
                label=f'Mean: {mean_sim:.3f} ± {std_sim:.3f}')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Similarity distribution plot saved to: {output_path}")

def generate_summary_report(similarity_matrix: np.ndarray,
                          generated_paths: List[str],
                          ikea_paths: List[str],
                          output_path: str) -> None:
    """
    Generate a text summary report of the similarity results.
    
    Args:
        similarity_matrix (np.ndarray): Cosine similarity matrix
        generated_paths (List[str]): List of generated image paths
        ikea_paths (List[str]): List of IKEA image paths
        output_path (str): Path to save the summary report
    """
    # Calculate statistics
    flat_similarities = similarity_matrix.flatten()
    
    # Handle case where there are no similarities
    if len(flat_similarities) == 0:
        report = [
            "CLIP Similarity Evaluation Report",
            "=" * 50,
            "",
            "No similarity data available.",
            "Please ensure both generated images and IKEA images are present."
        ]
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
        print(f"Summary report saved to: {output_path}")
        return
    
    mean_similarity = float(np.mean(flat_similarities))
    std_similarity = float(np.std(flat_similarities))
    min_similarity = float(np.min(flat_similarities))
    max_similarity = float(np.max(flat_similarities))
    
    # Find top similar pairs
    top_k = min(5, len(flat_similarities))
    top_indices = None
    sorted_indices = []
    
    if top_k > 0:
        flat_indices = np.argpartition(flat_similarities, -top_k)[-top_k:]
        top_indices = np.unravel_index(flat_indices, similarity_matrix.shape)
        
        # Sort by similarity score (descending)
        similarities = similarity_matrix[top_indices]
        sorted_indices = np.argsort(similarities)[::-1]
    
    # Generate report
    report = []
    report.append("CLIP Similarity Evaluation Report")
    report.append("=" * 50)
    report.append("")
    report.append("SUMMARY STATISTICS")
    report.append("-" * 20)
    report.append(f"Number of generated images: {len(generated_paths)}")
    report.append(f"Number of IKEA images: {len(ikea_paths)}")
    report.append(f"Total comparisons: {similarity_matrix.size}")
    report.append(f"Mean similarity: {mean_similarity:.4f}")
    report.append(f"Standard deviation: {std_similarity:.4f}")
    report.append(f"Min similarity: {min_similarity:.4f}")
    report.append(f"Max similarity: {max_similarity:.4f}")
    report.append("")
    report.append("TOP SIMILAR PAIRS")
    report.append("-" * 20)
    
    for i in sorted_indices:
        if top_indices is not None:
            gen_idx, ikea_idx = top_indices[0][i], top_indices[1][i]
            similarity = float(similarity_matrix[gen_idx, ikea_idx])
            
            gen_name = os.path.basename(generated_paths[gen_idx])
            ikea_name = os.path.basename(ikea_paths[ikea_idx])
            
            report.append(f"{i+1}. Similarity: {similarity:.4f}")
            report.append(f"   Generated: {gen_name}")
            report.append(f"   IKEA: {ikea_name}")
            report.append("")
    
    # Save report
    with open(output_path, 'w') as f:
        f.write('\n'.join(report))
    
    print(f"Summary report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Visualize CLIP similarity evaluation results')
    parser.add_argument('--results_path', type=str, default='../similarity_results',
                        help='Path to similarity results files (without extension)')
    parser.add_argument('--output_dir', type=str, default='../clip_eval_results',
                        help='Directory to save visualization results')
    parser.add_argument('--top_k', type=int, default=10,
                        help='Number of top similar pairs to display')
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    try:
        # Load similarity data
        similarity_matrix, generated_paths, ikea_paths = load_similarity_data(args.results_path)
        
        print(f"Loaded similarity matrix with shape: {similarity_matrix.shape}")
        print(f"Generated images: {len(generated_paths)}")
        print(f"IKEA images: {len(ikea_paths)}")
        
        # Generate visualizations
        heatmap_path = os.path.join(args.output_dir, 'similarity_heatmap.png')
        plot_similarity_heatmap(similarity_matrix, generated_paths, ikea_paths, heatmap_path)
        
        bar_chart_path = os.path.join(args.output_dir, 'top_similar_pairs.png')
        plot_top_similar_pairs(similarity_matrix, generated_paths, ikea_paths, args.top_k, bar_chart_path)
        
        distribution_path = os.path.join(args.output_dir, 'similarity_distribution.png')
        plot_similarity_distribution(similarity_matrix, distribution_path)
        
        # Generate summary report
        report_path = os.path.join(args.output_dir, 'clip_eval_report.txt')
        generate_summary_report(similarity_matrix, generated_paths, ikea_paths, report_path)
        
        print(f"\nAll visualizations saved to: {args.output_dir}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run the CLIP similarity evaluation first to generate the results files.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()