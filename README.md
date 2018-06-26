### Audio Dropout Detector 
##### Required README quiestions
1. What platform/system and Python version you used to run your code:

    `Project was created in macOS 10.12.6 / Python 3.6.3 / PyCharmCE 2018.1 / pyenv-virtualenv`

2. What packages and dependencies you used:

    `package dependencies: numpy, scipy, matplotlib, pytest(for unittests)`

    `built-in packages used: argparse, os, random, errno, warnings, logging(for debugging)`

3. The sequence of how your code needs to be executed:

        $ python audio_dropout_detector.py -i "/path/to/audio/file.wav" -w 256 -t 10

        -w = window = the amount of samples in each analyzer window
        -t = threshold = the threshold to flag as a possible dropout

#### QuickStart using the included test files:
    $ cd Audio-Dropout-Detector
    $ python audio_dropout_detector.py -i "../test/audio/Audio_With_Gap_768.wav" -w 256 -t 10
_This will use a file with a known gap of 768 samples, window value of 256 and threshold of 10_

    $ python audio_dropout_detector.py -i "../test/audio/Audio_With_Gap_20.wav" -w 8 -t 10
_This will use a file with a known gap of 20 samples, window value of 8 and threshold of 10_

    $ python audio_dropout_detector.py -i "../test/audio/ThisIsAmerica_negative_1.wav" -w 64 -t 10
_This will use a file with no gaps, but very silent passages, the script will report no dropouts_

    $ python audio_dropout_detector.py -i "../test/audio/ThisIsAmerica_negative_2.wav" -w 32 -t 20
_This will use a different file with no gaps, but similar silent passages, the script will report no dropouts_

    $ python audio_dropout_detector.py -w 64 -t 10
_Not specifying an input file will cause the script to randomly choose one of the 4 test files (2 positive, 2 negative)

#### Basis:
Audio engineers that produce multi-channel wav files sometimes need a way to quickly verify that the file they have 
rendered/processed is valid. Sometimes the engineer has to process the file offline 
_(meaning they are not monitoring the mix which is the default QA process for audio mixing)_

The most common artifacts encountered are dropouts or glitches. These types of artifacts can be the result of many things.
I/o buffering problems due to disk speed, hasty region edits with no cross-fade, and plug-in processing issues to name a few.   

#### so

I would like to have a script that processes and analyzes a wav file on disk by taking a rolling RMS calculation, 
if it detects a sharp change in amplitude the window could contain potential dropout or glitch.



#### Effort: 
Create a module (audio_dropout_detector.py) that takes in a wav file and analyzes it for dropouts. 
It does this by taking a window of samples (_default=64_, _overrideable_), calculating an RMS value 
(accounting for NaN which is expected for dropouts)

    def rms(samples):
        rms = np.sqrt(np.mean(samples**2))
        if np.isnan(rms):
            return np.nan
        else:
            return np.round(convert_to_dbfs(rms), 1)  

then converting to dbFS to compare:    

    def convert_to_dbfs(x):
        return 20 * np.log10(x)
If a dropout is detected the analyzer will return some information about the file like:
1. The sample rate of the input file for processing
2. If a dropout was detected based on the moving rms window method using the bool: 'contains-dropouts'
3. The starting offset sample of the block(s) a dropout was contained in 
   (for a glitch that spans multiple blocks we can also use the last block's offset + the window to give us the end sample)

The script then creates a plot of the surrounding blocks that the dropouts were detected in for analysis
  
    plot_area = 1000 samples + dropout chunks + 1000 samples 

Along with the plot, the script will create a wav file rendering that corresponds to the plot area.

_(I pad the glitch with 1 second of pre and post roll for context)_

    wavfile.write('output/{0}_artifact.wav'.format(filename), 
                   rate=48000, data=stereo_array[sample_start - 48000:sample_end + 48000])
###### Dependencies:
    - python: 3.6.3
    - numpy, scipy, matplotlib, pylab

#### Commandline Usage:
    usage: audio_dropout_detector.py [-h] [-i I] [-t T] [-w W]
                                     [-log {debug,info,warning,error}]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i I                  The input file for processing
      -t T                  Threshold for detection. default 10 (0-100)
      -w W                  The window/chunk size for analyzing the file. 
                            hint: smaller windows are preferred
                            
      -log {debug,info,warning,error}
                            logging level (defaults to 'warning')

#### Module Usage:
Import the module:

    import audio_dropout_detector
Read in the desired wav file under test with the read_wav() function:    

    sample_rate, stereo_audio, mono_audio, filename = audio_dropout_detector.read_wav(input_wav_file)
Now take the mono_audio provided by the wav reader and supply the 
window and threshold parameters to the analyzer() function:

    contains_dropouts, dropout_start, dropout_end = audio_dropout_detector.analyzer(mono_audio, window=32,
                                                                                             threshold=10)
If the 'contains_dropouts' bool is 'True', 
you can use the 'dropout_start' and 'dropout_end' values for the plot_problem_area() function:

            if contains_dropouts:
                audio_dropout_detector.plot_problem_area(stereo_audio, 
                                                         filename, 
                                                         (dropout_start - 48000), 
                                                         (dropout_end + 48000)
_(Note: that supplying a buffer of 48000 samples in either direction allows for 2 full seconds of context around the possible dropout)_
#### Tests:
###### using pytest: 
    
    $ cd audio_dropout_detector/test/
    
    $ py.test test_audio_dropout_detector.py
    
    ===================================== test session starts ============================================
    platform darwin -- Python 3.6.3, pytest-3.6.2, py-1.5.3, pluggy-0.6.0
    rootdir: /Users/jeblat/PycharmProjects/COMPSCI/Audio Dropout Detector/audio dropout detector, inifile:
    collected 4 items                                                                               
                                                                                                    [100%]
    test_audio_dropout_detector.py ....
    
###### Test using traditional positional arguments and test files:
    
    $ cd audio_dropout_detector/src/
    
    $ python audio_dropout_detector.py -i "../test/audio/Audio_With_Gap_768.wav" -w 256 -t 10
_This will use a file with a known gap of 768 samples, window value of 256 and threshold of 10_

    $ python audio_dropout_detector.py -i "../test/audio/Audio_With_Gap_20.wav" -w 8 -t 10
_This will use a file with a known gap of 20 samples, window value of 8 and threshold of 10_

    
##### NOTES:
_One thing that caught me up for a bit was a RuntimeError in numpy calculating the RMS value until I figured out how
to suppress the error:_
                
                with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning):
                    rms(chunk)


##### TODO:
- Figure out a better method than RMS so the script isn't so dpendent on window size.

- module currently only supports detecting drops in overall loudness (RMS) to look for potential problem areas.  
If a glitch was represented by an unusually loud signal (feedback, ringing, distortion), it would not flag that area
  
- Streamline the process so that it can process a batch of files based on directory contents

- I found the package soundfile after writing my own windowing.  sf.blocks() generator function would have been handy.
