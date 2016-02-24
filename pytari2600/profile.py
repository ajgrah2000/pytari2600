# Collection using:
# python -m cProfile -o profile.txt pytari2600.py ../atari2600/roms/Pitfall\!.bin 
import cProfile
import pytari2600
import argparse
import pstats

class Args(object):
    def __init__(self):
        pass
  
parser = argparse.ArgumentParser(description='Profile emulator')
parser.add_argument('-r', dest='rerun', action='store_true', default=False)
parser.add_argument('-t', dest='tottime', action='store_true', default=False)
parser.add_argument('-c', dest='cumulative', action='store_true', default=False)

cmd_args = parser.parse_args()

if cmd_args.rerun:
  pytari_args = Args()
  pytari_args.cart_type='default'
#  pytari_args.cart_type='single_bank'
  pytari_args.cartridge_name='../atari2600/roms/Pitfall!.bin'
  pytari_args.debug=False
  pytari_args.no_delay=False
  pytari_args.stop_clock=4000000
  pytari_args.replay_file=None
  pytari_args.graphics_driver='pygame'
  pytari_args.audio_driver='tia_dummy'
  pytari_args.cpu_driver='cpu_gen'
  
  cProfile.run('pytari2600.run(pytari_args)','profile.stats')
  
p = pstats.Stats('profile.stats')
if cmd_args.cumulative:
  p.sort_stats('cumulative').print_stats()
if cmd_args.tottime:
  p.sort_stats('tottime').print_stats()
