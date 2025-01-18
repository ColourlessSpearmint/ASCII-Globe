from PIL import Image
import numpy as np

def convert_to_ascii(image_path, output_path, palette=" .:;',wiogOLXHWYV@", target_width=202, target_height=80):
    """
    Convert an image to ASCII art and save it to a text file.
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the output text file
        palette (str): Characters to use for ASCII conversion, from darkest to brightest
        target_width (int): Width of the output ASCII art
        target_height (int): Height of the output ASCII art
    """
    # Load and resize image
    with Image.open(image_path) as img:
        # Convert to grayscale
        img = img.convert('L')
        
        # Calculate aspect ratio
        aspect_ratio = img.height / img.width
        
        # Resize image to target dimensions
        img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert image to numpy array
        pixels = np.array(img)
        
    # Create ASCII art
    ascii_art = []
    max_pixel = 255
    step = max_pixel / (len(palette) - 1)
    
    for row in pixels:
        ascii_row = ''
        for pixel in row:
            # Convert pixel value to palette index
            index = int(pixel / step)
            ascii_row += palette[index]
        ascii_art.append(ascii_row)
    
    # Save to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(ascii_art))

def main():
    # Example usage
    image_path = "mercator.png"  # Replace with your image path
    output_path = "ascii_texture.txt"
    
    # Custom palette (from darkest to brightest)
    custom_palette = " .:;',wiogOLXHWYV@"
    
    try:
        convert_to_ascii(
            image_path=image_path,
            output_path=output_path,
            palette=custom_palette,
            target_width=202,
            target_height=80
        )
        print(f"ASCII texture has been saved to {output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()