# Collection is absed on:
# python -m cProfile -o profile.txt pytari2600.py ../atari2600/roms/Pitfall\!.bin 
#
# Collect stats with this script via:
# python -m pytari2600.python -r -- <pytari2600 args>
#
# Results via:
#
# python -m pytari2600.python -t
# python -m pytari2600.python -c
#
#

import cProfile
import pytari2600
import argparse
import pstats
import sys

class Args(object):
    def __init__(self):
        pass
  
parser = argparse.ArgumentParser(description='Profiles the emulator. ')
parser.add_argument('-r', dest='rerun', action='store_true', default=False, 
                          help="Run and record profiling data.")
parser.add_argument('-t', dest='tottime', action='store_true', default=False,
                          help="Output ordered by total time per function.")
parser.add_argument('-c', dest='cumulative', action='store_true', default=False,
                          help="Output ordered by cumulative time per function.")

# Seperate the profiler options from the emulator options ('--')
ARG_SEPERATOR = '--'
try:
  arg_seperator_index = sys.argv.index(ARG_SEPERATOR)
  profiler_args = parser.parse_args(args=sys.argv[1:arg_seperator_index])
  emulator_args = sys.argv[arg_seperator_index + 1:]
except:
  profiler_args = parser.parse_args()
  DEFAULT_ROM = '../../emulator/atari2600/roms/Pitfall!.bin'
  emulator_args = [DEFAULT_ROM]


if profiler_args.rerun:
  pytari_args = Args()

  # Get/set/use the default arguments
  pytari_args_parser = pytari2600.get_pytari2600_argparser()

  pytari_args = pytari_args_parser.parse_args(args=emulator_args)

  # Explicitly overide defaults
  pytari_args.stop_clock=8000000
  
  cProfile.run('pytari2600.run(pytari_args)','profile.stats')
  
p = pstats.Stats('profile.stats')
if profiler_args.cumulative:
  p.sort_stats('cumulative').print_stats()
if profiler_args.tottime:
  p.sort_stats('tottime').print_stats()
