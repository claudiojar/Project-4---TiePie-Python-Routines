# -*- coding: utf-8 -*-
"""
Created on Wednesday 16.11.2021 at 09:23

Miraex - Miscellaneous Routines

@author: Claudio Jaramillo
"""

import os


def getParent(path, levels=1):
    """
    Fetches the parent(s) directory(ies) to the location passed in the path variable.

    param path : the path to which we want to find the parent directories.

    param levels (default = 1) : how many up levels we want to obtain parent directories from.
    """
    common = path

    # Using for loop for getting
    # starting point required for
    # os.path.relpath()
    for i in range(levels + 1):

        # Starting point
        common = os.path.dirname(common)

    # Parent directory upto specified
    # level
    return os.path.relpath(path, common)


def fprint(param):
    print(f'{param = }')
