from dataclasses import dataclass
from typing import List, Set, Tuple

import noise
import numpy as np


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
    def from_noise(seed: int=np.random.randint(0,100)):
        size = (128, 128)
        noise_gen = TileableNoiseMap(shape=size, seed=seed)

        # levels = {
        #     0.25: 3, # Water
        #     0.35: 1, # Sand
        #     0.40: 2, # Grass
        #     0.95: 4, # Stone
        # }

        game_map = Map(w=size[0], h=size[1])
       
        for y in range(0, size[1]):
            for x in range(0, size[0]):
                noise_val = noise_gen.noise_map[y][x]

                if noise_val <= 0.0:
                    game_map.set_tile(x, y, 3) # Water
                    continue
                elif noise_val <= 0.03:
                    game_map.set_tile(x, y, 1) # Sand
                    continue
                elif noise_val <= 0.30:
                    game_map.set_tile(x, y, 2) # Grass
                    continue
                elif noise_val <= 0.40:
                    game_map.set_tile(x, y, 4) # Stone
                    continue
                game_map.set_tile(x, y, 5) # Snow

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
        shape: Tuple[int, int] = (1024, 1024),
        scale: float = 0.25,
        octaves: int = 6,
        persistence: float = 0.5,
        lacunarity: float = 2.0,
        seed: int = np.random.randint(0,100),
    ):
        assert _is_power_of_two(shape[0]) and _is_power_of_two(shape[1]), "Noise map is not a power of 2. This means it won't be wrappable/tileable!"

        self.shape = shape
        self.scale = scale
        self.octaves = octaves
        self.persistence = persistence
        self.lacunarity = lacunarity
        self.seed = seed #if seed is not None else np.random.randint(0,100)

        self.noise_map = np.zeros(shape)

        # make coordinate grid on [0,1]^2
        x_idx = np.linspace(0, 1, shape[0])
        y_idx = np.linspace(0, 1, shape[1])
        map_x, map_y = np.meshgrid(x_idx, y_idx)

        # apply perlin noise, instead of np.vectorize, consider using itertools.starmap()
        self.noise_map = np.vectorize(noise.pnoise2)(map_x/scale,
                                map_y/scale,
                                octaves=self.octaves,
                                persistence=self.persistence,
                                lacunarity=self.lacunarity,
                                repeatx=3,
                                repeaty=3,
                                base=self.seed)
        # tmp = np.floor((self.noise_map + 0.5) * 2)

        # img = np.floor((self.noise_map + 0.5) * 255).astype(np.uint8) # <- Normalize world first
        # from PIL import Image
        # Image.fromarray(img, mode='L').show()