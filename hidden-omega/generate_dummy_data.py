from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import os

os.makedirs("test_data", exist_ok=True)

def create_noisy_texture(width, height, color_range):
    # Create simple Gaussian noise
    array = np.random.randint(color_range[0], color_range[1], (height, width, 3), dtype=np.uint8)
    img = Image.fromarray(array)
    return img

def generate_ultrasound():
    width, height = 512, 512
    # Background black
    img = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(img)
    
    # Fan shape mask
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.pieslice([50, 50, 462, 462], 30, 150, fill=255)
    
    # Texture (Grainy grayscale)
    texture = create_noisy_texture(width, height, (50, 150))
    # Convert texture to grayscale
    texture = texture.convert('L').convert('RGB')
    
    # Composite
    img.paste(texture, (0,0), mask)
    
    # Add some "features"
    draw.ellipse([200, 200, 250, 250], fill=(20, 20, 20), outline=None) # Dark spot
    
    img.save("test_data/dummy_ultrasound.jpg")
    print("Generated dummy_ultrasound.jpg")

def generate_ct():
    width, height = 512, 512
    img = Image.new('RGB', (width, height), 'black')
    draw = ImageDraw.Draw(img)
    
    # Body contour
    draw.ellipse([100, 100, 412, 412], fill=(100, 100, 100))
    
    # Liver-ish shape (Right side)
    draw.ellipse([120, 150, 280, 350], fill=(160, 160, 160))
    
    # Tumor (Bright spot)
    draw.ellipse([200, 250, 230, 280], fill=(220, 220, 220))
    
    # Spine
    draw.ellipse([240, 400, 272, 430], fill=(255, 255, 255))
    
    img = img.filter(ImageFilter.GaussianBlur(2))
    img.save("test_data/dummy_ct.jpg")
    print("Generated dummy_ct.jpg")

def generate_histo():
    width, height = 512, 512
    # H&E Background: Pinkish (Eosin)
    # R: 200-255, G: 150-200, B: 200-240
    
    # Create pink noise
    base = np.zeros((height, width, 3), dtype=np.uint8)
    base[:,:,0] = np.random.randint(220, 255, (height, width))
    base[:,:,1] = np.random.randint(180, 220, (height, width))
    base[:,:,2] = np.random.randint(200, 240, (height, width))
    img = Image.fromarray(base)
    draw = ImageDraw.Draw(img)
    
    # Add Nuclei: Purple/Blue (Hematoxylin)
    # Random dots
    for _ in range(500):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        r = np.random.randint(3, 8)
        color = (
            np.random.randint(50, 100), # R
            np.random.randint(0, 50),   # G
            np.random.randint(100, 180) # B
        )
        draw.ellipse([x-r, y-r, x+r, y+r], fill=color)
        
    # Add Fat Vacuoles: White bubbles
    for _ in range(50):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        r = np.random.randint(10, 30)
        draw.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255), outline=(230, 200, 220))

    img.save("test_data/dummy_histopathology.jpg")
    print("Generated dummy_histopathology.jpg")

if __name__ == "__main__":
    generate_ultrasound()
    generate_ct()
    generate_histo()
