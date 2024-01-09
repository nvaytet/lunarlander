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


class Terrain:
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
        img = Image.open(config.resources / f"lunar-surface.png")
        if (img.width != config.nx) or (img.height != config.ny):
            img = img.resize((config.nx, config.ny))
        img = img.convert("RGBA")
        data = img.getdata()
        self.raw_background = (
            np.array(data).reshape(img.height, img.width, 4).astype(np.uint8)
        )
        self.current_background = self.raw_background.copy()
        self.y_map = np.broadcast_to(
            config.ny - np.arange(config.ny).reshape(config.ny, 1),
            (config.ny, config.nx),
        )

        self.update_background(0, config.nx)
        self.background_image = self.terrain_to_image()

    def update_background(self, start: int, end: int):
        # self.array = np.zeros([config.ny, config.nx])
        # y = np.arange(config.ny).reshape(config.ny, 1)
        sl = slice(start, end)
        raw = self.raw_background[:, sl]
        # mask = np.ones([config.ny, end - start])
        mask = (self.y_map[:, sl] < self.terrain[sl]).astype(int)
        mask = mask.reshape(mask.shape + (1,))
        # print(mask.shape, hide.shape)
        # mask[hide] = 0
        # print("self.current_background[sl].shape", self.current_background[sl].shape)
        # print("raw.shape", raw.shape)
        # print("mask.shape", mask.shape)

        self.current_background[:, sl] = raw * mask

    def make_crater(self, x: int):
        r = config.crater_radius
        self.terrain[x - r : x + r] = float(self.terrain[x])
        self.update_background(x - r, x + r)
        self.background_image = self.terrain_to_image()

    def terrain_to_image(self):
        # self.array = np.zeros([config.ny, config.nx])
        # y = np.arange(config.ny).reshape(config.ny, 1)
        # sel = self.y_map < self.terrain
        # self.array[sel] = 1

        # img = img.convert("RGBA")
        # data = img.getdata()
        # arr = np.flipud(np.array(data).reshape(img.height, img.width, 4))
        # arr = self.raw_background.copy()
        # arr[~sel] *= 0
        # img = Image.fromarray(np.flipud(arr).astype(np.uint8))
        img = Image.fromarray(self.current_background)
        return pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
