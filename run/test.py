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
    bots=bots[1:],  # List of bots to use
    manual=False,  # Set to True to play manually
    crater_scaling=1.0,  # Artificially increase the size of craters
    test=False,
)
