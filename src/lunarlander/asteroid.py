# SPDX-License-Identifier: BSD-3-Clause

import uuid
from itertools import chain
from typing import Any, Iterator, Tuple

from matplotlib.colors import hex2color
import numpy as np
from PIL import Image
import pyglet

from . import config
from .base import Base
from .core import Instructions

# from .game_map import MapView
from .tools import recenter_image, string_to_color, text_to_raw_image


class Asteroid:
    def __init__(
        self,
        x: float,
        y: float,
        v: float,
        heading: float,
        size: float,
        batch: Any,
    ):
        self.id = uuid.uuid4().hex
        # self.x = x
        # self.y = y
        self.v = v
        self.size = int(size)
        self.heading = heading
        self.make_avatar(x, y, batch)

    def make_avatar(self, x, y, batch):
        img = Image.open(config.resources / f"asteroid.png")
        img = img.resize((self.size, self.size)).convert("RGBA")

        imd = pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
        self.avatar = pyglet.sprite.Sprite(
            img=recenter_image(imd),
            x=x,
            y=y,
            batch=batch,
        )
        self.avatar.rotation = -self.heading

    @property
    def x(self):
        return self.avatar.x

    @x.setter
    def x(self, value):
        self.avatar.x = value

    @property
    def y(self):
        return self.avatar.y

    @y.setter
    def y(self, value):
        self.avatar.y = value

    def move(self, dt):
        self.x += self.v * np.cos(np.radians(self.heading)) * dt
        self.y += self.v * np.sin(np.radians(self.heading)) * dt
        self.x = self.x % config.nx

    def tip(self):
        tipx = self.x + self.size * np.cos(np.radians(self.heading)) / 2
        tipy = self.y + self.size * np.sin(np.radians(self.heading)) / 2
        return tipx % config.nx, tipy
