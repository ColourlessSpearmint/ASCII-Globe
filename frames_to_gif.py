import json
import argparse
from PIL import Image, ImageDraw, ImageFont

# Render a frame with given text and font size
def render_frame(text, font_size=10):
    font = ImageFont.truetype("cour.ttf", font_size)
    bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), text, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    img = Image.new('RGBA', (text_width, text_height), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, fill="white", font=font)
    
    return img

# Crop image to non-transparent content
def crop_to_content(img, bbox=None):
    if bbox is None:
        bbox = img.getbbox()  # Get bounding box of non-transparent content
    return img.crop(bbox) if bbox else img

# Resize image to a square, choosing the larger dimension
def resize_to_square(img):
    size = max(img.size)
    return img.resize((size, size), Image.LANCZOS)

# Parse CLI arguments
def parse_args():
    parser = argparse.ArgumentParser(description="Generate a square-cropped GIF from frames.")
    parser.add_argument("--input-file", type=str, default="earth_frames.json", help="Path to the input JSON file with frame data")
    parser.add_argument("--output-file", type=str, default="animated_globe.gif", help="Path to the output GIF file")
    parser.add_argument("--font_size", type=int, default=10, help="Font size for text rendering")
    parser.add_argument("--duration", type=int, default=100, help="Duration of each frame in milliseconds")

    return parser.parse_args()

# Load frames from JSON
def load_frames(input_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    return [frame for frame in data.get("frames", [])]

# Main processing function
def process_frames(input_file, output_file, font_size, duration):
    # Load frames
    frames = load_frames(input_file)

    # Render all frames
    rendered_frames = [render_frame(frame, font_size) for frame in frames]

    # Find the universal bounding box for all frames
    universal_bbox = None
    for frame in rendered_frames:
        frame_bbox = frame.getbbox()
        if universal_bbox is None:
            universal_bbox = frame_bbox
        else:
            # Update to the union of bounding boxes across all frames
            universal_bbox = (
                min(universal_bbox[0], frame_bbox[0]),
                min(universal_bbox[1], frame_bbox[1]),
                max(universal_bbox[2], frame_bbox[2]),
                max(universal_bbox[3], frame_bbox[3])
            )

    # Crop all frames to the universal bounding box
    cropped_frames = [crop_to_content(frame, universal_bbox) for frame in rendered_frames]

    # Resize each cropped frame to a square
    squared_frames = [resize_to_square(frame) for frame in cropped_frames]

    # Convert frames to 'P' mode for GIF compatibility
    indexed_frames = [frame.convert("P", palette=Image.ADAPTIVE, colors=256) for frame in squared_frames]

    # Save frames as a GIF
    indexed_frames[0].save(
        output_file,
        save_all=True,
        append_images=indexed_frames[1:],  # Append remaining frames
        duration=duration,  # Duration of each frame in milliseconds
        loop=0,  # Loop setting
        transparency=0,  # Index 0 is the transparent color
        disposal=2  # Clear previous frame after each one
    )

    print(f"GIF saved as {output_file}")

# Main execution
if __name__ == "__main__":
    args = parse_args()
    process_frames(args.input_file, args.output_file, args.font_size, args.duration)
