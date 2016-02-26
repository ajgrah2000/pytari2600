import unittest

import pytari2600.audio.tiasound as tiasound
import sys

class TestTiaSound(unittest.TestCase):
    def test_poly4(self):
        poly5_state = 0
        for j in range(0xF):
            audio_ctrl = j
            poly4_state = 0xF
            for i in range(20):
                ref_poly4_state = self.reference_poly4(audio_ctrl, poly5_state, poly4_state)
                poly4_state = tiasound.TIA_Sound.poly4(audio_ctrl, poly5_state, poly4_state)
                self.assertEqual(poly4_state, ref_poly4_state)

    def test_poly5(self):
        poly4_state = 0x6
        for j in range(0x1F):
            audio_ctrl = j
            poly5_state = j
            for i in range(40):
                ref_poly5_state = self.reference_poly5(audio_ctrl, poly5_state, poly4_state)
                poly5_state = tiasound.TIA_Sound.poly5(audio_ctrl, poly5_state, poly4_state)
                self.assertEqual(poly5_state, ref_poly5_state)

    def test_poly5_4_combo(self):
        for j in range(0x10):
            audio_ctrl = j
#            sys.stdout.write("(%s) - "%(audio_ctrl))
            next_poly5 = poly5_state = 0x1F
            next_poly4 = poly4_state = 0xF

            for i in range(260):
                ref_poly5_state = self.reference_poly5(audio_ctrl, poly5_state, poly4_state)
                next_poly5 = tiasound.TIA_Sound.poly5(audio_ctrl, poly5_state, poly4_state)
                self.assertEqual(ref_poly5_state, next_poly5)

                if tiasound.TIA_Sound.poly5clk(audio_ctrl, poly5_state):
                    ref_poly4_state = self.reference_poly4(audio_ctrl, poly5_state, poly4_state)
                    next_poly4 = tiasound.TIA_Sound.poly4(audio_ctrl, poly5_state, poly4_state)
                    poly4_state = next_poly4
                    self.assertEqual(ref_poly4_state, poly4_state)

#                sys.stdout.write("%d"%(poly4_state & 1))
                poly5_state = next_poly5
#            print ""

    def test_hex_combo(self):
        for audio_ctrl in range(0x10):
            for poly5_state in range(0x20):
                ref_poly5clk = self.reference_poly5clk(audio_ctrl, poly5_state)
                p5clk = tiasound.TIA_Sound.poly5clk(audio_ctrl, poly5_state)
                self.assertEqual(p5clk, ref_poly5clk)

                for poly4_state in range(0x10):
                    ref_poly4_state = self.reference_poly4(audio_ctrl, poly5_state, poly4_state)
                    p4 = tiasound.TIA_Sound.poly4(audio_ctrl, poly5_state, poly4_state)

                    ref_poly5_state = self.reference_poly5(audio_ctrl, poly5_state, poly4_state)
                    p5 = tiasound.TIA_Sound.poly5(audio_ctrl, poly5_state, poly4_state)

                    self.assertEqual(p4, ref_poly4_state)
                    self.assertEqual(p5, ref_poly5_state)

    # Clock poly 4, return new poly4 state
    @staticmethod
    def reference_poly4(audio_ctrl, poly5_state, poly4_state):

        i = not (audio_ctrl & 0xF) or  \
            (not (audio_ctrl & 0xC) and (((poly4_state & 0x3) != 0x3) and (poly4_state & 0x3) and ((poly4_state & 0xF) != 0xA))) or \
            (((audio_ctrl & 0xC) == 0xC) and  (poly4_state & 0xC) and not(poly4_state & 0x2)) or \
            (((audio_ctrl & 0xC) == 0x4) and not(poly4_state & 0x8)) or \
            (((audio_ctrl & 0xC) == 0x8) and not(poly5_state & 0x1))

        poly4Output = (0x7 ^ (poly4_state >> 1)) | i << 3

        return poly4Output

    # Clock poly 5, return new poly5 state
    def reference_poly5(self, audio_ctrl, poly5_state, poly4_state):

        in_5 =    not(audio_ctrl & 0xF) or \
                  (((audio_ctrl & 0x3) or ((poly4_state & 0xF) == 0xA)) and not(poly5_state & 0x1F)) or \
                  not((((audio_ctrl & 0x3) or not(poly4_state & 0x1)) and (not(poly5_state & 0x8) or not(audio_ctrl & 0x3))) ^ (poly5_state & 0x1))

        poly5Output = (poly5_state >> 1) | (in_5 << 4)

        return poly5Output

    @staticmethod
    def reference_poly5clk(audio_ctrl, poly5_state):
        clockoutput = (((audio_ctrl & 0x3) != 0x2) or (0x2 == (poly5_state & 0x1E))) and \
                      (((audio_ctrl & 0x3) != 0x3) or (poly5_state & 0x1))

        return clockoutput

class TestStretch(unittest.TestCase):
    def test_stretch(self):
        stretch = tiasound.Stretch()
        a = [1,0,1,0,1,0,1,0]
        print("orig:", a)
        print(stretch.stretch(a))

        stretch.rate = 80
        b = stretch.stretch(a)
        print(b)

        stretch.rate = 70
        print(stretch.stretch(a))
        print(stretch.stretch(a))

        stretch.rate = 120
        print(stretch.stretch(a))

if __name__ == '__main__':
    unittest.main()
