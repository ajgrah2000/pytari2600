""" Entry point for the atari emulator.
    Intended to work with python3, python2, pypy, pygame, pyglet, cyglfw3.
"""

import argparse
from . import atari2600

# Possible audio drivers
audio_options = {
    'sounddevice':      'from pytari2600.audio.sounddeviceaudio import SoundDeviceSound as AudioDriver',
    'pygame':      'from pytari2600.audio.pygameaudio import PygameStretchTIA_Sound as AudioDriver',
    'wav':         'from pytari2600.audio.testaudio import WAV_TIA_Sound as AudioDriver',
    'oss':         'from pytari2600.audio.testaudio import OSS_TIA_Sound as AudioDriver',
    'oss_stretch': 'from pytari2600.audio.testaudio import OSS_StretchTIA_Sound as AudioDriver',
    'tia_dummy' :  'from pytari2600.audio.tiasound import TIA_Sound as AudioDriver'
    }

# Possible graphics drivers
graphics_options = {
    'pyglet': 'from pytari2600.graphics.pygletstella import PygletStella as Graphics',
    'pygame': 'from pytari2600.graphics.pygamestella import PygameStella as Graphics',
    'cyglfw': 'from pytari2600.graphics.cyglfwstella import CyglfwStella as Graphics'
    }

# Possible graphics drivers
cpu_options = {
    'cpu_gen': 'from pytari2600 import cpu_gen as cpu',
    'cpu': 'import pytari2600.cpu as cpu'
    }

def config(graphics_selection, audio_selection, cpu_selection):
    # Use some questionable code to perform driver selection.
    # Imports only occur 'on-demand' so missing dependencies cause issues
    # unless you attempt to use them.
    exec_locals= {}
    exec(audio_options[audio_selection], {}, exec_locals)
    exec(graphics_options[graphics_selection], {}, exec_locals)
    exec(cpu_options[cpu_selection], {}, exec_locals)

    return (exec_locals['Graphics'], 
            exec_locals['AudioDriver'], 
            exec_locals['cpu'])

def run(args):
    (video, audio, cpu) = config(args.graphics_driver, args.audio_driver, args.cpu_driver)

    atari = atari2600.Atari(video, audio, cpu)

    atari.set_palette(args.palette)
    atari.insert_cartridge(args.cartridge_name, args.cart_type)

    atari.power_on(args.stop_clock, args.no_delay, args.debug, args.replay_file, args.stella_record_file, args.record_audio_only)

def get_pytari2600_argparser():
    parser = argparse.ArgumentParser(description='ATARI emulator', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    populate_pytari2600_argparser(parser)
    return parser 

def populate_pytari2600_argparser(parser):
    parser.add_argument('cartridge_name',            action='store')
    parser.add_argument('-d', dest='debug',          action='store_true')
    parser.add_argument('-r', '--replay_file', dest='replay_file', type=str,
                              help="Json file to save/restore state. Triggered via '[',']' keys")
    parser.add_argument('--stella_record_file', dest='stella_record_file', type=str,
                              help="Stella record/replay output script file. Generates a python script that can replay stella read/writes.")
    parser.add_argument('--record_audio_only', dest='record_audio_only',          action='store_true',
            help="To be used in conjuction with '--stella_record_file', records only the audio writes, allows audio only playback from tia.")
    parser.add_argument('-s', dest='stop_clock',     type=int, default=0,
                              help="Set a clock time to stop (useful for profiling), setting to '0' is disable stop")
    parser.add_argument('-c', dest='cart_type', 
                              choices=['default', 'pb', 'mnet', 'cbs',
                              'e', 'fe','super','f4', 'single_bank'], 
                              default='default',
                              help="Select the cartridge type of the rom being run (default is for 'common' bankswitching)")
    parser.add_argument('-p', dest='palette', 
                              choices=['ntsc', 'pal'], 
                              default='ntsc',
                              help="Select the palette to use (only changes color, not timing).")
    parser.add_argument('-g', dest='graphics_driver', 
                              choices=graphics_options.keys(), 
                              default='pygame',
                              help="Select an alternate to graphics module")
    parser.add_argument('--cpu', dest='cpu_driver', 
                              choices=cpu_options.keys(), 
                              default='cpu_gen',
                              help="Select an alternate CPU emulation, primarily to allow trying different optimisations.")
    parser.add_argument('-a', dest='audio_driver', 
                              choices=audio_options.keys(), 
                              default='tia_dummy',
                              help="Select an alternate CPU emulation, primarily to allow trying different optimisations.")
    parser.add_argument('-n', dest='no_delay',       action='store_true',
                              help="Wishful flag for when the emulator runs too fast.")

def main():
    parser = get_pytari2600_argparser()

    args = parser.parse_args()

    print(args)
                      
    run(args)

if __name__=='__main__':
    main()
