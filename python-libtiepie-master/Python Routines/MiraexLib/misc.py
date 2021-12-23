# -*- coding: utf-8 -*-
"""
Created on Wednesday 16.11.2021 at 09:23

Miraex - Miscellaneous Routines

@author: Claudio Jaramillo
"""

import os
import datetime
import sys
import tkinter as tk
from tkinter import filedialog


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


def CreateFileName(FileName: str, FileType: str):
    # Careful here ! The 'exports' dir is manually set depending on the repo structure.
    # It would be useful to create some sort of JSON file giving the path required.

    file_type_raw = ['txt', 'csv', 'json']
    file_type_fig = ['jpg', 'jpeg', 'png']

    if FileType not in (file_type_raw+file_type_fig):
        assert('INVALID FILE TYPE (try removing a dot)')

    # datetime object containing current date and time
    now = datetime.datetime.now()
    # dd-mm-YY_H-M-S
    dt_string = now.strftime("%d-%m-%Y_%H-%M-%S")

    # creation of save path and stuff
    save_name = FileName+'__'+dt_string+'.'+FileType
    save_file = save_name

    return save_file


def CreateWriteDir(DataType: str):

    allowed_types = ['raw', 'figure']

    if DataType not in allowed_types:
        assert('ERROR : DataType must be "raw" or "figure".')

    # Write directory within the repo
    if DataType == 'raw':
        writeDir_in_repo = '\\exports\\raw-data\\'
    elif DataType == 'figure':
        writeDir_in_repo = '\\exports\\figures\\'

    # Get repo path
    myPath = os.getcwd()
    writeDir = myPath + writeDir_in_repo

    return writeDir


def OpenFileDialog():

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()

    return file_path
