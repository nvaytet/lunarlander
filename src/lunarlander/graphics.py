# SPDX-License-Identifier: BSD-3-Clause

import datetime
import pyglet

import numpy as np

from . import config
from .tools import text_to_image


class Graphics:
    def __init__(self, game_map, fullscreen: bool = False):
        self.window = pyglet.window.Window(
            config.nx + config.scoreboard_width,
            config.ny,
            caption="Lunar Lander",
            fullscreen=fullscreen,
            resizable=not fullscreen,
        )

        self.game_map = game_map
        self.star_batch = pyglet.graphics.Batch()
        self.background_batch = pyglet.graphics.Batch()
        self.main_batch = pyglet.graphics.Batch()
        self.time_label = pyglet.sprite.Sprite(
            img=text_to_image(
                "Time left:", width=100, height=24, font=config.large_font
            ),
            x=config.nx + 20,
            y=config.ny - 30,
            batch=self.main_batch,
        )
        self.time_left = None
        self.exit_message = None
        self.make_stars()

        @self.window.event
        def on_draw():
            self.window.clear()
            self.game_map.background_image.get_texture().blit(0, 0)
            self.star_batch.draw()
            self.background_batch.draw()
            self.main_batch.draw()

    def make_stars(self):
        # star_image = pyglet.image.load(config.resources / f"star.png")
        self.stars = []
        self.star_t0 = np.random.uniform(0, config.twinkle_period, config.nstars)
        xstar = np.random.uniform(0, config.nx, config.nstars)
        ystar = np.random.uniform(0, config.ny, config.nstars)
        for x, y in zip(xstar, ystar):
            self.stars.append(
                pyglet.shapes.Circle(
                    x, y, 1, color=(255, 255, 255, 255), batch=self.star_batch
                )
                # pyglet.sprite.Sprite(img=star_image, x=x, y=y, batch=self.star_batch)
            )

    def update_stars(self, t):
        for star, t0 in zip(self.stars, self.star_t0):
            star.opacity = int(
                255
                * np.sin(
                    np.pi * ((t % config.twinkle_period) - t0) / config.twinkle_period
                )
                ** 2
            )

    def update_scoreboard(self, t: float):
        if self.time_left is not None:
            self.time_left.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        self.time_left = pyglet.sprite.Sprite(
            img=text_to_image(t_str, width=100, height=24, font=config.large_font),
            x=self.time_label.x + 90,
            y=self.time_label.y,
            batch=self.main_batch,
        )

    def show_exit_message(self):
        self.exit_message = pyglet.text.Label(
            "Press ESC to exit",
            color=(153, 51, 153, 255),
            font_size=80,
            x=config.nx * 0.5,
            y=config.ny * 0.5,
            batch=self.main_batch,
            anchor_x="center",
            anchor_y="center",
        )
