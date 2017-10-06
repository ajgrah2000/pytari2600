import ctypes
import time
import pkg_resources

class PlayfieldState(object):
    """  Playfield state.
         It's updated infrequently, so generate an entire scan each update and
         return the lookup.
    """

    def __init__(self):
        self.pf0    = 0
        self.pf1    = 0
        self.pf2    = 0
        self.ctrlpf = 0

        self._pf_lookup = [False] * Stella.FRAME_WIDTH
        self._pre_calc_playfield()

    def get_save_state(self):
        state = {}
        state['pf0'] = self.pf0
        state['pf1'] = self.pf1
        state['pf2'] = self.pf2
        state['ctrlpf'] = self.ctrlpf
        return state

    def set_save_state(self, state):
        self.pf0    = state['pf0']
        self.pf1    = state['pf1']
        self.pf2    = state['pf2']
        self.ctrlpf = state['ctrlpf']

        self.update()

    def _pre_calc_playfield(self):
        """ Pre-calc playfield lists. 

            Bit order for displaying pf1 is reverse to pf0 & pf2.
            Order:
            PF0: 4,5,6,7, PF1: 7,6,5,4,3,2,1,0 PF2: 0,1,2,3,4,5,6,7
        """

        self._pf0_lookup = []
        self._pf1_lookup = []
        self._pf2_lookup = []

        for i in range(256):
            pf_lookup = [False]*8
            mask = 1
            for b in range(8):
                if i & mask:
                    pf_lookup[b] = True
                mask += mask

            # Expand to 4-pixels
            pf_lookup = [x for x in pf_lookup for _ in (0,1,2,3)]

            self._pf2_lookup.append(list(pf_lookup))
            pf_lookup.reverse()
            self._pf1_lookup.append(list(pf_lookup))

        # PF0 is only 4-bit encoding.
        for i in range(16):
            self._pf0_lookup.append(self._pf2_lookup[i*16][16:32])

    def get_playfield_scan(self):
        return self._pf_lookup

    def update(self):
        """ Pre-compute the playfield on register change. """
        self._pf_lookup = []
        field = self._pf0_lookup[int(self.pf0/16)] + self._pf1_lookup[self.pf1] + self._pf2_lookup[self.pf2]
        self._pf_lookup.extend(field)

        # If right half is reversed, then reverse it.
        if self.ctrlpf & 0x1:
            field.reverse()

        self._pf_lookup.extend(field)

    def update_pf0(self, data):   
        self.pf0 = data
        self.update()

    def update_pf1(self, data):   
        self.pf1 = data
        self.update()

    def update_pf2(self, data):   
        self.pf2 = data
        self.update()

    def update_ctrlpf(self, data):   
        self.ctrlpf = data
        self.update()

class BallState(object):

    def __init__(self):
        self.enabl     = 0
        self.enablOld  = 0
        self.vdelbl    = 0
        self.resbl     = 0
        self.ctrlpf    = 0

        self._x_min     = 0
        self._x_max     = 0

        self._enabled  = False

        self._scan_line = [False] * Stella.FRAME_WIDTH

    def get_save_state(self):
        state = {}
        state['enabl']    = self.enabl
        state['enablOld'] = self.enablOld
        state['vdelbl']   = self.vdelbl
        state['resbl']    = self.resbl
        state['ctrlpf']   = self.ctrlpf
        return state

    def set_save_state(self, state):
        self.enabl    = state['enabl']
        self.enablOld = state['enablOld']
        self.vdelbl   = state['vdelbl']
        self.resbl    = state['resbl']
        self.ctrlpf   = state['ctrlpf']

        self.update()

    def update(self):
        if 0 == (self.vdelbl & 0x1):
            self._enabled = 0 != (self.enabl & 0x02)
        else:
            self._enabled = 0 != (self.enablOld & 0x02)

        width = 1 << ((self.ctrlpf & 0x30) >> 4)

        self._x_min = self.resbl - Stella.HORIZONTAL_BLANK 
        self._x_max = self.resbl - Stella.HORIZONTAL_BLANK  + width

        self._calc_ball_scan()

    def update_resbl(self, data):
        self.resbl = data
        self.update()
        
    def update_enableOld(self, data):
        self.enableOld = data
        self.update()

    def update_enabl(self, data):
        self.enabl = data
        self.update()

    def update_vdelbl(self, data):
        self.vdelbl = data
        self.update()

    def update_ctrlpf(self, data):
        self.ctrlpf = data
        self.update()

    def _calc_ball_scan(self):
        """ Calculate an entire scanline for the ball, re-calculated on
        parameter change. """
        # Default scan to false.
        self._scan_line = [False] * Stella.FRAME_WIDTH

        if self._enabled:
            for x in range(self._x_min, self._x_max):
               self._scan_line[x % Stella.FRAME_WIDTH] = True

    def get_ball_scan(self):
        return self._scan_line

class MissileState(object):

    def __init__(self):
        self.nusiz  = 0
        self.enam   = 0
        self.resm   = 0

        # Derived state data (nominally generated during update)
        self._number = 0
        self._gap    = 0

        # Default scan to false.
        self._scan_line = [False] * Stella.FRAME_WIDTH

    def get_save_state(self):
        state = {}
        state['nusiz'] = self.nusiz
        state['enam']  = self.enam
        state['resm']  = self.resm
        return state

    def set_save_state(self, state):
        self.nusiz = state['nusiz']
        self.enam  = state['enam']
        self.resm  = state['resm']

        self.update()

    def update(self):
        # Missiles ignore scaling options.
        (number, size, gap) = Stella.nusize(self.nusiz)
        self._number = number
        self._gap    = gap

        self._calc_missile_scan()

    def update_nusiz(self, data):
        self.nusiz = data
        self.update()

    def update_resm(self, data):
        self.resm = data
        self.update()

    def update_enam(self, data):
        self.enam = data
        self.update()

    def _calc_missile_scan(self):
        """ Pre-calculate an entire scan line, as update is called relatively
            infrequently. 
        """
        self._scan_line = [False] * Stella.FRAME_WIDTH

        if self.enam & 0x02:
            for n in range(self._number):
                # Uses same stretching as 'ball'
                width = 1 << ((self.nusiz & 0x30) >> 4)
                # Uses similar position to 'player'
                for i in range(width):
                    x = (i +self.resm + n*self._gap*8) % Stella.FRAME_WIDTH 
                    self._scan_line[x] = True

    def get_missile_scan(self):
        return self._scan_line

class PlayerState(object):
    def __init__(self, clocks):
        self.nusiz  = 0
        self.p      = 0
        self.pOld   = 0
        self.refp   = 0
        self.resp   = 0
        self.vdelp  = 0
        self.clocks = clocks

        # Derived state data (nominally generated during update)
        self._grp     = 0
        self._number  = 0
        self._size    = 0
        self._gap     = 0

        self._pos_start = 0

        self._scan_line = [False] * Stella.FRAME_WIDTH

        self._pre_calc_player()

    def get_save_state(self):
        state = {}
        state['nusiz'] = self.nusiz
        state['p'] = self.p
        state['pOld'] = self.pOld
        state['refp'] = self.refp
        state['resp'] = self.resp
        state['vdelp'] = self.vdelp
        return state

    def set_save_state(self, state):
        self.nusiz = state['nusiz'] 
        self.p     = state['p']     
        self.pOld  = state['pOld']  
        self.refp  = state['refp']  
        self.resp  = state['resp']  
        self.vdelp = state['vdelp'] 

        self.update()

    def update_nusiz(self, data):
        self.nusiz = data
        self.update()

    def update_resp(self, data):
        self.resp = data
        self.update()

    def update_refp(self, data):
        self.refp = data
        self.update()

    def update_p(self, data):
        self.p = data
        self.update()

    def update_pOld(self, data):
        self.pOld = data
        self.update()

    def update_vdelp(self, data):
        self.vdelp = data
        self.update()

    def _pre_calc_player(self):
        """ Precalculate all number, gap, size, graphic combinations. """
        self._player_scan_unshifted = []

        # Only 1,2,3 required, but 0..3 calculated
        NUMBER_RANGE = 4

        # Only 1,2,4 required, but 0..4 calculated
        SIZE_RANGE = 5

        # Gaps are 0, 2, 4, 8
        GAP_RANGE = 9

        GRAPHIC_RANGE = 256

        # Create enough empty lists to allow direct indexing.
        self._player_scan_unshifted = [[] for x in range(NUMBER_RANGE)]
        for number in [1,2,3]:

            self._player_scan_unshifted[number] = [[] for x in range(SIZE_RANGE)]
            for size in [1,2,4]:

                self._player_scan_unshifted[number][size] = [[] for x in range(GAP_RANGE)]
                for gap in [0,2,4,8]:
                    self._player_scan_unshifted[number][size].append([])
                    for reflect in range(2):
                        self._player_scan_unshifted[number][size][gap].append([])
                        for g in range(GRAPHIC_RANGE):
                            # Create the 8-bit 'graphic'
                            graphic = [False] * 8
                            for i in range(8):
                                if (g >> i) & 0x01:
                                    graphic[i] = True

                            if reflect:
                                graphic.reverse()

                            # Scale the graphic, so each pixel is 'size' big
                            graphic = [x for x in graphic for _ in [0] * size]

                            scan = [False] * Stella.FRAME_WIDTH
                            for n in range(number):
                                offset = n*gap*8
                                scan[offset:offset + len(graphic)] = graphic

                            self._player_scan_unshifted[number][size][gap][reflect].append(scan)

    def update(self):
        if (0 == (self.vdelp & 0x1)):
            self._grp = self.p
        else:
            self._grp = self.pOld

        if 0 == self._grp:
            self._scan_line = [False] * 160
        else:
            (number, size, gap) = Stella.nusize(self.nusiz)
            self._number = number
            self._size   = size
            self._gap    = gap

            if (self.refp & 0x8) == 0:
                self._reflect = 1
            else:
                self._reflect = 0

            self._pos_start = (self.resp + int(self._size/2))
            self._calc_player_scan()

    def _calc_player_scan(self):
        # Rotate the scan.
        rotation = Stella.FRAME_WIDTH-self._pos_start
        scan = self._player_scan_unshifted[self._number][self._size][self._gap][self._reflect][self._grp]
        self._scan_line = scan[rotation:] + scan[:rotation]
                            
        
    def get_player_scan(self):
        return self._scan_line

class LineState(object):
  """ Line state used per stella line. """
  def __init__(self, default_color):
    self.pColor = [default_color,default_color]
    self.backgroundColor = default_color
    self.playfieldColor = default_color
    self.ctrlpf   = 0
    self.hmp      = [0,0]
    self.hmm      = [0,0]
    self.hmbl     = 0

  def get_save_state(self):
      state = {}
      state['pColor'] = self.pColor
      state['backgroundColor'] = self.backgroundColor
      state['playfieldColor'] = self.playfieldColor
      state['ctrlpf'] = self.ctrlpf
      state['hmp'] = list(self.hmp)
      state['hmm'] = list(self.hmm)
      state['hmbl'] = self.hmbl
      return state

  def set_save_state(self, state):
      self.pColor          = state['pColor']
      self.backgroundColor = state['backgroundColor']
      self.playfieldColor  = state['playfieldColor']
      self.ctrlpf          = state['ctrlpf']
      self.hmp             = list(state['hmp'])
      self.hmm             = list(state['hmm'])
      self.hmbl            = state['hmbl']

class CollisionState(object):
    def __init__(self):
        self._cxmp = [0,0]
        self._cxpfb = [0, 0]
        self._cxmfb = [0, 0]
        self._cxblpf = 0
        self._cxppmm = 0

    def get_save_state(self):
        state = {}
        state['cxmp']   = self._cxmp
        state['cxpfb']  = list(self._cxpfb)
        state['cxmfb']  = list(self._cxmfb)
        state['cxblpf'] = self._cxblpf
        state['cxppm']  = self._cxppmm
        return state

    def set_save_state(self, state):
        self._cxmp   = state['cxmp']
        self._cxpfb  = state['cxpfb']
        self._cxmfb  = state['cxmfb']
        self._cxblpf = state['cxblpf']
        self._cxppmm = state['cxppm']

    def clear(self):
        self._cxmp = [0,0]
        self._cxpfb = [0, 0]
        self._cxmfb = [0, 0]
        self._cxblpf = 0
        self._cxppmm = 0

    def update_collisions(self, p0, p1, m0, m1, bl, pf):
        if m0:
            if p1:
                self._cxmp[0]  |= 0x80 # m0 & p1
            if pf:
                self._cxmfb[0] |= 0x80 # m0 & pf
            if bl:
                self._cxmfb[0] |= 0x40 # m0 & bl
            if m1:
                self._cxppmm   |= 0x40 # m0 & m1
            if p0:
                self._cxmp[0]  |= 0x40 # m0 & p0

        if m1:
            if pf:
                self._cxmfb[1] |= 0x80 # m1 & pf
            if bl:
                self._cxmfb[1] |= 0x40 # m1 & bl
            if p0:
                self._cxmp[1]  |= 0x80 # m1 & p0
            if p1:
                self._cxmp[1]  |= 0x40 # m1 & p1

        if bl:
            if pf:
                self._cxblpf   |= 0x80 # bl & pf
            if p0:
                self._cxpfb[0] |= 0x40 # bl & p0
            if p1:
                self._cxpfb[1] |= 0x40 # bl & p1

        if p0:
            if pf:
                self._cxpfb[0] |= 0x80 # p0 & pf
            if p1:
                self._cxppmm   |= 0x80 # p0 & p1

        if p1 & pf:
            self._cxpfb[1]     |= 0x80 # p1 & pf

class Colors(object):

    def __init__(self):
        self.set_palette("ntsc")

    def set_palette(self, palette_type):
        """ palette_type needs to match the file name, expected:
            ntsc -> palette.ntsc.dat
            or 
            pal -> palette.pal.dat
        """

        palette_filename = "palette.%s.dat"%(palette_type)

        self.colors = []

        palette_file = pkg_resources.resource_stream(__name__, palette_filename)
        for line in palette_file:
            (r, g, b) = [int(x) for x in line.split()[0:3]]
            self.colors.append(self.set_color(r, g, b))

    def fade_color(self, color):
        color  = (int(color[0] * 0.9), 
                  int(color[1] * 0.9),
                  int(color[2] * 0.9),
                  int(color[3] * 0.9))
        return color # * (0.9,0.9,0.9)

    def set_color(self, r, g, b):
        pass

    def get_color(self, color):
        c = color >> 1
        return self.colors[c]

class Stella(object):

    HORIZONTAL_BLANK  = 68
    FRAME_WIDTH       = 160
    FRAME_HEIGHT      = 280
    PIXEL_HEIGHT      = 2
    PIXEL_WIDTH       = 4

    # Scaled 'blit' size.
    BLIT_WIDTH  = FRAME_WIDTH  * PIXEL_WIDTH 
    BLIT_HEIGHT = FRAME_HEIGHT * PIXEL_HEIGHT

    VSYNC_LINES       = 3
    VBLANK_LINES      = 37
    OVERSCAN_LINES    = 30

    NUM_COLORS        = 256

    VSYNC_MASK = 0x2
    VSYNC_ON   = 0x2
    VSYNC_OFF  = 0x0

    START_DRAW_Y      = 0
    END_DRAW_Y = VBLANK_LINES + FRAME_HEIGHT + OVERSCAN_LINES

    HORIZONTAL_TICKS = FRAME_WIDTH + HORIZONTAL_BLANK
    INPUT_45_LATCH_MASK = 0x40
    BLANK_PADDLE_RECHARGE = 0x80
    BLANK_MASK = 0x2
    BLANK_ON   = 0x2
    BLANK_OFF  = 0x0

    PF_PRIORITY = 0x4
    PF_SCORE    = 0x2

    def __init__(self, clocks, inputs, AudioDriver):
        self.clocks = clocks
        self.inputs = inputs

        # Sound generation
        self.tiasound = AudioDriver(clocks)

        self._is_vsync = False
        self._screen_start_clock       = self.clocks.system_clock
        self._paddle_start_clock       = self.clocks.system_clock
        self._last_screen_update_clock = self.clocks.system_clock
        self._is_blank = True
        self._is_input_latched = True
        self._is_update_time = True

        self.nextLine = LineState(self.default_color)
        self.p0_state = PlayerState(self.clocks)
        self.p1_state = PlayerState(self.clocks)
        self.missile0 = MissileState()
        self.missile1 = MissileState()
        self.ball     = BallState()
        self.playfield_state = PlayfieldState()

        self._display_lines = []
        for y in range(self.END_DRAW_Y - self.START_DRAW_Y + 1):
          self._display_lines.append([self.default_color]*self.FRAME_WIDTH)

        self._collision_state = CollisionState()
        # Dummy input return values
        self._inpt = [0, 0, 0, 0, 0, 0] 

        self._debug_display_time = 0
        self._vsync_debug_output_clock = 0

        # Initialse write lookup
        self._populate_write_lookup()

        self.driver_open_display()

    def get_save_state(self):
        state = {}
        state['tiasound']  = self.tiasound.get_save_state()
        state['nextLine']  = self.nextLine.get_save_state()
        state['p0']        = self.p0_state.get_save_state()
        state['p1']        = self.p1_state.get_save_state()
        state['missile0']  = self.missile0.get_save_state()
        state['missile1']  = self.missile1.get_save_state()
        state['ball']      = self.ball.get_save_state()
        state['playfield'] = self.playfield_state.get_save_state()
        state['collision'] = self._collision_state.get_save_state()
        state['is_vsync']  = self._is_vsync
        state['is_blank']  = self._is_blank
        state['is_input_latched']   = self._is_input_latched
        state['is_update_time']     = self._is_update_time
        state['screen_start_clock'] = self._screen_start_clock
        state['paddle_start_clock'] = self._paddle_start_clock
        state['last_screen_update_clock'] = self._last_screen_update_clock

        return state

    def set_save_state(self, state):
        self.tiasound.set_save_state(state['tiasound'])
        self.nextLine.set_save_state(state['nextLine'])
        self.p0_state.set_save_state(state['p0'])
        self.p1_state.set_save_state(state['p1'])
        self.missile0.set_save_state(state['missile0'])
        self.missile1.set_save_state(state['missile1'])
        self.ball.set_save_state(state['ball'])
        self.playfield_state.set_save_state(state['playfield'])
        self._collision_state.set_save_state(state['collision'])
        self._is_vsync                 = state['is_vsync']
        self._is_blank                 = state['is_blank']
        self._is_input_latched         = state['is_input_latched']
        self._is_update_time           = state['is_update_time']
        self._screen_start_clock       = state['screen_start_clock']
        self._paddle_start_clock       = state['paddle_start_clock']
        self._last_screen_update_clock = state['last_screen_update_clock']

        # Update after load
        self._update_scans()

    def driver_open_display(self):
        """ Open display function to be implemented based on implementing
            display driver.
        """
        raise Exception("missing implementation ")

    def driver_update_display(self):
        """ Update display function to be implemented based on implementing
            display driver.
        """
        raise Exception("missing implementation ")

    def read(self, address):
        self._update_scans()
        self.tiasound.step()

        masked_address = address & 0xF
        if 0x0   == masked_address:
            result = self._collision_state._cxmp[0]
        elif 0x1 == masked_address:
            result = self._collision_state._cxmp[1]
        elif 0x2 == masked_address:
            result = self._collision_state._cxpfb[0]
        elif 0x3 == masked_address:
            result = self._collision_state._cxpfb[1]
        elif 0x4 == masked_address:
            result = self._collision_state._cxmfb[0]
        elif 0x5 == masked_address:
            result = self._collision_state._cxmfb[1]
        elif 0x6 == masked_address:
            result = self._collision_state._cxblpf
        elif 0x7 == masked_address:
            result = self._collision_state._cxppmm
        elif 0x8 == masked_address:
            result = self._inpt[0]
            # paddle0 stuff
        elif 0x9 == masked_address:
            result = self._inpt[1]
            # paddle1 stuff
        elif 0xA == masked_address:
            # paddle3 stuff
            result = self._inpt[2]
        elif 0xB == masked_address:
            result = self.inputs.get_input7()
        elif 0xC == masked_address:
            result = self.inputs.get_input7()
        elif 0xD == masked_address:
            # Guessing at '0x80'
            result = self._inpt[5] | 0x80
        else:
            print("Unknown stella read")
            result = 0

        # TODO: Check values, 'noice_liquidcandy.bin' appears to require
        # cxmp[0] to return 0x20 for correct font, guessing that '| address' is
        # related.  I don't know what D0-D5 should read for collisions
        result = result | address
        return result

    def write(self, address, data):
        self._update_scans()
        self.tiasound.step()

        if False == self._is_blank:
            self._screen_scan(self.nextLine, self._display_lines)

        masked_address = address & 0x3F
        self._write_function[masked_address](data)

    def _dummy_write(self, data):
        pass

    def _populate_write_lookup(self):
        self._write_function = [self._dummy_write] * 0x40

        self._write_function[0x00] = self._STELLA_Write_Vsync
        self._write_function[0x01] = self._STELLA_Write_Vblank
        self._write_function[0x02] = self._STELLA_Write_Wsync
        self._write_function[0x03] = self._STELLA_Write_Rsync
        self._write_function[0x04] = self._STELLA_Write_Nusiz0
        self._write_function[0x05] = self._STELLA_Write_Nusiz1
        self._write_function[0x06] = self._STELLA_Write_Colump0
        self._write_function[0x07] = self._STELLA_Write_Colump1
        self._write_function[0x08] = self._STELLA_Write_Colupf
        self._write_function[0x09] = self._STELLA_Write_Colubk
        self._write_function[0x0A] = self._STELLA_Write_Ctrlpf
        self._write_function[0x0B] = self._STELLA_Write_Refp0
        self._write_function[0x0C] = self._STELLA_Write_Refp1
        self._write_function[0x0D] = self._STELLA_Write_Pf0
        self._write_function[0x0E] = self._STELLA_Write_Pf1
        self._write_function[0x0F] = self._STELLA_Write_Pf2
        self._write_function[0x10] = self._STELLA_Write_Resp0
        self._write_function[0x11] = self._STELLA_Write_Resp1
        self._write_function[0x12] = self._STELLA_Write_Resm0
        self._write_function[0x13] = self._STELLA_Write_Resm1
        self._write_function[0x14] = self._STELLA_Write_Resbl
        self._write_function[0x15] = self.tiasound.write_audio_ctrl_0 # AudioCtrl0
        self._write_function[0x16] = self.tiasound.write_audio_ctrl_1 # AudioCtrl1
        self._write_function[0x17] = self.tiasound.write_audio_freq_0 # AudioFreq0
        self._write_function[0x18] = self.tiasound.write_audio_freq_1 # AudioFreq1
        self._write_function[0x19] = self.tiasound.write_audio_vol_0  # AudioVol0
        self._write_function[0x1A] = self.tiasound.write_audio_vol_1  # AudioVol1
        self._write_function[0x1B] = self._STELLA_Write_Grp0
        self._write_function[0x1C] = self._STELLA_Write_Grp1
        self._write_function[0x1D] = self._STELLA_Write_Enam0
        self._write_function[0x1E] = self._STELLA_Write_Enam1
        self._write_function[0x1F] = self._STELLA_Write_Enabl
        self._write_function[0x20] = self._STELLA_Write_Hmp0
        self._write_function[0x21] = self._STELLA_Write_Hmp1
        self._write_function[0x22] = self._STELLA_Write_Hmm0
        self._write_function[0x23] = self._STELLA_Write_Hmm1
        self._write_function[0x24] = self._STELLA_Write_Hmbl
        self._write_function[0x2A] = self._STELLA_Write_Hmove
        self._write_function[0x2B] = self._STELLA_Write_Hclr
        self._write_function[0x25] = self._STELLA_Write_Vdelp0
        self._write_function[0x26] = self._STELLA_Write_Vdelp1
        self._write_function[0x27] = self._STELLA_Write_Vdelbl
        self._write_function[0x2C] = self._STELLA_Write_Cxclr

    def _STELLA_Write_Vsync(self, data):
            self._write_vsync(data)

    def _STELLA_Write_Vblank(self, data):
            self._write_vblank(data)

    def _STELLA_Write_Wsync(self, data):
            self._write_wsync(data)

    def _STELLA_Write_Rsync(self, data):
            self._write_rsync(data)

    def _STELLA_Write_Nusiz0(self, data):
            self.p0_state.update_nusiz(data)
            self.missile0.update_nusiz(data)

    def _STELLA_Write_Nusiz1(self, data):
            self.p1_state.update_nusiz(data)
            self.missile1.update_nusiz(data)

    def _STELLA_Write_Colump0(self, data):
            self.nextLine.pColor[0] = self._colors.get_color(data)

    def _STELLA_Write_Colump1(self, data):
            self.nextLine.pColor[1] = self._colors.get_color(data)

    def _STELLA_Write_Colupf(self, data):
            self.nextLine.playfieldColor = self._colors.get_color(data)

    def _STELLA_Write_Colubk(self, data):
            self.nextLine.backgroundColor = self._colors.get_color(data)

    def _STELLA_Write_Ctrlpf(self, data):
            self.nextLine.ctrlpf        = data
            self.playfield_state.update_ctrlpf(data)
            self.ball.update_ctrlpf(data)

    def _STELLA_Write_Refp0(self, data):
            self.p0_state.update_refp(data)

    def _STELLA_Write_Refp1(self, data):
            self.p1_state.update_refp(data)

    def _STELLA_Write_Pf0(self, data):
            self.playfield_state.update_pf0(data)

    def _STELLA_Write_Pf1(self, data):
            self.playfield_state.update_pf1(data)

    def _STELLA_Write_Pf2(self, data):
            self.playfield_state.update_pf2(data)

    def _STELLA_Write_Resp0(self, data):
            if (((self.clocks.system_clock + 5 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS) < Stella.HORIZONTAL_BLANK):
                self.p0_state.update_resp(3)
            else:
                self.p0_state.update_resp((self.clocks.system_clock + 5 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS - Stella.HORIZONTAL_BLANK)

    def _STELLA_Write_Resp1(self, data):
            if (((self.clocks.system_clock + 5 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS) < Stella.HORIZONTAL_BLANK):
                self.p1_state.update_resp(3)
            else:
                self.p1_state.update_resp((self.clocks.system_clock + 5 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS - Stella.HORIZONTAL_BLANK)

    def _STELLA_Write_Resm0(self, data):
            if (((self.clocks.system_clock + 4 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS) < Stella.HORIZONTAL_BLANK):
                self.missile0.update_resm(3)
            else:
                self.missile0.update_resm((self.clocks.system_clock + 4 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS - Stella.HORIZONTAL_BLANK)

    def _STELLA_Write_Resm1(self, data):
            if (((self.clocks.system_clock + 4 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS) < Stella.HORIZONTAL_BLANK):
                self.missile1.update_resm(3)
            else:
                self.missile1.update_resm((self.clocks.system_clock + 4 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS - Stella.HORIZONTAL_BLANK)

    def _STELLA_Write_Resbl(self, data):
            self.ball.update_resbl((self.clocks.system_clock + 4 - self._screen_start_clock) % Stella.HORIZONTAL_TICKS)

    def _STELLA_Write_Grp0(self, data):
            self.p0_state.update_p(data)
            self.p1_state.update_pOld(self.p1_state.p)

    def _STELLA_Write_Grp1(self, data):
            self.p1_state.update_p(data)
            self.p0_state.update_pOld(self.p0_state.p)
            self.ball.update_enableOld(self.ball.enabl)

    def _STELLA_Write_Enam0(self, data):
            self.missile0.update_enam(data)

    def _STELLA_Write_Enam1(self, data):
            self.missile1.update_enam(data)

    def _STELLA_Write_Enabl(self, data):
            self.ball.update_enabl(data)

    def _STELLA_Write_Hmp0(self, data):
            self.nextLine.hmp[0] = data

    def _STELLA_Write_Hmp1(self, data):
            self.nextLine.hmp[1] = data

    def _STELLA_Write_Hmm0(self, data):
            self.nextLine.hmm[0] = data

    def _STELLA_Write_Hmm1(self, data):
            self.nextLine.hmm[1] = data

    def _STELLA_Write_Hmbl(self, data):
            self.nextLine.hmbl = data

    def _STELLA_Write_Hmove(self, data):
            self._hmove()

    def _STELLA_Write_Hclr(self, data):
            self.nextLine.hmp[0] = 0 
            self.nextLine.hmp[1] = 0 
            self.nextLine.hmm[0] = 0 
            self.nextLine.hmm[1] = 0 
            self.nextLine.hmbl   = 0

    def _STELLA_Write_Vdelp0(self, data):
            self.p0_state.update_vdelp(data)

    def _STELLA_Write_Vdelp1(self, data):
            self.p1_state.update_vdelp(data)

    def _STELLA_Write_Vdelbl(self, data):
            self.ball.update_vdelbl(data)

    def _STELLA_Write_Cxclr(self, data):
            self._collision_state.clear()

    def _screen_scan(self, next_line, display_lines):

      FUTURE_PIXELS = 1
    
      last_screen_pos = self._last_screen_update_clock - self._screen_start_clock
      screen_pos      = self.clocks.system_clock       - self._screen_start_clock + FUTURE_PIXELS
    
      y_start = int(last_screen_pos/Stella.HORIZONTAL_TICKS) - self.START_DRAW_Y
      y_stop  = int(screen_pos/Stella.HORIZONTAL_TICKS) - self.START_DRAW_Y

      if y_stop < (self.END_DRAW_Y - self.START_DRAW_Y):

        priority_ctrl = (0 == next_line.ctrlpf & self.PF_PRIORITY)
        nl_pColor0  = next_line.pColor[0]
        nl_pColor1  = next_line.pColor[1]
        nl_pfColor  = next_line.playfieldColor
        nl_bgColor  = next_line.backgroundColor

        p0_scan = self.p0_state.get_player_scan()
        p1_scan = self.p1_state.get_player_scan()
        pf_scan = self.playfield_state.get_playfield_scan()
        m0_scan = self.missile0.get_missile_scan()
        m1_scan = self.missile1.get_missile_scan()
        bl_scan = self.ball.get_ball_scan()

        x_start = 0
        if (last_screen_pos % Stella.HORIZONTAL_TICKS) >= Stella.HORIZONTAL_BLANK:
            x_start = (last_screen_pos % Stella.HORIZONTAL_TICKS) - Stella.HORIZONTAL_BLANK

        last_x_stop = 0
        if (screen_pos % Stella.HORIZONTAL_TICKS) >= Stella.HORIZONTAL_BLANK:
          last_x_stop = screen_pos % Stella.HORIZONTAL_TICKS - Stella.HORIZONTAL_BLANK

        for y in range(y_start, y_stop+1):
    
          if y == y_stop:
            x_stop = last_x_stop
          else:
            x_stop = self.FRAME_WIDTH
    
          current_y_line = display_lines[y]
          for x in range(x_start, x_stop):
    
            # TODO: Check the 'score' color application.
            #  pf color set to either 'p0' or 'p1' depending on which half of
            #  the screen is being draw.
            # ie: if (0 == next_line.ctrlpf & self.PF_SCORE):

            pf = pf_scan[x]
            bl = bl_scan[x]
            m1 = m1_scan[x]
            p1 = p1_scan[x]
            m0 = m0_scan[x]
            p0 = p0_scan[x]

            # Priorities (bit 2 set):  Priorities (bit 2 clear):
            #  PF, BL                   P0, M0
            #  P0, M0                   P1, M1
            #  P1, M1                   PF, BL
            #  BK                       BK
            pixelColor = nl_bgColor
            hits = 0
            if priority_ctrl:
              if pf or bl: 
                  pixelColor = nl_pfColor
                  hits += bl + pf
              if p1 or m1: 
                  pixelColor = nl_pColor1
                  hits += m1 + p1
              if p0 or m0: 
                  pixelColor = nl_pColor0
                  hits += m0 + p0
            else:
              if p1 or m1: 
                  pixelColor = nl_pColor1
                  hits += m1 + p1
              if p0 or m0: 
                  pixelColor = nl_pColor0
                  hits += m0 + p0
              if pf or bl: 
                  pixelColor = nl_pfColor
                  hits += bl + pf

            if hits > 1:
                self._collision_state.update_collisions(p0, p1, m0, m1, bl, pf)

#       Display scan 'start position'.
#            ps0 = self.p0_state._pos_start
#            ps1 = self.p1_state._pos_start
#            if x == ps0:
#                pixelColor = self._colors.get_color(2)
#            if x == ps1:
#                pixelColor = self._colors.get_color(3)
#
            current_y_line[x] = pixelColor

          x_start = 0
    
      self._last_screen_update_clock = self.clocks.system_clock + FUTURE_PIXELS

    @staticmethod
    def nusize(nusiz):
        if 0 == (nusiz & 0x7):
            (number, size, gap) = (1, 1, 0)
        elif 1 == (nusiz & 0x7):
            (number, size, gap) = (2, 1, 2)
        elif 2 == (nusiz & 0x7):
            (number, size, gap) = (2, 1, 4)
        elif 3 == (nusiz & 0x7):
            (number, size, gap) = (3, 1, 2)
        elif 4 == (nusiz & 0x7):
            (number, size, gap) = (2, 1, 8)
        elif 5 == (nusiz & 0x7):
            (number, size, gap) = (1, 2, 0)
        elif 6 == (nusiz & 0x7):
            (number, size, gap) = (3, 1, 4)
        elif 7 == (nusiz & 0x7):
            (number, size, gap) = (1, 4, 0)
        return (number, size, gap)

    def _update_scans(self):
        if self._is_update_time:
            tmp = time.clock()
            print(tmp - self._debug_display_time)
            self._debug_display_time = tmp

            self._is_update_time = False

            self.driver_update_display()

    def _draw_display(self):
        self.poll_events()
        self.driver_draw_display()

    def _hmove(self):

        self.p0_state.resp  = (self.p0_state.resp - self._hmove_clocks(self.nextLine.hmp[0])) % Stella.FRAME_WIDTH
        self.p1_state.resp  = (self.p1_state.resp - self._hmove_clocks(self.nextLine.hmp[1])) % Stella.FRAME_WIDTH

        self.missile0.resm  = (self.missile0.resm - self._hmove_clocks(self.nextLine.hmm[0])) % Stella.FRAME_WIDTH
        self.missile1.resm  = (self.missile1.resm - self._hmove_clocks(self.nextLine.hmm[1])) % Stella.FRAME_WIDTH
        self.ball.resbl     = (self.ball.resbl - self._hmove_clocks(self.nextLine.hmbl)) % Stella.HORIZONTAL_TICKS

        self.p0_state.update()
        self.p1_state.update()
        self.missile0.update()
        self.missile1.update()
        self.ball.update()

    def _hmove_clocks(self, hm):
        # hm - int8
        # Need to ensure 'hm' maintains negative when shifted.
        clock_shift = 0
        # 'hm >= 0x80' is negative move.
        clock_shift = ctypes.c_byte(hm).value >> 4
        
        # If hmove is on the '74th' CPU cycle of the scan line, special case.
        if ((((self.clocks.system_clock - self._screen_start_clock) % Stella.HORIZONTAL_TICKS))/3 == 73):
          clock_shift = clock_shift + 8

        return clock_shift

    def _write_vsync(self, data):
        if False == self._is_vsync:
            if self.VSYNC_ON == (data & self.VSYNC_MASK):
                self._is_update_time = True
                self._is_vsync = True
        else:
            if self.VSYNC_OFF == (data & self.VSYNC_MASK):
                self._is_vsync = False
                self._vsync_debug_output_clock = self.clocks.system_clock 
                self._screen_start_clock = self.clocks.system_clock - Stella.HORIZONTAL_TICKS + (Stella.HORIZONTAL_TICKS - self.clocks.system_clock + self._screen_start_clock) % Stella.HORIZONTAL_TICKS
                self._last_screen_update_clock = self._screen_start_clock

    def _write_vblank(self, data):
        if data & self.INPUT_45_LATCH_MASK:
            self._is_input_latched = True
        else:
            self._is_input_latched = False

        if (data & self.BLANK_PADDLE_RECHARGE) == self.BLANK_PADDLE_RECHARGE:
            self._paddle_start_clock = self.clocks.system_clock

        if (data & self.BLANK_MASK) == self.BLANK_ON:
            self._is_blank = True
        elif (data & self.BLANK_MASK) == self.BLANK_OFF:
            self._is_blank = False

    def _write_wsync(self, data):
        if (self.clocks.system_clock - self._screen_start_clock) % Stella.HORIZONTAL_TICKS > 3:
          self.clocks.system_clock += Stella.HORIZONTAL_TICKS - (self.clocks.system_clock - self._screen_start_clock)%Stella.HORIZONTAL_TICKS

    def _write_rsync(self, data):
        FUDGE = 3
        if (self.clocks.system_clock - self._screen_start_clock) > 3:
          self.clocks.system_clock += Stella.HORIZONTAL_TICKS - (self.clocks.system_clock - self._screen_start_clock + FUDGE) % Stella.HORIZONTAL_TICKS 

class StellaInstrumentRecord(object):
    """ Record read/write calls, to allow replay/debugging.
        Generated script can be run to replay.
    """

    @staticmethod
    def instrumentStella(stella_instance, file_name, audio_only):
        import StringIO
        output = open(file_name, 'w')

        output.write(StellaInstrumentRecord.stella_record_header())

        def _decorator(func):
          """ Debug decorator for stella """
          def func_wrapper(*data):
              if (audio_only == False):
                output.write("# %s (%s)\n"%(func.__name__, func.__module__))
                output.write("dummy_clock.system_clock = %s\n"%(stella_instance.clocks.system_clock))
                output.write("stella_instance.%s%s\n"%(func.__name__, data))
              return func(*data)
          return func_wrapper

        def _write_decorator(func):
          """ Debug decorator specifically for stella write functions"""
          def func_wrapper(*data):
              comment_string = "%s (%s)"%(
                      stella_instance._write_function[data[0] & 0x3F].__name__, 
                      stella_instance._write_function[data[0] & 0x3F].__module__)
              if ((data[0] & 0x3F) != data[0]):
                comment_string  += " [address = %s]"%(data[0] & 0x3F)

              if ((audio_only == False) or (("audio" in comment_string) or ("Vsync" in comment_string))):
#                output.write("#%s\n"%(str(stella_instance.get_save_state())))
                output.write("# %s\n"%(comment_string))
                output.write("dummy_clock.system_clock = %s\n"%(stella_instance.clocks.system_clock))
                output.write("stella_instance.%s%s\n"%(func.__name__, data))
              return func(*data)
          return func_wrapper

        stella_instance.read  = _decorator(stella_instance.read )
        stella_instance.write = _write_decorator(stella_instance.write)

    @staticmethod
    def stella_record_header():
        return """
# Debugging tip: To render 'partial' displays/check progress add
#
# stella_instance.driver_update_display() # Draw what's available.
# time.sleep(5)
#
import time
from pytari2600.test.test_stella_replay import DummyClocks as DummyClocks
#from pytari2600.test.test_stella_replay import DummyAudio as DummyAudio
from pytari2600.audio.pygameaudio import PygameStretchTIA_Sound as DummyAudio
from pytari2600.test.test_stella_replay import DummyInputs as DummyInputs
from pytari2600.graphics.pygamestella import PygameStella as stella

dummy_clock = DummyClocks()
dummy_inputs = DummyInputs()
stella_instance = stella(dummy_clock, dummy_inputs, DummyAudio)
"""

