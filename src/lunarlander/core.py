from dataclasses import dataclass


@dataclass
class Instructions:
    """
    Instructions for the lander.
    """

    left: bool = False
    right: bool = False
    main: bool = False
