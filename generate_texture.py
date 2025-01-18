from PIL import Image
import numpy as np
import argparse

def convert_to_ascii(
    image_path, 
    output_path, 
    palette=" .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    target_width=202, 
    target_height=80,
    ocean_colors=[(0, 6, 20)],  # List of ocean colors
    ocean_char=" ",            # Character to use for ocean
    color_threshold=10         # Tolerance for color matching
):
    """
    Convert a map image to ASCII art with uniform ocean and shaded land areas.
    
    Args:
        image_path (str): Path to the input image
        output_path (str): Path for the output text file
        palette (str): Characters to use for land ASCII conversion, from darkest to brightest
        target_width (int): Width of the output ASCII art
        target_height (int): Height of the output ASCII art
        ocean_colors (list): List of RGB tuples for ocean colors to mask
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
            
            # Check if pixel matches any ocean color
            is_ocean = False
            for ocean_color in ocean_colors:
                color_diff = sum(abs(c1 - c2) for c1, c2 in zip(pixel_rgb, ocean_color))
                if color_diff <= color_threshold * 3:
                    is_ocean = True
                    break
            
            if is_ocean:
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

def parse_color(s):
    """Parse a color string in format 'R,G,B'"""
    try:
        r, g, b = map(int, s.split(','))
        return (r, g, b)
    except:
        raise argparse.ArgumentTypeError("Color must be in format 'R,G,B'")

def main():
    parser = argparse.ArgumentParser(description='Convert an image to ASCII art with ocean masking')
    parser.add_argument('--image_path', type=str, default="input_image.png", help='Path to the input image')
    parser.add_argument('--output_path', type=str, default="textures\\ascii_texture.txt", help='Path for the output text file')
    parser.add_argument('--width', type=int, default=202, help='Width of output ASCII art')
    parser.add_argument('--height', type=int, default=80, help='Height of output ASCII art')
    parser.add_argument('--palette', default=" .:;',wiogOLXHWYV@", help='ASCII characters for land, from darkest to brightest')
    parser.add_argument('--ocean-colors', type=parse_color, nargs='+', default=[(0,6,20)], 
                      help='Ocean colors in R,G,B format (can specify multiple)')
    parser.add_argument('--ocean-char', default=" ", help='Character to use for ocean')
    parser.add_argument('--threshold', type=int, default=10, help='Color matching threshold (0-255)')
    
    args = parser.parse_args()
    
    try:
        convert_to_ascii(
            image_path=args.image_path,
            output_path=args.output_path,
            palette=args.palette,
            target_width=args.width,
            target_height=args.height,
            ocean_colors=args.ocean_colors,
            ocean_char=args.ocean_char,
            color_threshold=args.threshold
        )
        print(f"ASCII texture has been saved to {args.output_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()