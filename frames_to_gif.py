import json
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

# Load frames from JSON
with open("earth_frames.json", 'r') as f:
    data = json.load(f)

# Render all frames
frames = [render_frame(frame) for frame in data.get("frames", [])]

# Find the universal bounding box for all frames
universal_bbox = None
for frame in frames:
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
cropped_frames = [crop_to_content(frame, universal_bbox) for frame in frames]

# Resize each cropped frame to a square
squared_frames = [resize_to_square(frame) for frame in cropped_frames]

# Convert frames to 'P' mode for GIF compatibility
indexed_frames = [frame.convert("P", palette=Image.ADAPTIVE, colors=256) for frame in squared_frames]

# Save frames as a GIF
output_file = "output.gif"
indexed_frames[0].save(
    output_file,
    save_all=True,
    append_images=indexed_frames[1:],  # Append remaining frames
    duration=100,  # Duration of each frame in milliseconds
    loop=0,  # Infinite loop
    transparency=0,  # Index 0 is the transparent color
    disposal=2  # Clear previous frame after each one
)

print(f"GIF saved as {output_file}")
