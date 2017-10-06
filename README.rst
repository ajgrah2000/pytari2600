# pytari2600
python based atari 2600 emulator

Python atari2600 emulator
=========================
|license| |build| |coverage|

Atari2600 emulator written in Python.

The emulator is written based on information from the following documents: 

  Atari 2600 TIA Hardware Notes, by Andrew Towers
  http://www.atarihq.com/danb/files/TIA_HW_Notes.txt
  Stella programmer's guide, by Steve Write

  Atari 2600 TIA Schematics (primarily used for the audio module).
  http://www.atariage.com/2600/archives/schematics_tia/index.html

Module dependencies:
   pygame (1.9.1)
   numpy (optional)
   pyglet (optional, not fully supported)

Create package:
   python setup.py sdist
Install:
   python setup.py install 
Run (show help):
   python -m pytari2600

   usage: pytari2600.py [-h] [-d] [-r REPLAY_FILE]
                        [--stella_record_file STELLA_RECORD_FILE]
                        [--record_audio_only] [-s STOP_CLOCK]
                        [-c {default,pb,mnet,cbs,e,fe,super,f4,single_bank}]
                        [-p {ntsc,pal}] [-g {pyglet,pygame}]
                        [--cpu {cpu,cpu_gen}]
                        [-a {oss_stretch,wav,oss,pygame,tia_dummy}] [-n]
                        cartridge_name
   
   ATARI emulator
   
   positional arguments:
     cartridge_name
   
   optional arguments:
     -h, --help            show this help message and exit
     -d
     -r REPLAY_FILE, --replay_file REPLAY_FILE
                           Json file to save/restore state. Triggered via '[',']'
                           keys
     --stella_record_file STELLA_RECORD_FILE
                           Stella record/replay output script file. Generates a
                           python script that can replay stella read/writes.
     --record_audio_only   To be used in conjuction with '--stella_record_file',
                           records only the audio writes, allows audio only
                           playback from tia.
     -s STOP_CLOCK         Set a clock time to stop (useful for profiling),
                           setting to '0' is disable stop
     -c {default,pb,mnet,cbs,e,fe,super,f4,single_bank}
                           Select the cartridge type of the rom being run
                           (default is for 'common' bankswitching)
     -p {ntsc,pal}         Select the palette to use (only changes color, not
                           timing).
     -g {pyglet,pygame}    Select an alternate to graphics module
     --cpu {cpu,cpu_gen}   Select an alternate CPU emulation, primarily to allow
                           trying different optimisations.
     -a {oss_stretch,wav,oss,pygame,tia_dummy}
                           Select an alternate CPU emulation, primarily to allow
                           trying different optimisations.
     -n                    Wishful flag for when the emulator runs too fast.

Keys
====
arrow keys - move
z - Fire button
s - Select
r - Reset
1 - difficulty
2 - difficulty
[ - save state (if -r has been specified)
] - restore state (if -r has been specified)

Example startup
===============
Examples (no audio by default, as audio is too flakey):

python -m pytari2600 myrom.bin

For different cartridge type: 
python -m pytari2600 -c cbs my_cbs_rom.bin

Save audio to 'pytari.wav' file, no audio during play (for your listening pleasure when you've finished playing) 
python -m pytari2600 -a wav my_cbs_rom.bin

pypy -m pytari2600 my_cbs_rom.bin


Issues:

TODO:
    - Speed improvements: On my machine, python + pygame runs ~ 1/3 of real-time
    - Audio with python. There are large delays in they way I'm handling audio,
      larger buffers lead to larger delay, smaller buffers drain and drop out.
    - Audio with 'pypy'.  pypy + Pygame appears to deal with sound buffers
      differently, so audio is choppy/broken
    - Audio general.  I'd like to switch to a callback for audio, so the buffer
      can be filled when it's close to empty, rather pre-filling buffers to try to keep them full.
    - Cartridge auto detection (I'd like to determine the style of cartridge by
      it's contents, ie detect the bank switching mechanism and RAM)
    - More undocumented opcoded (I've generally added op-codes as I encounter them).
    - Pick another name, 'pytari' appears to be used for another python atari
      emulator, so 'pytari2600' isn't particularly original.
    - Ensure that creating the setup.py package hasn't broken anything.
    - Find a better way to 'quit/stop' (currently harsh exit in
      pytari2600/inputs.py), this was easiest mechanism that worked for tests
      and normal usage.
    - Fix remaining/known Stella emulation issues:
        - Generally setting 'FUTURE_PIXELS' between 1-9 will be fairly stable for a particular rom, but is a fudge.
        - Real Stella 'latches' the first graphic, reset is at end of line,
          currently it's update 'immediately' (which is why FUTURE_PIXELS fudge
          sometimes makes things look batter).
        - HMOVE/Other writes have slightly different timing based on scan
          location (currently not checking all cases, only '74th' cycle is
          checked.)

.. |license| image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://raw.githubusercontent.com/agraham/pytari2600/master/LICENSE
   :alt: MIT License

.. |build| image:: https://travis-ci.org/ajgrah2000/pytari2600.svg?branch=master
   :target: https://travis-ci.org/ajgrah2000/pytari2600
   :alt: Continuous Integration

.. |coverage| image:: https://coveralls.io/repos/github/ajgrah2000/pytari2600/badge.svg?branch=master
   :target: https://coveralls.io/github/ajgrah2000/pytari2600?branch=master
   :alt: Coverage
