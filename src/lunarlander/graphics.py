# SPDX-License-Identifier: BSD-3-Clause

import datetime
from typing import Any

import pyglet

from . import config
from .tools import text_to_image


class Graphics:
    def __init__(self, engine: Any, fullscreen: bool):
        self.engine = engine

        self.window = pyglet.window.Window(
            int((config.nx * config.scaling) + config.scoreboard_width),
            int(config.ny * config.scaling),
            caption="Supremacy",
            fullscreen=fullscreen,
            resizable=not fullscreen,
        )

        self.background = self.engine.game_map.background_image.get_texture()
        self.main_batch = pyglet.graphics.Batch()
        self.time_label = pyglet.sprite.Sprite(
            img=text_to_image(
                "Time left:", width=100, height=24, scale=False, font=config.medium_font
            ),
            x=(config.nx * config.scaling) + 20,
            y=(config.ny * config.scaling) - 30,
            batch=self.main_batch,
        )
        self.time_left = None
        self.exit_message = None

        self.scoreboard_labels = []

        @self.window.event
        def on_draw():
            self.window.clear()
            self.background.blit(0, 0)
            self.main_batch.draw()

        @self.window.event
        def on_key_release(symbol, modifiers):
            if symbol == pyglet.window.key.P:
                self.engine.paused = not self.engine.paused

    def update_scoreboard(self, t: float):
        if self.time_left is not None:
            self.time_left.delete()
        t_str = str(datetime.timedelta(seconds=int(t)))[2:]
        self.time_left = pyglet.sprite.Sprite(
            img=text_to_image(
                t_str, width=100, height=24, scale=False, font=config.medium_font
            ),
            x=self.time_label.x + 60,
            y=self.time_label.y,
            batch=self.main_batch,
        )

    def show_exit_message(self):
        self.exit_message = pyglet.text.Label(
            "Press ESC to exit",
            color=(0, 0, 0, 255),
            font_size=80,
            x=config.nx * 0.5,
            y=config.ny * 0.5,
            batch=self.main_batch,
            anchor_x="center",
            anchor_y="center",
        )
