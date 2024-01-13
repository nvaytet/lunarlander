# SPDX-License-Identifier: BSD-3-Clause

import importlib_resources as ir
import numpy as np
from matplotlib import font_manager
from PIL import ImageFont


class Config:
    def __init__(self):
        self.scoreboard_width = 200
        self.fps = 30
        self.resources = ir.files("lunarlander") / "resources"
        self.avatar_size = (25, 25)
        file = font_manager.findfont("sans")
        self.small_font = ImageFont.truetype(file, size=10)
        self.large_font = ImageFont.truetype(file, size=16)
        self.medium_font = ImageFont.truetype(file, size=12)
        self.nx = 1920 - self.scoreboard_width
        self.ny = 1080
        self.time_limit = 60 * 5
        self.gravity = np.array([0, -1.62])  # m/s^2
        self.lem_mass = 1  # kg
        self.thrust = np.abs(self.gravity[1]) * 3  # N
        self.rotation_speed = 15.0
        self.max_landing_speed = 5.0
        self.max_landing_angle = 5.0
        self.max_fuel = 3000
        self.main_engine_burn_rate = 5
        self.rotation_engine_burn_rate = 2
        self.asteroid_delay = 5.0
        self.crater_radius = self.avatar_size[0] // 2 - 1
        self.collision_radius = self.avatar_size[0] * 0.5 * np.sqrt(2)
        self.twinkle_period = 4.0
        self.nstars = 500
