import math
import os
import time
import sys

# Screen dimensions
WIDTH = 800
HEIGHT = 608

# Width and height of each character in pixels
dW = 4
dH = 8

# Constants
PI = math.pi
PALETTE = " .:;',wiogOLXHWYV@"

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

    def convert(self, tx, ty, tz):
        vec = [tx, ty, tz]
        vec = transform_vector(vec, self.matrix)
        if vec[2] > 0:
            return None
            
        xI = -vec[0]/vec[2]
        yI = -vec[1]/vec[2]
        xI *= WIDTH/dW/2
        yI *= WIDTH/dH/2
        xI += WIDTH/dW/2
        yI += HEIGHT/dH/2
        
        return [int(xI), int(yI)]

    def render_sphere(self, canvas, radius, angle_offset, earth, earth_night):
        light = [0, 999999, 0]  # Sun position
        
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
                luminance = clamp(5*(dot(n,l))+0.5, 0, 1)
                
                temp = rotate_x(inter.copy(), -PI*2*26/360)
                
                phi = -temp[2]/radius/2 + 0.5
                theta = math.atan2(temp[1], temp[0])/PI + 0.5 + angle_offset/2/PI
                theta -= math.floor(theta)
                
                earthX = int(theta * 202)
                earthY = int(phi * 80)
                
                if 0 <= earthY < 80 and 0 <= earthX < 202:
                    day = find_index(earth[earthY][earthX], PALETTE)
                    night = find_index(earth_night[earthY][earthX], PALETTE)
                    index = int((1.0-luminance)*night + luminance*day)
                    if 0 <= index < len(PALETTE):
                        draw_point(canvas, xi, yi, PALETTE[index])

def main():
    # Read earth textures
    with open('textures/earth.txt', 'r') as file:
        earth = [line.strip() for line in file]
        
    with open('textures/earth_night.txt', 'r') as file:
        earth_night = [line.strip() for line in file]
    
    angle_offset = 0
    
    while True:
        cam = Camera(2, 0, 0)
        canvas = [[' ' for _ in range(WIDTH // dW)] for _ in range(HEIGHT // dH)]
        
        cam.render_sphere(canvas, 1, angle_offset, earth, earth_night)
        
        # Display
        clear_screen()
        print('\n'.join(''.join(row) for row in canvas))
        goto_xy(0, 0)
        
        angle_offset += 2*PI/18
        time.sleep(0.1)  # Add small delay to control rotation speed

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)