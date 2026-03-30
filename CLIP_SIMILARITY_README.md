# CLIP Image Similarity Module

This module provides functionality to compute CLIP embeddings for images and calculate similarity matrices between two sets of images (e.g., generated interior designs and IKEA products).

## Features

- Load a pretrained CLIP model (e.g., "ViT-B/32") with GPU support if available
- Image preprocessing pipeline compatible with the CLIP model
- Compute normalized CLIP embeddings from image file paths
- Load two lists of image paths—one for generated images and one for IKEA dataset images
- Compute CLIP embeddings for all images in both sets
- Calculate a cosine similarity matrix between generated image embeddings and IKEA image embeddings
- Return or save this similarity matrix in a format suitable for analysis or visualization
- Efficient GPU memory use and clear, modular, well-commented code with automatic type hints

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. The CLIP library will be installed from the GitHub repository as specified in requirements.txt

## Usage

### Python Module

```python
from clip_similarity import CLIPImageSimilarity

# Initialize the similarity evaluator
evaluator = CLIPImageSimilarity()

# Compute similarity matrix between two image directories
similarity_matrix, generated_paths, ikea_paths = evaluator.compute_similarity_matrix(
    "../generated_images",  # Directory with generated images
    "../ikea_dataset"       # Directory with IKEA images
)

# Find most similar pairs
top_pairs = evaluator.find_most_similar_pairs(
    similarity_matrix, generated_paths, ikea_paths, top_k=5
)

# Save results
evaluator.save_similarity_matrix(
    similarity_matrix, generated_paths, ikea_paths, 
    "../similarity_results"
)
```

### API Endpoint

The module is also integrated with the Flask backend as an API endpoint:

```
POST /api/compute-similarity
{
  "generatedImagesDir": "../generated_images",
  "ikeaImagesDir": "../ikea_dataset"
}
```

### Test Script

Run the test script to verify functionality:

```bash
python test_clip_similarity.py
```

## Requirements

- Python 3.7+
- PyTorch
- CLIP (OpenAI)
- scikit-learn
- Pillow
- NumPy

## Output

The module produces:
1. A cosine similarity matrix between all generated and IKEA images
2. Lists of the most similar image pairs
3. Saved results in numpy format for further analysis

## Notes

- The CLIP model will automatically use GPU if available
- Image preprocessing follows CLIP's recommended pipeline
- Embeddings are normalized for accurate cosine similarity computation
- The module handles errors gracefully and skips invalid images