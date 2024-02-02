# SPDX-License-Identifier: BSD-3-Clause

import glob
import importlib

import lunarlander

bots = []
for repo in glob.glob("*_bot"):
    module = importlib.import_module(f"{repo}")
    bots.append(module.Bot())

extras = ["Andrew", "Janice", "Katie", "David", "Jenny", "Martin"]

for i, name in enumerate(extras):
    extra_bot = module.Bot()
    extra_bot.team = name
    extra_bot.avatar = i + 1
    bots.append(extra_bot)

lunarlander.play(
    bots=bots,  # List of bots to use
    manual=False,  # Set to True to play manually using the keyboard arrow keys
    crater_scaling=1.0,  # Artificially increase the size of craters
    player_collisions=True,  # Set to False to disable collisions between players
    asteroid_collisions=True,  # Set to False to disable being destroyed by asteroids
    speedup=1.0,  # Increase to speed up the game (no guarantees this works very well)
    test=True,  # Set to True to run in test mode
)
