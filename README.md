# MIRAEX Project 4 : TiePie Python Routines
### Python and MATLAB routines used for interfacing with a TiePie oscilloscope/arbitrary function generator

---

## Checklist before usage :

 * Import and activate the latest conda environment found under : `\env`

 * To execute the Python scripts navigate to : `\python-libtiepie-master\Python Routines`
 * To view the equivalent MATLAB routines navigate to : `\matlab-libtiepie-master\Reference MATLAB Files`

## Special dependencies

### All scripts
All scripts depend on the `libtiepie` SDK provided for free at : [LibTiePie](https://www.tiepie.com/en/libtiepie-sdk). Before using the LibTiePie SDK it is required to install the drivers found at : https://www.tiepie.com/en/download

### Fiber Characterisation script

This script depends on the [Cubini library](https://github.com/Schlabonski/cubini).

To install follow the steps in the READ ME of the repo.

If the line :

    python3 setup.py install

fails, try using :

    python setup.py install

For this script to work properly, the libraries :
 - PyUSB
 - LibUSB

Need to be installed.

Install them both first by using :

    conda install -c conda-forge pyusb
    conda install -c conda-forge libusb

from the anaconda cmd line after having activated the relevant environment.

> Environment Miraex_2021_12_01 is the earliest to have this dependency installed.

Then, go to : https://github.com/libusb/libusb/releases/tag/v1.0.24

Download the zip file, and open it.

Unzip using 7zip into a temp dir.

If on 64-bit Windows, copy

    MinGW64\dll\libusb-1.0.dll

into

    C:\windows\system32

If on 32-bit windows, copy

    MinGW32\dll\libusb-1.0.dll

into

    C:\windows\SysWOW64.

This should solve the ''No backend available'' exepction raised at init of the cuboids.

## Known problems
### Fiber Characterisation

* Known problem in the `KPZ101.py` script : the `__del__(self)` method calls for `#self.com.disconnect()` which calls `self.device.attach_kernel_driver(0)` in `vcp_terminal.py` which calls `self._ctx.backend.attach_kernel_driver()` in `core.py`. The `attach_kernel_driver()` method is not implemented in the `core.py` and raises a `Not_Implemented` exception when called.\
This bug could be solved by updating the `core.py` build to a newer build in which the method is implemented. But we have not found a way to try and test this.

* If we set a given output voltage before setting the maximum voltage the script can potentially crash.