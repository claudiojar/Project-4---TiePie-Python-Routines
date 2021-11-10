# python-libtiepie
[![Build Status](https://travis-ci.org/TiePie/python-libtiepie.svg?branch=master)](https://travis-ci.org/TiePie/python-libtiepie)
[![PyPI](https://img.shields.io/pypi/v/python-libtiepie.svg)](https://pypi.org/project/python-libtiepie/)
[![License](https://img.shields.io/github/license/tiepie/python-libtiepie.svg)](LICENSE)

Python bindings for [LibTiePie SDK](https://www.tiepie.com/node/930). The LibTiePie SDK is a library to easily interface with TiePie engineering [USB oscilloscopes](https://www.tiepie.com/node/4). Using the LibTiePie SDK the user has full control over all aspects of the USB oscilloscope and can perform measurements easily on Windows and Linux. Examples for different measurements are available to get started easily.

## Installation

### Windows

To install the Python bindings for LibTiePie and examples on Windows:

1. Install the Python bindings by executing `pip install python-libtiepie`
2. Download the [python-libtiepie examples](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/TiePie/python-libtiepie/tree/master/examples).
3. Unpack them using an extractor.
4. Connect your [USB oscilloscope](https://www.tiepie.com/node/4).
5. Run an example by executing e.g. `python OscilloscopeBlock.py`

### Linux

To install the Python bindings for LibTiePie and examples on Linux:

1. Ensure that [LibTiePie for Linux](https://www.tiepie.com/node/1016) is installed.
2. Install the Python bindings by executing `sudo pip install python-libtiepie`
3. Download the [python-libtiepie examples](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/TiePie/python-libtiepie/tree/master/examples).
4. Unpack them using an extractor, or run in the console using `unzip`.
5. Connect your [USB oscilloscope](https://www.tiepie.com/node/4).
6. Run an example by executing e.g. `python OscilloscopeBlock.py`

## Examples

See the [examples directory](examples).
