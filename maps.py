from dataclasses import dataclass
import itertools
from typing import List, Set, Tuple

import numpy as np
from pynoise.noisemodule import Perlin
from pynoise.noiseutil import noise_map_plane


# @dataclass
# class Color:
#     rgb: Tuple[int, int, int]

#     def __init__(self, r, g, b):


#     # def as_rgb(self) -> Tuple[int, int, int]:
#     #     return self.rgb


@dataclass
class Tile:
    name: str
    color: Tuple[int, int, int]

    def __eq__(self, other):
        return isinstance(other, Tile) and other.name == self.name

    def __hash__(self):
        return hash(self.name)


class Map:
    tiles: List[List[Tile]]
    width: int
    height: int

    def __init__(self, tiles=None, w=None, h=None):
        if tiles is None:
            assert w is not None and h is not None, "if tiles aren't given, w and h need to be given"
            self.tiles = [[Map.tile_of_id(0) for _ in range(0, w)] for _ in range(0, h)]
        else:
            self.tiles = tiles
        self.width = len(self.tiles[0])
        self.height = len(self.tiles)
        assert self.width == self.height, f"Maps must be square! width={self.width}, height={self.height}"


    def __getitem__(self, items):
        if isinstance(items, tuple) and len(items) == 2:
            x, y = items
            return tiles[y][x]  # Tile
        return tiles[items]  # List[Tile]

    def at(self, x: int, y: int) -> Tile:
        return self.tiles[int(y)][int(x)]

    def set_tile(self, x: int, y: int, tile_id: int=None, tile: Tile=None):
        if tile_id is not None:
            self.tiles[y][x] = Map.tile_of_id(tile_id)
        elif tile is not None:
            raise NotImplementedError()
        #     self.tiles[y][x] = tile.

    @staticmethod
    def tile_of_id(i: int) -> Tile:
        return TILE_REGISTRY[i]

    @staticmethod
    def from_txt_file(path: str):
        with open(path, 'r') as file:
            raw_map = file.read().split("\n")
        line_lengths = list(map(lambda line: len(line), raw_map))
        assert min(line_lengths) == max(line_lengths), "Map lines must be of the same width and height!"

        map_width = max(line_lengths)
        map_height = len(raw_map)
        
        game_map = Map(w=map_width, h=map_height)
        txt_tile_registry = {
            "w": 3,
            "g": 2
        }

        for y in range(0, map_height):
            for x in range(0, map_width):
                char = raw_map[y][x]
                if char not in list(txt_tile_registry.keys()):
                    raise ValueError(f"Unrecognized character '{char}' on line {y}, col {x}")
                game_map.set_tile(x, y, txt_tile_registry[char])
                if y == 0 or x == 0:
                    game_map.set_tile(x, y, 0)

        return game_map

    @staticmethod
    def from_noise(**map_json: dict):
        map_json['size'] = (map_json['size'], map_json['size'])

        noise_gen = TileableNoiseMap(**map_json)

        # levels = {
        #     0.25: 3, # Water
        #     0.35: 1, # Sand
        #     0.40: 2, # Grass
        #     0.95: 4, # Stone
        #     None: 5
        # }

        game_map = Map(w=map_json['size'][0], h=map_json['size'][1])
       
        for y in range(0, map_json['size'][1]):
            for x in range(0, map_json['size'][0]):
                noise_val = noise_gen.noise_map[y][x]

                for i, window in enumerate(map_json['generator']['noise_windows']):
                    if window is None:
                        game_map.set_tile(x, y, map_json['generator']['tile_ids_for_windows'][-1])
                        break
                    elif noise_val <= window:
                        game_map.set_tile(x, y, map_json['generator']['tile_ids_for_windows'][i])
                        break

        return game_map


TILE_REGISTRY: List[Tile] = [
    Tile("Error", (255, 0, 0)),
    Tile("Sand", (255, 255, 0)),
    Tile("Grass", (0, 255, 0)),
    Tile("Water", (0, 0, 255)),
    Tile("Stone", (125, 125, 125)),
    Tile("Snow", (240, 240, 240)),
]

def _is_power_of_two(n: int) -> bool:
    return (n & (n-1) == 0) and n != 0

class TileableNoiseMap:

    def __init__(self,
        size: Tuple[int, int] = (1024, 1024),
        frequency: int = 1,
        octaves: int = 8,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        seed: int = np.random.randint(0,100),
        **_
    ):
        # assert _is_power_of_two(size[0]) and _is_power_of_two(size[1]), "Noise map is not a power of 2. This means it won't be wrappable/tileable!"

        self.size = size
        self.frequency = frequency
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = seed

        # self.noise_map = np.zeros(size)

        # # make coordinate grid on [0,1]^2
        # x_idx = np.linspace(0, 1, size[0])
        # y_idx = np.linspace(0, 1, size[1])
        # map_x, map_y = np.meshgrid(x_idx, y_idx)

        perlin = Perlin(frequency=self.frequency, lacunarity=self.lacunarity, octaves=self.octaves, persistence=self.persistence, seed=self.seed)
        self.noise_map = noise_map_plane(
            width=size[0],
            height=size[1],
            lower_x=0,
            upper_x=1,
            lower_z=0,
            upper_z=1,
            source=perlin,
            seamless=True,
        )
        self.noise_map = np.reshape(self.noise_map, size)

        # img = np.floor((self.noise_map + 0.5) * 255).astype(np.uint8)
        # from PIL import Image
        # Image.fromarray(img, mode='L').show()
