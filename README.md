# ASCII-Globe

ASCII-Globe is a Python script that renders a 3D representation of the Earth in the console using ASCII characters. It unwraps texture files to create a rotating globe effect.

## Features

- Renders a 3D globe using ASCII characters.
- Supports day and night textures.
- Real-time rotation.
- Adjustable scale, rotation speed, and axial tilt.

## Installation

To get started, first clone the repository.

```bash
git clone https://github.com/ColourlessSpearmint/ASCII-Globe.git
cd ASCII-Globe
```

Next, you must obtain texture files (`earth.txt` and `earth_night.txt`) and place them in the `textures/` directory. 

This can be done by running the following script to download them from the [original repo](https://github.com/DinoZ1729) 

```bash
curl -o "textures/earth.txt" https://raw.githubusercontent.com/DinoZ1729/Earth/refs/heads/master/earth.txt
curl -o "textures/earth_night.txt" https://raw.githubusercontent.com/DinoZ1729/Earth/refs/heads/master/earth_night.txt
```

Texture files can also be aquired using the generate_texture.py script. Below is an example script that downloads maps images from NASA and applies the texture generator.

```bash
mkdir downloads
curl -o "downloads/nasa_day.jpg" https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74218/world.200412.3x5400x2700.jpg
curl -o "downloads/nasa_night.jpg" https://eoimages.gsfc.nasa.gov/images/imagerecords/144000/144896/BlackMarble_2012_01deg_gray.jpg
mkdir textures
python generate_texture.py --image_path downloads/nasa_day.jpg --output_path textures/earth.txt --ocean-colors 0,6,20 20,57,101 6,24,60 --threshold 10 --ocean-char .
python generate_texture.py --image_path downloads/nasa_night.jpg --output_path textures/earth_night.txt
```

## Usage

Run the script with optional arguments to adjust the rendering settings:

```sh
python render.py [--scale SCALE] [--speed SPEED] [--tilt TILT] [--sleep SLEEP]
```

## Arguments
- --scale: Scale of the Earth (default: 1.0)
- --speed: Rotation speed multiplier (default: 1.0)
- --tilt: Axial tilt in degrees (default: 23.5)
- --sleep: Sleep to allow reading settings (default: True)

## Example

```sh
python render.py --scale 1.5 --speed 2.0 --tilt 23.5 --sleep False
```

## License

This project is licensed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html). 

You are free to use, modify, and distribute this software, provided that any derivative works or redistributed versions comply with the terms of the GPL-3.0 license. 

For more details, see the [LICENSE](./LICENSE) file in this repository.

## Acknowledgements

This project was heavily inspired by [Earth](https://github.com/DinoZ1729/Earth) by [DinoZ1729](https://github.com/DinoZ1729). My original intention with this project was to port DinoZ1729's code from C++ to Python, but it eventually became more feature-rich than a simple port.

For licensing reasons, the texture files included in the original project have been ommited, but I do provide links to download them.