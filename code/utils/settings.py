from pathlib import Path


WIDTH = 1280
HEIGHT = 720
WINSIZE = (WIDTH, HEIGHT)
FPS = 60

# Player
PLAYER_SPEED = 200


_HERE = Path(__file__).parent.resolve()
ASSETS_PATH = _HERE.joinpath("../../assets").resolve()
LEVELS_PATH = ASSETS_PATH.joinpath("levels").resolve()
SPRITES_PATH = ASSETS_PATH.joinpath("sprites").resolve()

