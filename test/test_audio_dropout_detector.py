from src import audio_dropout_detector
import os

# Set a couple different positive and negative cases
AUDIO_FILES = os.path.abspath(os.path.join(os.path.dirname(__file__), 'audio'))

NEG_INFILES = ['ThisIsAmerica_negative_1.wav',
               'ThisIsAmerica_negative_2.wav']
POS_INFILES = ['Audio_With_Gap_768.wav',
               'Audio_with_Gap_20.wav']
DEBUG = False


class TestDropoutDetector:

    def test_dropout_pos_768_128(self):
        """
        This test takes the positive file with a gap of 768 samples and asserts that the analyzer
        returns the bool value for 'contains_dropouts'
        :return:
        """
        print('TEST: dropout pos 768 window=128')
        samplefreq, stereo_array, mon_array, filename = audio_dropout_detector.read_wav(os.path.join(AUDIO_FILES,
                                                                                                     POS_INFILES[0]))
        print('{0} sampling frequency of {1}/sec\n'.format(filename, samplefreq))

        window, threshold = 128, 10
        contains_dropouts, plot_start, plot_end = audio_dropout_detector.analyzer(mon_array, window=window,
                                                                                  threshold=threshold)
        # If it did contain dropouts, let's plot the problem area for subjective analysis
        assert contains_dropouts, 'Error: {0} was reported NOT to have dropouts with a window of: {1} and threshold of {2}'.format(
                                                                                                    filename, window, threshold)
        if DEBUG:  # The plotting is slow so let's only plot in unittest when debugging
            if contains_dropouts:
                print('The file contains dropouts: {0}\nplot_area: {1}-{2}'.format(contains_dropouts, plot_start, plot_end))
                audio_dropout_detector.plot_problem_area(stereo_array, filename, plot_start, plot_end)

    def test_dropout_pos_20_8(self):
        """
        This test takes the positive file with a gap of 20 samples and asserts that the analyzer
        returns the bool value for 'contains_dropouts'
        :return:
        """
        print('TEST: dropout pos 20 window=8')
        samplefreq, stereo_array, mon_array, filename = audio_dropout_detector.read_wav(os.path.join(AUDIO_FILES,
                                                                                                     POS_INFILES[1]))
        print('{0} sampling frequency of {1}/sec\n'.format(filename, samplefreq))

        window, threshold = 8, 10
        contains_dropouts, plot_start, plot_end = audio_dropout_detector.analyzer(mon_array, window=window,
                                                                                  threshold=threshold)
        # If it did contain dropouts, let's plot the problem area for subjective analysis
        assert contains_dropouts, 'Error: {0} was reported NOT to have dropouts with a window of: {1} and threshold of {2}'.format(
                                                                                                        filename, window, threshold)
        if DEBUG:  # The plotting is slow so let's only plot in unittest when debugging
            if contains_dropouts:
                print('The file contains dropouts: {0}\nplot_area: {1}-{2}'.format(contains_dropouts, plot_start, plot_end))
                audio_dropout_detector.plot_problem_area(stereo_array, filename, plot_start, plot_end)

    def test_dropout_neg_1_64(self):
        """
        This test takes a negative file with no gaps, but periods of near silence, with a window of 64 samples
        :return:
        """
        print('TEST: dropout neg_1 window=64')
        # Read in the wav file and get the samplerate, numpy array, and filename
        samplefreq, _, mon_array, filename = audio_dropout_detector.read_wav(os.path.join(AUDIO_FILES, NEG_INFILES[0]))
        print('{0} sampling frequency of {1}/sec\n'.format(filename, samplefreq))

        window, threshold = 64, 10
        contains_dropouts, plot_start, plot_end = audio_dropout_detector.analyzer(mon_array, window=window,
                                                                                  threshold=threshold)
        # If it did contain dropouts, let's plot the problem area for subjective analysis
        assert not contains_dropouts, 'Error: {0} was reported to have dropouts with a window of: {1} and threshold of {2}'.format(
            filename, window, threshold)
        print('No dropouts were found in: {0}'.format(filename))

    def test_dropout_neg_2_32(self):
        """
        This test takes a negative file with no gaps, but periods of near silence, with a window of 8 samples
        :return:
        """
        print('TEST: dropout neg_2 window=32')
        # Read in the wav file and get the samplerate, numpy array, and filename
        samplefreq, _, mon_array, filename = audio_dropout_detector.read_wav(os.path.join(AUDIO_FILES, NEG_INFILES[1]))
        print('{0} sampling frequency of {1}/sec\n'.format(filename, samplefreq))

        window, threshold = 32, 10
        contains_dropouts, plot_start, plot_end = audio_dropout_detector.analyzer(mon_array, window=window,
                                                                                  threshold=threshold)
        # If it did contain dropouts, let's plot the problem area for subjective analysis
        assert not contains_dropouts, 'Error: {0} was reported to have dropouts with a window of: {1} and threshold of {2}'.format(
            filename, window, threshold)
        print('No dropouts were found in: {0}'.format(filename))

