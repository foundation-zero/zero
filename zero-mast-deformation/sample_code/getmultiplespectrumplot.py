#! /usr/bin/env python
#
#getspectrumandpeaksplot.py
#
#Copyright (c) 2018 by Micron Optics, Inc.  All Rights Reserved
#
"""This example will plot a spectrum and the corresponding peaks.  This
requires numpy, and matplotlib packages.
"""
import matplotlib
matplotlib.use('tkagg')
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

import sys

import hyperion


h1 = hyperion.Hyperion('10.0.10.71')

#Get the spectrum

h1.active_full_spectrum_channel_numbers = range(1, h1.channel_count + 1)

fig = plt.figure()
ax = plt.subplot(111)
spectra = h1.spectra
wavelengths = spectra.wavelengths

for channel in h1.active_full_spectrum_channel_numbers:
    ax.plot(wavelengths, spectra[channel], label = str(channel))

ax.legend()


ax.set_xlabel('Wavelength (nm)')
ax.set_ylabel('Amplitude (dBm)')
plt.show()
