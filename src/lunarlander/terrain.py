# SPDX-License-Identifier: BSD-3-Clause

import numpy as np
from PIL import Image
import pyglet
from scipy.ndimage import gaussian_filter

from . import config


class Terrain:
    def __init__(self):
        profile = np.zeros([config.nx])
        nseeds = 100
        xseed = np.random.randint(config.nx, size=nseeds)
        profile[xseed] = 10000 * np.random.random(nseeds)
        self.smooth = gaussian_filter(profile, sigma=30, mode="wrap")
        self.terrain = self.smooth.copy()

        img = Image.open(config.resources / f"lunar-surface.png")
        if (img.width != config.nx) or (img.height != config.ny):
            img = img.resize((config.nx, config.ny))
        img = img.convert("RGBA")
        data = img.getdata()
        self.raw_background = (
            np.array(data).reshape(img.height, img.width, 4).astype(np.uint8)
        )
        self.current_background = np.full(
            (config.ny, config.nx + config.scoreboard_width, 4), 20, dtype=np.uint8
        )
        self.current_background[..., 3] = 255
        self.current_background[:, : config.nx, :] = self.raw_background
        # self.current_background = self.raw_background.copy()
        self.y_map = np.broadcast_to(
            config.ny - np.arange(config.ny).reshape(config.ny, 1),
            (config.ny, config.nx),
        )

        self.update_background(slice(0, config.nx))
        self.background_image = self.terrain_to_image()

    def update_background(self, sl: slice) -> None:
        # sl = slice(start, end)
        raw = self.raw_background[:, sl]
        mask = (self.y_map[:, sl] < self.terrain[sl]).astype(int)
        mask = mask.reshape(mask.shape + (1,))
        self.current_background[:, sl] = raw * mask

    def make_crater(self, x: int) -> None:
        r = config.crater_radius
        slices = []
        start = x - r
        end = x + r
        if start < 0:
            slices.append(slice(start, None))
            start = 0
        if end > config.nx:
            slices.append(slice(None, end - config.nx))
            end = config.nx
        slices.append(slice(start, end))
        for sl in slices:
            self.terrain[sl] = float(self.terrain[x])
            self.update_background(sl)
        self.background_image = self.terrain_to_image()

    def terrain_to_image(self) -> Image:
        img = Image.fromarray(self.current_background)
        return pyglet.image.ImageData(
            width=img.width,
            height=img.height,
            fmt="RGBA",
            data=img.tobytes(),
            pitch=-img.width * 4,
        )
