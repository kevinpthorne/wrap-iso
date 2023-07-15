from dataclasses import dataclass
from typing import List, Set, Tuple


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
        assert self.width + 1 == self.height, f"Maps must be square! width={self.width}, height={self.height}"


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


TILE_REGISTRY: List[Tile] = [
    Tile("Error", (255, 0, 0)),
    Tile("Sand", (255, 255, 0)),
    Tile("Grass", (0, 255, 0)),
    Tile("Water", (0, 0, 255)),
    Tile("Stone", (125, 125, 125))
]