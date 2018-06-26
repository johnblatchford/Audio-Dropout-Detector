""" audio dropout detector
    John Blatchford - listening@mac.com
    Final project for COMPSCI X433.3 - Python for Data Analysis and Scientific Computing
"""
from scipy.io import wavfile
import pylab as plb
import numpy as np
import argparse
import os
import random
import errno
import logging
import warnings

# GLOBALS
POSITIVE = random.choice([True, False])

# Set a couple different positive and negative cases to be chosen at random at runtime
AUDIO_FILES = os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'test', 'audio'))

NEG_INFILES = ['ThisIsAmerica_negative_1.wav',
               'ThisIsAmerica_negative_2.wav']
POS_INFILES = ['Audio_With_Gap_768.wav',
               'Audio_with_Gap_20.wav']


# Setup logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


# Define all of the utility methods
def convert_to_dbfs(x):
    """
    Converts raw np.array sample value to dbFS
    :param x: np.array value
    :return: dbFS value
    """
    return 20 * np.log10(x)


def rms(samples):
    """
    performs simple RMS over a range of samples
    :param samples: a window of samples to process
    :return: RMS value
    """
    rms = np.sqrt(np.mean(samples**2))
    # Have to account for NaN
    if np.isnan(rms):
        return np.nan
    else:
        return np.round(convert_to_dbfs(rms), 1)


def read_wav(infile):
    """
    Takes in a broadcast .wav file and creates
    the intermediate file for processing/analyzing
    :param infile: .wav file
    :return: samplerate, stereo_array, mono_array, filename
    """
    filename = os.path.basename(infile)
    print('Reading in: {0} ...'.format(filename))
    samplerate, st_array,  = wavfile.read(infile)
    mono_array = st_array.sum(axis=1) / 2
    return samplerate, st_array, mono_array, filename


def analyzer(a, window=64, threshold=10):
    """
    Does most of the heavy lifting.  Should convert this to a generator
    and do the rms and comparison in a separate function
    :param a: the input file ndarray
    :param window: the size of the analyzer window
    :param threshold: the threshold to trigger dropout detection
    :return: contains_dropouts, plot_start, plot_end
    """
    offset = 0
    rms_val_list = []  # Keep a running tally for min() and max() calculations
    offending_offsets = []  # collect the offsets where dropouts occur
    contains_dropouts = False  # if swapped to True, triggers the plotting mechanism

    #  Iterate over the file a window size at a time and call rms() to analyze for dropouts
    for idx, sample in enumerate(a):
        chunk = a[offset + 1:offset + window]
        offset = offset + window
        if not all(np.isfinite(chunk)):
            logger.debug('... no more chunks')
            break
        else:
            with warnings.catch_warnings():  # will return an odd RuntimeWarning if not used. clutters console output
                warnings.simplefilter("ignore", category=RuntimeWarning)
                rms_val = (rms(chunk))
                logger.debug('Chunk: {0}RMS: {1}'.format(idx, rms_val))
                rms_val_list.append(rms_val)
                if np.isnan(rms_val):  # must account for NaN when we reach an empty array element and try to run rms()
                    logger.debug('NaN detected at {0}'.format(idx))
                    break
                if rms_val < threshold:  # If the rms(chunk) value is less than the threshold, send to offenders list
                    offending_offsets.append(offset)
                    print('possible dropout between samples: {0} - {1}\nrms for chunk {2}: {3}'.format(
                                                                            offset, offset + window, idx, rms(chunk)))
                    contains_dropouts = True  # Flip the bool to indicate plotting is needed
    #  Show the min and max for the file for information sake
    print('max rms: {0}\nmin rms: {1}\n'.format(max(rms_val_list), min(rms_val_list)))
    logger.debug('max rms: {0}\nmin rms: {1}\n'.format(max(rms_val_list), min(rms_val_list)))

    if not offending_offsets:  # Use arbitrary values to return if no dropouts were encountered
        plot_start = 0
        plot_end = len(a)
    else:
        plot_start = min(offending_offsets)
        plot_end = max(offending_offsets)
    return contains_dropouts, plot_start, plot_end


def plot_problem_area(array, filename, start_sample, end_sample):
    """
    Plots the area that was found during detection
    :param start_sample: beginning of the problem area
    :param end_sample: end of the problem area
    :return: plot.show()
    """
    #  Plot 1 - The time domain waveform view that is instantly recognizable
    plb.figure('Artifact Overview:', figsize=(8, 6), dpi=100)
    plb.style.use('ggplot')
    plb.subplot2grid((3, 1), (0, 0), colspan=1, rowspan=2)
    # Only plot the slice of audio the dropouts occur in
    plb.plot(array[start_sample - 1000:end_sample + 1000], label='channel')
    plb.title('Time domain:\n')
    plb.ylabel("Threshold of: {0}dbFS".format(convert_to_dbfs(10)))
    plb.yscale('linear')
    plb.xlabel("From sample: {0} to sampale: {1} ".format(start_sample, end_sample))
    fig1 = plb.gca()
    fig1.axes.xaxis.set_ticklabels([])
    fig1.axes.yaxis.set_ticklabels(range(-100, 100, 20))
    plb.legend(loc='lower right')
    plb.grid(True)
    #  Render this clip to disk for subjective analysis in the output/ directory and label as an artifact
    wavfile.write('output/{0}_artifact.wav'.format(filename),
                  rate=48000, data=array[start_sample - 48000:end_sample + 48000])
    #  Plot 2 - the FFT of the waveform decomposed into it's parts
    plb.subplot2grid((3, 1), (2, 0), colspan=1, rowspan=1)
    plb.title('Frequency domain:')
    x = array[start_sample - 1000:end_sample + 1000]
    fft = abs(np.fft.rfft(x))
    plb.plot(fft, label='channel')
    plb.xscale('symlog')
    plb.xlabel('frequency [Hz]')
    plb.yscale('linear')
    plb.ylabel('amplitude')
    plb.legend(loc='upper left')
    plb.tight_layout()

    #  Save an image of the plot alongside the wav file
    plb.savefig('output/{0}_artifact.png'.format(filename))
    #  Display the plot.
    plb.show()

    return None


if __name__ == '__main__':
    '''  I had planned on using a package called 'begins' that was going to boilerplate 
         the argparse() and input handling. It did not work out as you can see.'''

    #  Set up argparse with the input params needed for user input
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help='The input file for processing')
    parser.add_argument('-t', help='Threshold for detection. default 10 (0-100)', type=int)
    parser.add_argument('-w', help='The window/chunk size for analyzing the file. '
                                   'hint: smaller windows are preferred', type=int)
    parser.add_argument('-log', default='warning', choices=['debug', 'info', 'warning', 'error'],
                        help="logging level (defaults to 'warning')")
    args = parser.parse_args()
    logging.basicConfig(level=getattr(logging, args.log.upper(), None),
                        format='%(levelname)s: %(message)s')
    if args.i:
        if os.path.isfile(args.i):
            input_wav = args.i
        else:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), os.path.realpath(args.i))
    else:
        if POSITIVE:
            input_wav = os.path.join(AUDIO_FILES, random.choice(POS_INFILES))
        else:
            input_wav = os.path.join(AUDIO_FILES, random.choice(NEG_INFILES))
        print('POSITIVE = {1} \nUsing the default: {0} \nNo user wav file was passed using --i'.format(
                                                                                os.path.basename(input_wav), POSITIVE))
    if args.t:
        input_threshold = args.t
    else:
        input_threshold = 10
        print('Using default threshold of: {0}\n'.format(input_threshold))
    if args.w:
        input_window_size = args.w
    else:
        input_window_size = 256
        print('Using default window size of: {0}'.format(input_window_size))

    # FUNCTION CALLS

    # Read in the wav file and get the samplerate, numpy array, and filename
    samplefreq, stereo_array, mon_array, filename = read_wav(input_wav)
    print('{0} sampling frequency of {1}/sec'.format(filename, samplefreq))

    # Now we'll take the converted mono array and anylize it for dropouts
    contains_dropouts, plot_start, plot_end = analyzer(mon_array, window=input_window_size, threshold=input_threshold)
    # If it did contain dropouts, let's plot the problem area for subjective analysis
    if contains_dropouts:
        print('The file contains dropouts: {0}\nplot_area: {1}-{2}'.format(contains_dropouts, plot_start, plot_end))
        # Plot the dropout range
        plot_problem_area(stereo_array, filename, plot_start, plot_end)
    else:
        print('No dropouts were found in: {0}'.format(filename))
