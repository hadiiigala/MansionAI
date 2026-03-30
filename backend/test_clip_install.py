"""
Test script to verify CLIP installation
"""

def test_clip_installation():
    try:
        import torch
        import clip
        print("✓ PyTorch is installed")
        print(f"  Version: {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        
        # Try to load a CLIP model
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        print("✓ CLIP model loaded successfully")
        print(f"  Device: {device}")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print("Please install the required packages:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing CLIP installation...")
    success = test_clip_installation()
    if success:
        print("\n✓ All tests passed! CLIP is ready to use.")
    else:
        print("\n✗ Tests failed. Please check your installation.")