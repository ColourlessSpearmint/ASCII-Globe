from PIL import Image
import numpy as np

def convert_to_ascii(
    image_path, 
    output_path, 
    palette=" .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    target_width=202, 
    target_height=80,
    ocean_color=(0, 0, 255),    # Default ocean color (blue)
    ocean_char=":",             # Character to use for ocean
    color_threshold=30          # Tolerance for color matching
):
    """
    Convert a map image to ASCII art with uniform ocean and shaded land areas.
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the output text file
        palette (str): Characters to use for land ASCII conversion, from darkest to brightest
        target_width (int): Width of the output ASCII art
        target_height (int): Height of the output ASCII art
        ocean_color (tuple): RGB values for the ocean color to mask
        ocean_char (str): Character to use for ocean areas
        color_threshold (int): Threshold for color matching (0-255)
    """
    # Load image
    with Image.open(image_path) as img:
        # Resize image to target dimensions
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to RGB for ocean detection
        rgb_img = img.convert('RGB')
        rgb_pixels = np.array(rgb_img)
        
        # Convert to grayscale for land shading
        gray_img = img.convert('L')
        gray_pixels = np.array(gray_img)

    # Create ASCII art
    ascii_art = []
    max_pixel = 255
    step = max_pixel / (len(palette) - 1)
    
    for y in range(target_height):
        ascii_row = ''
        for x in range(target_width):
            pixel_rgb = rgb_pixels[y, x]
            
            # Check if pixel is ocean
            color_diff = sum(abs(c1 - c2) for c1, c2 in zip(pixel_rgb, ocean_color))
            if color_diff <= color_threshold * 3:
                ascii_row += ocean_char
            else:
                # Convert land pixel to ASCII based on brightness
                pixel_gray = gray_pixels[y, x]
                index = int(pixel_gray / step)
                ascii_row += palette[min(index, len(palette) - 1)]
                
        ascii_art.append(ascii_row)
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(ascii_art))

def main():
    # Example usage
    image_path = "input_image.png"  # Replace with your image path
    output_path = "textures/ascii_texture.txt"
    
    # Custom palette for land (from darkest to brightest)
    custom_palette = " .:;',wiogOLXHWYV@"
    
    try:
        convert_to_ascii(
            image_path=image_path,
            output_path=output_path,
            palette=custom_palette,
            target_width=202,
            target_height=80,
            ocean_color=(1,4,19),  # Blue for ocean
            ocean_char=".",           # Use colon for ocean
            color_threshold=20        # Adjust this value based on your needs
        )
        print(f"ASCII texture has been saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()