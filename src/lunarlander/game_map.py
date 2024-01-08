# SPDX-License-Identifier: BSD-3-Clause

from typing import Any, List

import matplotlib as mpl
import numpy as np
from matplotlib.colors import Normalize
from PIL import Image
import pyglet
from scipy.ndimage import gaussian_filter

from . import config
from .config import scale_image
from .tools import periodic_distances, wrap_position


class GameMap:
    def __init__(self):
        # nx = con
        # ny = 1080 - config.scoreboard_width
        # self.array = np.zeros([config.ny, config.nx])

        profile = np.zeros([config.nx])
        nseeds = 100
        xseed = np.random.randint(config.nx, size=nseeds)

        profile[xseed] = 10000 * np.random.random(nseeds)

        self.smooth = gaussian_filter(profile, sigma=30, mode="wrap")

        # nsites = 20

        # sizes = np.random.randint(10, 100, size=nsites)
        # locs = np.random.randint(0, config.nx - 1, size=nsites)

        self.terrain = self.smooth.copy()

        # for i in range(nsites):
        #     w = sizes[i] // 2
        #     l = locs[i]
        #     self.terrain[l - w : l + w] = smooth[l - w]

        # y = np.arange(config.ny).reshape(config.ny, 1)
        # sel = y < self.terrain
        # self.array[sel] = 1

        # to_image = np.flipud(self.array * 255)
        # to_image = np.broadcast_to(
        #     to_image.reshape(to_image.shape + (1,)), to_image.shape + (3,)
        # )

        # img = Image.fromarray(to_image.astype(np.uint8))
        # self.background_image = pyglet.image.ImageData(
        #     width=img.width,
        #     height=img.height,
        #     fmt="RGB",
        #     data=img.tobytes(),
        #     pitch=-img.width * 3,
        # )

        self.background_image = self.terrain_to_image()

    def make_crater(self, x: int, y: int, radius: int):
        self.terrain[x - radius : x + radius] = float(self.terrain[x])
        self.background_image = self.terrain_to_image()

    def terrain_to_image(self):
        self.array = np.zeros([config.ny, config.nx])
        y = np.arange(config.ny).reshape(config.ny, 1)
        sel = y < self.terrain
        self.array[sel] = 1

        to_image = np.flipud(self.array * 255)
        to_image = np.broadcast_to(
            to_image.reshape(to_image.shape + (1,)), to_image.shape + (3,)
        )

        img = Image.fromarray(to_image.astype(np.uint8))
        return pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGB",
            data=img.tobytes(),
            pitch=-img.width * 3,
        )
