# Collection is absed on:
# python -m cProfile -o profile.txt pytari2600.py ../atari2600/roms/Pitfall\!.bin 
#
# Collect stats with this script via:
# python -m pytari2600.python profile <pytari2600 args>
#
# Results via:
#
# python -m pytari2600.python report [-c] [-t]
#

import cProfile
import pytari2600
import argparse
import pstats
import sys

def profile(profile_args):
  """ Run the c profiler using the specified arguments. 
  """

  profile_args.stop_clock=8000000

  cProfile.runctx('pytari2600.run(profile_args)', 
                  globals={'pytari2600':pytari2600}, 
                  locals={'profile_args':profile_args}, 
                  filename=profile_args.profile_filename)

def report(profile_args):
  """ Generate a profile report. 
  """

  p = pstats.Stats(profile_args.profile_filename)
  if profile_args.cumulative:
    p.sort_stats('cumulative').print_stats()

  if profile_args.tottime:
    p.sort_stats('tottime').print_stats()

def main():
  parser = argparse.ArgumentParser(description='Profiles the emulator. ', 
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('--filename', dest='profile_filename', action='store', default='profile.stats',
                      help="Name of the profile data file to create/read.")
  
  sub_parsers = parser.add_subparsers(help='Subparser commands.')
  report_args_parser  = sub_parsers.add_parser('report',  help='Display profile report data')

  profile_args_parser = sub_parsers.add_parser('profile', help='Generate new profile data.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  # Populate the pytari sub command arguments.
  pytari2600.populate_pytari2600_argparser(profile_args_parser)

  report_args_parser.add_argument('-t', dest='tottime', action='store_true', default=False,
                            help="Output ordered by total time per function.")
  report_args_parser.add_argument('-c', dest='cumulative', action='store_true', default=False,
                            help="Output ordered by cumulative time per function.")


  # The command to execute is selected by setting a different default function
  # per command, to a common function name.
  profile_args_parser.set_defaults(func=profile)
  report_args_parser.set_defaults(func=report)
  
  profiler_args = parser.parse_args()
  profiler_args.func(profiler_args) 

if __name__=='__main__':
  main()
