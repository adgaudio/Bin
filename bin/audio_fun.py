"""Build (audio) signals and output them to sound card.  What does 
a fibonacci sequence sound like?"""

import numpy as np
import pyaudio
import pylab
from scipy.signal import waveforms
import struct
import wave

def fib():
    n_1 = 0
    n = 1
    while True:
        yield n
        tmp = n
        n = n_1 + n
        n_1 = tmp

def fib_arr(n):
    a = fib()
    return [a.next() for x in range(n)]

def fib_example():
    freqs = np.log2(np.array(fib_arr(90)))
    music =  [sine_wave(x, duration=.5) for x in freqs%4 *100+220]
    play_arrs(music, pyaudio.PyAudio())

notes = 'A Bb B C C# D Eb E F F# G G#'.split()
freqs = [440*pow(2, (1./12))**i for i in range(len(notes))] # equal temperment
notemap = {n:f for n,f in zip(notes[:12], freqs)}

###############################



DURATION_SECONDS = .5
CHANNELS = 1
SAMPLE_RATE = 44100
NUM_SAMPLES = SAMPLE_RATE * DURATION_SECONDS

PYAUDIO_FORMAT = pyaudio.paFloat32
NUMPY_FORMAT = 'float32'
STRUCT_FORMAT = 'f'


#def add_enharmonics(arr, n):
    #return arr

def wave_generator(func, freq, duration=DURATION_SECONDS, sample_rate=SAMPLE_RATE):
    arr = np.arange(0, duration, 1.0/sample_rate)
    arr2 = func(2.0*np.pi*freq*arr)
    # Taper head and tail of wave to 0 so it makes smooth transitions
    pct_tapered = 0.05
    amt_tapered = len(arr2) * pct_tapered
    head = arr2[:amt_tapered]
    middle = arr2[amt_tapered:len(arr2) - amt_tapered]
    tail = arr2[len(arr2) - amt_tapered:]
    head = head * np.resize(np.arange(0, 1,  1./amt_tapered), len(head))
    tail = tail * np.arange(1, 0, -1./amt_tapered)
    return np.concatenate([head,middle,tail])

def sine_wave(freq, **kwargs):
    return wave_generator(waveforms.sin, freq, **kwargs)
def sawtooth_wave(freq, **kwargs):
    return wave_generator(waveforms.sawtooth, freq, **kwargs)

def plot_fft(arr, args=('g.',)):
    pylab.plot(np.fft.fftfreq(arr.shape[-1]), abs(np.fft.fft(arr)), *args)


def get_stream(pyaudio_manager, output=True, format=PYAUDIO_FORMAT, channels=CHANNELS,
        sample_rate=SAMPLE_RATE, frames_per_buffer=1024, **kwargs):
    kwargs.update(dict( format=format, 
                        channels=channels,
                        rate=sample_rate,
                        output=output,
                        #input=True,
                        frames_per_buffer=frames_per_buffer,))
    stream = pyaudio_manager.open(**kwargs)
    return stream

def _structpack(arrs, struct_format=STRUCT_FORMAT):
    return [struct.pack('@%s%s' % (len(arr), struct_format), *arr) for arr in arrs]

def write_wave(arrs, filepath,
               sample_width=pyaudio.get_sample_size(PYAUDIO_FORMAT),
               channels=CHANNELS, sample_rate=SAMPLE_RATE):
    f = wave.open(filepath, 'w')
    f.setnchannels(channels)
    f.setsampwidth(sample_width)
    f.setframerate(sample_rate)
    for arr in _structpack(arrs):
        f.writeframes(arr)
    f.close()

def play_arrs(arrs, pyaudio_manager):
    stream = get_stream(pyaudio_manager)
    arrs2 = _structpack(arrs)
    [stream.write(arr) for arr in arrs2]
    stream.close()

def example(freq=440, dur=1):
    arr = sawtooth_wave(freq, duration=dur)
    arr2 = sine_wave(freq, duration=dur)
    arr = np.resize([arr,arr2], [1, len(arr)+len(arr2)])[0]
    p = pyaudio.PyAudio()
    play_arrs([arr], p)
    plot_fft(arr2)

