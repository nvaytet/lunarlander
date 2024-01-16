# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import lunarlander

bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

# extra_bot = module.Bot()
# extra_bot.team = "Andrew"
# bots.append(extra_bot)

start = None

lunarlander.play(
    bots=bots,  # List of bots to use
    manual=True,  # Set to True to play manually
    crater_scaling=2.0,  # Artificially increase the size of craters
    player_collisions=True,  # Set to False to disable collisions between players
    asteroid_collisions=False,  # Set to False to disable being destroyed by asteroids
    test=False,
)
