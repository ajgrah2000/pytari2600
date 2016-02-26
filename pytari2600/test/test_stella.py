import unittest
import pytari2600.graphics.pygamestella as pygamestella
import pytari2600.graphics.stella as stella
import pytari2600.clocks as clocks
import pytari2600.inputs as inputs

class TestCollisions(unittest.TestCase):
    def test_collisions(self):
        collisions = stella.CollisionState()

        for i in range(0x40):
          p0 = i & 0x1
          p1 = (i >> 1) & 0x1
          m0 = (i >> 2) & 0x1
          m1 = (i >> 3) & 0x1
          bl = (i >> 4) & 0x1
          pf = (i >> 5) & 0x1
          collisions.update_collisions(p0, p1, m0, m1, bl, pf)

        self.assertEqual(collisions._cxmp, [0xC0, 0xC0])
        self.assertEqual(collisions._cxpfb, [0xC0, 0xC0])
        self.assertEqual(collisions._cxmfb, [0xC0, 0xC0])
        self.assertEqual(collisions._cxblpf, 0x80)
        self.assertEqual(collisions._cxppmm, 0xC0)

    def test_colors(self):
        """ Test color lookup. """
        c = pygamestella.PygameColors()
        # Check length and sample first and last color values.
        self.assertEqual(len(c.colors), 128)
        self.assertEqual(c.colors[0], 0)
        self.assertEqual(c.colors[127], 0xfce08c)

class TestDrawing(unittest.TestCase):

    def reference_update_playfield(self, pf0, pf1, pf2, ctrlpf, x):
        drawn = False
        if (x>=0) and (x < stella.Stella.FRAME_WIDTH & 0xFFFF):
            # Bit order for displaying pf1 is reverse to pf0 & pf2.
            # Order:
            # PF0: 4,5,6,7, PF1: 7,6,5,4,3,2,1,0 PF2: 0,1,2,3,4,5,6,7
            pixelWidth = 4
            shift = 0
            bits = 0
            
            i = int(x/pixelWidth)
            
            if i >= 20:
                if 0 == (ctrlpf & 0x1):
                    # right half is identical to left.
                    i = i - 20
                else:
                    # right half is reverse of left.
                    i = 39 - i
            if (i >= 0) and (i < 4):
                bits = pf0
                shift = (i + 4)
            elif ((i >= 4) and (i < 12)):
                bits = pf1
                shift = (11 - i)
            elif (i >= 12) and (i < 20):
                bits = pf2
                shift = (i - 12)
            
            bits = bits >> shift
            
            drawn = (bits & 0x1)
        return drawn

    def reference_update_player(self, nusiz, grp, refp,  resp, x):

        drawn = False

        if 0 != grp:
            (number, size, gap) = stella.Stella.nusize(nusiz)

            if resp < stella.Stella.HORIZONTAL_BLANK:
                resp = stella.Stella.HORIZONTAL_BLANK

            for n in range(number):
                bitfield = grp
                # Scale the player.
                for s in range(size):
                    for i in range(8):
                        # TODO: 'size/2' is a workaround for 'missile command'
                        # shifting of the explosion when size increases.
                        pos = (resp - stella.Stella.HORIZONTAL_BLANK + int(size/2) + i*size + s + n * gap*8) % stella.Stella.FRAME_WIDTH & 0xFF

                        if x == pos:
                            if (refp & 0x8) == 0:
                                # Check each bit
                                if (bitfield << i) & 0x80:
                                    drawn = True
                            else:
                                # Check each bit
                                if (bitfield >> i) & 0x01:
                                    drawn = True

        return drawn

    def test_update_player(self):
        test_clocks = clocks.Clock()
        test_input = inputs.Input()
        s = stella.PlayerState(test_clocks)

        test_nusiz = range(0,8)
        test_refp   = [0,0x8]
        test_resp   = range(0,159)# horizontal position - (0,HORIZONTAL_BLANK)
        test_grp    = [0x83] # Asymetric bit-field
        test_x      = range(0,68)# test x position

        draw_count = 0
        all_count = 0
        for nusiz in test_nusiz:
            for refp in test_refp:
                for resp in test_resp:
                    for grp in test_grp:
                        for x in test_x:
                            all_count += 1
                            s.nusiz = nusiz
                            s.p     = grp # don't use vdelp for this test
                            s.pOld  = grp # don't use vdelp for this test
                            s.refp  = refp
                            s.resp  = resp
                            s.vdelp = 0 # Ignore for this test
                            s.update()
                            update_player_draw = s.get_player_scan()[x]
                            reference_update_player_draw = self.reference_update_player(nusiz, grp, refp,  resp, x) 
                            if update_player_draw:
                                draw_count +=1
                            if reference_update_player_draw != update_player_draw:
                                print (nusiz, grp, refp,  resp, x)
                            self.assertEqual(reference_update_player_draw,
                                             update_player_draw)
        self.assertEqual(draw_count, 12791)
        self.assertEqual(all_count, len(test_nusiz) * 
                                    len(test_refp)  * 
                                    len(test_resp)  * 
                                    len(test_grp)   *
                                    len(test_x))

    def test_update_playfield(self):
        test_clocks = clocks.Clock()
        test_input = inputs.Input()
        s = stella.PlayfieldState()

        test_pf0    = [0,0x10,0x20,0x40,0x80]
        test_pf1    = [0,0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80]
        test_pf2    = [0,0x1,0x2,0x4,0x8,0x10,0x20,0x40,0x80]
        test_x      = range(0,21)
        test_ctrlpf = [0,1]

        draw_count = 0
        all_count = 0
        for pf0 in test_pf0:
            for pf1 in test_pf1:
                for pf2 in test_pf2:
                    for x in test_x:
                        for ctrlpf in test_ctrlpf:
                            all_count += 1
                            s.pf0    = pf0
                            s.pf1    = pf1
                            s.pf2    = pf2
                            s.ctrlpf = ctrlpf
                            s.update()
                            update_playfield = s.get_playfield_scan()[x * 4]
                            reference_update_playerfield = self.reference_update_playfield(pf0, pf1, pf2, ctrlpf, x * 4)
                            if update_playfield:
                                draw_count +=1
                            if reference_update_playerfield != update_playfield:
                                print (pf0, pf1, pf2, ctrlpf, x)
                            self.assertEqual(reference_update_playerfield,
                                             update_playfield)
        self.assertEqual(draw_count, 2214)
        self.assertEqual(all_count, len(test_pf0) * 
                                    len(test_pf1)  * 
                                    len(test_pf2)  * 
                                    len(test_x)   *
                                    len(test_ctrlpf))

if __name__ == '__main__':
    unittest.main()
