from distutils.core import setup
setup(name='pytari2600',
      description='Python atari2600 emulator',
      version='0.1',
      author='Andrew Graham',
      packages=['.',
                'pytari2600',
                'pytari2600.memory',
                'pytari2600.cpu',
                'pytari2600.cpu_gen',
                'pytari2600.graphics',
                'pytari2600.test',
                'pytari2600.audio'],
      package_dir={'pytari2600':'pytari2600'},
      package_data={'pytari2600':['graphics/palette.dat','test/dummy_rom.bin']}
      )
