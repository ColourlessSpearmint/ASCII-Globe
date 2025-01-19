import math
import os
import time
import sys
import argparse
import json

# Screen dimensions
WIDTH = 800
HEIGHT = 608

# Width and height of each character in pixels
dW = 4
dH = 8

# Constants
PI = math.pi
PALETTE = " .:;',wiogOLXHWYV@"
MAX_SCALE = 1.15

# Default parameters
DEFAULT_SCALE = 1.0
DEFAULT_SPEED = 1.0
DEFAULT_TILT = 23.5
DEFAULT_SLEEP = True
DEFAULT_LIGHTING = True
DEFAULT_SAVE_FRAMES = False
DEFAULT_OUTPUT_FILE = "earth_frames.json"
DEFAULT_OVERRIDE_MAX_SCALE = False

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def parse_arguments():
    parser = argparse.ArgumentParser(description='Earth Console Renderer')
    parser.add_argument('--scale', type=float, default=DEFAULT_SCALE,
                      help=f'Scale of the Earth (default: {DEFAULT_SCALE})')
    parser.add_argument('--speed', type=float, default=DEFAULT_SPEED,
                      help=f'Rotation speed multiplier (default: {DEFAULT_SPEED})')
    parser.add_argument('--tilt', type=float, default=DEFAULT_TILT,
                      help=f'Axial tilt in degrees (default: {DEFAULT_TILT})')
    parser.add_argument('--sleep', type=str2bool, default=DEFAULT_SLEEP,
                      help=f'Sleep to allow reading settings (default: {DEFAULT_SLEEP})')
    parser.add_argument('--lighting', type=str2bool, default=DEFAULT_LIGHTING,
                      help=f'Toggle lighting/night effect (default: {DEFAULT_LIGHTING})')
    parser.add_argument('--save-frames', type=str2bool, default=DEFAULT_SAVE_FRAMES,
                      help=f'Save frames to JSON file (default: {DEFAULT_SAVE_FRAMES})')
    parser.add_argument('--output-file', type=str, default=DEFAULT_OUTPUT_FILE,
                      help=f'Output JSON file path (default: {DEFAULT_OUTPUT_FILE})')
    parser.add_argument('--override-max-scale', type=str2bool, default=DEFAULT_OVERRIDE_MAX_SCALE,
                      help=f'Disable scale maximum (default: {DEFAULT_OVERRIDE_MAX_SCALE})')
    return parser.parse_args()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def goto_xy(x, y):
    print(f"\033[{y};{x}H", end='')

def find_index(c, s):
    try:
        return s.index(c)
    except ValueError:
        return -1

def draw_point(canvas, A, B, c):
    if A < 0 or B < 0 or A >= WIDTH // dW or B >= HEIGHT // dH:
        return
    canvas[B][A] = c

def cross(a, b):
    return [
        a[1]*b[2] - a[2]*b[1],
        a[2]*b[0] - a[0]*b[2],
        a[0]*b[1] - a[1]*b[0]
    ]

def magnitude(r):
    return math.sqrt(sum(x*x for x in r))

def normalize(r):
    mag = magnitude(r)
    if mag == 0:
        return r
    return [x/mag for x in r]

def dot(a, b):
    return sum(x*y for x, y in zip(a, b))

def vector(b, c):
    return [b[i]-c[i] for i in range(3)]

def transform_vector(vec, m):
    x = vec[0]*m[0] + vec[1]*m[4] + vec[2]*m[8] + m[12]
    y = vec[0]*m[1] + vec[1]*m[5] + vec[2]*m[9] + m[13]
    z = vec[0]*m[2] + vec[1]*m[6] + vec[2]*m[10] + m[14]
    return [x, y, z]

def rotate_x(vec, theta):
    a = math.sin(theta)
    b = math.cos(theta)
    m = [
        1, 0, 0,
        0, b, -a,
        0, a, b
    ]
    return transform_vector_2(vec, m)

def transform_vector_2(vec, m):
    x = m[0]*vec[0] + m[1]*vec[1] + m[2]*vec[2]
    y = m[3]*vec[0] + m[4]*vec[1] + m[5]*vec[2]
    z = m[6]*vec[0] + m[7]*vec[1] + m[8]*vec[2]
    return [x, y, z]

def clamp(x, min_val, max_val):
    return max(min(x, max_val), min_val)

class Camera:
    def __init__(self, r, alfa, beta):
        a = math.sin(alfa)
        b = math.cos(alfa)
        c = math.sin(beta)
        d = math.cos(beta)
        
        self.x = r * b * d
        self.y = r * a * d
        self.z = r * c
        
        # Create camera matrix
        self.matrix = [
            -a, b, 0, 0,
            b*c, a*c, -d, 0,
            b*d, a*d, c, 0,
            self.x, self.y, self.z, 1
        ]

    def render_sphere(self, canvas, radius, angle_offset, earth, earth_night, scale=1.0, tilt=23.5, lighting=True):
        light = [0, 999999, 0]  # Sun position
        
        # Get dimensions of the texture
        texture_height = len(earth)
        texture_width = len(earth[0]) if texture_height > 0 else 0
        
        if texture_height == 0 or texture_width == 0:
            print("Error: Invalid texture dimensions")
            return
        
        # Apply scale to radius
        radius *= scale
        
        # Convert tilt to radians
        tilt_rad = math.radians(tilt)
        
        for yi in range(HEIGHT // dH):
            for xi in range(WIDTH // dW):
                o = [self.x, self.y, self.z]
                u = [
                    -((xi-WIDTH/dW/2)+0.5)/(WIDTH/dW/2)*1.2,
                    ((yi-HEIGHT/dH/2)+0.5)/(WIDTH/dH/2),
                    -1
                ]
                
                u = transform_vector(u, self.matrix)
                u = [u[0]-self.x, u[1]-self.y, u[2]-self.z]
                u = normalize(u)
                
                discriminant = dot(u,o)*dot(u,o) - dot(o,o) + radius*radius
                if discriminant < 0:
                    continue
                    
                distance = -math.sqrt(discriminant)-dot(u,o)
                inter = [
                    o[0]+distance*u[0],
                    o[1]+distance*u[1],
                    o[2]+distance*u[2]
                ]
                
                n = normalize(inter)
                l = normalize(vector(light, inter))
                luminance = clamp(5*(dot(n,l))+0.5, 0, 1) if lighting else 1.0
                
                # Apply tilt before calculating texture coordinates
                temp = rotate_x(inter.copy(), -tilt_rad)
                
                phi = -temp[2]/radius/2 + 0.5
                theta = -math.atan2(temp[1], temp[0])/PI + 0.5 + angle_offset/2/PI
                theta -= math.floor(theta)
                
                earthX = int(theta * (texture_width - 1))
                earthY = int(phi * (texture_height - 1))
                
                earthX = clamp(earthX, 0, texture_width - 1)
                earthY = clamp(earthY, 0, texture_height - 1)
                
                try:
                    day = find_index(earth[earthY][earthX], PALETTE)
                    night = find_index(earth_night[earthY][earthX], PALETTE)
                    
                    if day >= 0 and night >= 0:
                        index = int((1.0-luminance)*night + luminance*day)
                        index = clamp(index, 0, len(PALETTE) - 1)
                        draw_point(canvas, xi, yi, PALETTE[index])
                except IndexError:
                    continue

def load_texture(filename):
    try:
        with open(filename, 'r') as file:
            return [line.rstrip('\n') for line in file]
    except FileNotFoundError:
        print(f"Error: Could not find {filename}")
        return []
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return []

def main():
    args = parse_arguments()
    if not args.override_max_scale:
        assert args.scale <= MAX_SCALE, f"The maximum scale is {MAX_SCALE}; your scale, {args.scale}, is too large. Use --override-max-scale to bypass this."
    earth = load_texture('textures/earth.txt')
    earth_night = load_texture('textures/earth_night.txt')
    
    if not earth or not earth_night:
        print("Failed to load textures")
        return
    
    print(f"Earth Renderer Settings:")
    print(f"Scale: {args.scale}")
    print(f"Speed: {args.speed}x")
    print(f"Tilt: {args.tilt}°")
    
    print(f"Texture dimensions: {len(earth[0])}x{len(earth)}")
    print(f"Lighting: {args.lighting}")
    print(f"Save frames: {args.save_frames}")
    if args.save_frames:
        print(f"Output file: {args.output_file}")
    print("\nPress Ctrl+C to exit...")
    
    angle_offset = 0
    frames = []
    if args.save_frames:
        while angle_offset < 2 * PI:  # Stop after one revolution
            cam = Camera(2, 0, 0)
            canvas = [[' ' for _ in range(WIDTH // dW)] for _ in range(HEIGHT // dH)]
            
            cam.render_sphere(canvas, 1, angle_offset, earth, earth_night, 
                            scale=args.scale, tilt=args.tilt, lighting=args.lighting)
            
            frame_data = '\n'.join(''.join(row) for row in canvas)
            frames.append(frame_data)
            
            angle_offset += (2*PI/18) * args.speed
            
        frames.pop()  # Remove duplicate start and end frame
        print(f"\nSaving {len(frames)} frames to {args.output_file}...")
        with open(args.output_file, 'w') as f:
            json.dump({"frames": frames}, f)
        print("Frames saved successfully.")
    else:
        while True:
            cam = Camera(2, 0, 0)
            canvas = [[' ' for _ in range(WIDTH // dW)] for _ in range(HEIGHT // dH)]
            
            cam.render_sphere(canvas, 1, angle_offset, earth, earth_night, 
                            scale=args.scale, tilt=args.tilt, lighting=args.lighting)
            
            # Display
            clear_screen()
            print('\n'.join(''.join(row) for row in canvas))
            goto_xy(0, 0)
            
            # Apply speed multiplier to rotation
            angle_offset += (2*PI/18) * args.speed
            time.sleep(0.1)  # Base delay
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)