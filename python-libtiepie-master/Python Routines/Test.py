from __future__ import print_function
import libtiepie
import time
import matplotlib.pyplot as plt
import os
import sys

import numpy as np
import MiraexLib.plot as miraex_plt
import MiraexLib.misc as miraex_misc
import MiraexLib.analysis as miraex_anls
from MiraexLib.printinfo import*
#from cubini.KPZ101 import KPZ101
from cubini.KPZ101 import KPZ101


def main():
    # %% Generic
    name = 'MY BIG NAME'
    print(name)

    # list of serial numbers
    cuboids = [0,29250837,0,0]

    # connect to all modules
    cubinis = []

    for i, sn in enumerate(cuboids):

        print('serial number ', sn)
        print('iteration : ', i)
        myCube = KPZ101(serial_number=sn)
        time.sleep(0.5)

        print(myCube)

        if myCube is None :
            pass

        else :
            myCube.set_input_mode()
            cubinis.append(myCube)
            #print('KPZ101 {} found.'.format(myCube.device_unit_sf))


if __name__ == "__main__":
    main()
