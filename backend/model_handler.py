import torch
from diffusers import StableDiffusionPipeline
import os
import gc
import random

class InteriorDesignGenerator:
    def __init__(self, model_id="runwayml/stable-diffusion-v1-5"):
        """
        Initialize the Interior Design Generator with Stable Diffusion
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        try:
            # Load Stable Diffusion pipeline
            print("Loading Stable Diffusion pipeline...")
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                safety_checker=None,
                requires_safety_checker=False
            )

            if torch.cuda.is_available():
                self.pipeline = self.pipeline.to(self.device)
                # Enable memory efficient attention if available
                try:
                    self.pipeline.enable_attention_slicing()
                    print("Enabled attention slicing for memory efficiency")
                except:
                    pass
                
                # Clear cache
                torch.cuda.empty_cache()
            
            print("Pipeline loaded successfully!")
        except Exception as e:
            print(f"Error loading pipeline: {str(e)}")
            raise

    def generate_room_scene(self, prompt, negative_prompt="", num_images=1,
                           guidance_scale=7.5, num_inference_steps=30,
                           height=512, width=512, seed=None):
        """
        Generate room scene images using Stable Diffusion
        """
        try:
            print(f"Starting generation with {num_inference_steps} steps...")
            
            # If seed is not provided, generate a random seed
            if seed is None:
                seed = random.randint(0, 2**32 - 1)
            
            # For multiple images, we'll generate them with slight variations
            images = []
            
            for i in range(num_images):
                print(f"Generating image {i+1}/{num_images}...")
                
                # Use a different seed for each image to create variation
                current_seed = seed + i
                generator = torch.Generator(device=self.device).manual_seed(current_seed)
                
                # Modify prompt slightly for different views
                modified_prompt = prompt
                if num_images > 1:
                    view_descriptions = [
                        "front view",
                        "side view", 
                        "perspective view",
                        "top-down view",
                        "angled view"
                    ]
                    # Add a view description to the prompt for variety
                    if i < len(view_descriptions):
                        modified_prompt = f"{prompt}, {view_descriptions[i]}"
                    else:
                        modified_prompt = f"{prompt}, view {i+1}"
                
                # Use autocast only for CUDA
                if torch.cuda.is_available():
                    with torch.cuda.amp.autocast():
                        image = self.pipeline(
                            prompt=modified_prompt,
                            negative_prompt=negative_prompt,
                            num_inference_steps=num_inference_steps,
                            guidance_scale=guidance_scale,
                            height=height,
                            width=width,
                            generator=generator
                        ).images[0]
                else:
                    # CPU mode - no autocast
                    image = self.pipeline(
                        prompt=modified_prompt,
                        negative_prompt=negative_prompt,
                        num_inference_steps=num_inference_steps,
                        guidance_scale=guidance_scale,
                        height=height,
                        width=width,
                        generator=generator
                    ).images[0]

                images.append(image)
                print(f"Image {i+1} generated successfully!")

                # Clear cache between generations
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    gc.collect()

            return images
            
        except torch.cuda.OutOfMemoryError as e:
            print(f"CUDA out of memory: {str(e)}")
            # Clear cache and try with smaller settings
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
            raise Exception("Out of memory. Try reducing image size or inference steps.")
        except Exception as e:
            print(f"Error during generation: {str(e)}")
            raise