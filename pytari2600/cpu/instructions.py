import ctypes

class Reading(object):
    def __init__(self, pc_state, memory):
        self.pc_state = pc_state
        self.memory = memory

    def get_reading_time(self):
        return 2*self.pc_state.CYCLES_TO_CLOCK

    def read(self, address):
        return self.memory.read(address)

class NullReading(Reading):
    def __init__(self, pc_state, memory):
        super(NullReading, self).__init__(pc_state, memory)

    def read(self, address):
        return 0

    def get_reading_time(self):
        return self.pc_state.CYCLES_TO_CLOCK

class AccumulatorReading(Reading):
    def __init__(self, pc_state, memory):
        super(AccumulatorReading, self).__init__(pc_state, memory)

    def read(self, address):
        return self.pc_state.A.get_value()

    def get_reading_time(self):
        return self.pc_state.CYCLES_TO_CLOCK

class Writing(object):
    def __init__(self, pc_state, memory):
        self.pc_state = pc_state
        self.memory = memory

    def write(self, address, data):
        self.memory.write(address, data)

    def get_writing_time(self):
        return 2*self.pc_state.CYCLES_TO_CLOCK

class RegWriting(Writing):
    def __init__(self, pc_state, memory):
        super(RegWriting, self).__init__(pc_state, memory)

    def get_writing_time(self):
        return self.pc_state.CYCLES_TO_CLOCK

class NullWriting(Writing):
    def __init__(self, pc_state, memory):
        super(NullWriting, self).__init__(pc_state, memory)

    def write(self, address, data):
        pass

    def get_writing_time(self):
        return 0

class AccumulatorWriting(Writing):
    def __init__(self, pc_state, memory):
        super(AccumulatorWriting, self).__init__(pc_state, memory)

    def write(self, address, data):
        self.pc_state.A.set_value(data)

    def get_writing_time(self):
        return self.pc_state.CYCLES_TO_CLOCK

class InstructionExec(object):
    def __init__(self, pc_state):
        self.pc_state = pc_state

    def NOP_exec(self, data):
        """NOP"""
        return int(data)

    def OR_exec(self, data):
        """OR"""
        self.pc_state.A.set_value(self.pc_state.A.get_value() | int(data))
        self.set_status_NZ(self.pc_state.A.get_value())
        return 0

    def ASL_exec(self, data):
        """ASL"""
        self.pc_state.P.set_C((int(data) >> 7) & 0x1)
        data = (int(data) << 1) & 0xFF
        self.set_status_NZ(int(data))
        return int(data)

    def AND_exec(self, data):
        """AND"""
        self.pc_state.A.set_value(self.pc_state.A.get_value() & int(data))
        self.set_status_NZ(self.pc_state.A.get_value())
        return 0

    def CLC_exec(self, data):
        """CLC"""
        self.pc_state.P.set_C(0)
        return 0

    def CLD_exec(self, data):
        """CLD"""
        self.pc_state.P.set_D(0)
        return 0

    def CLI_exec(self, data):
        """CLI"""
        self.pc_state.P.set_I(0)
        return 0

    def CLV_exec(self, data):
        """CLV"""
        self.pc_state.P.set_V(0)
        return 0

    def SEC_exec(self, data):
        """SEC"""
        self.pc_state.P.set_C(1)
        return 0

    def SED_exec(self, data):
        """SED"""
        self.pc_state.P.set_D(1)
        return 0

    def SEI_exec(self, data):
        """SEI"""
        self.pc_state.P.set_I(1)
        return 0

    def BIT_exec(self, data):
        """BIT"""
        self.pc_state.P.set_N((0,1)[0x80 == (int(data) & 0x80)])
        self.pc_state.P.set_V((0,1)[0x40 == (int(data) & 0x40)])
        self.pc_state.P.set_Z((0,1)[(self.pc_state.A.get_value() & int(data)) == 0x0])
        return 0

    def ROL_exec(self, data):
        """ROL"""
        t8 = ((int(data) << 1) | self.pc_state.P.get_C()) & 0xFF
        self.pc_state.P.set_C((int(data) >> 7) & 1)
        self.set_status_NZ(t8)
        return t8

    def EOR_exec(self, data):
        """EOR"""
        self.pc_state.A.set_value(self.pc_state.A.get_value() ^ int(data))
        self.set_status_NZ(self.pc_state.A.get_value())
        return 0

    def LSR_exec(self, data):
        """LSR"""
        self.pc_state.P.set_C(int(data) & 0x1)
        data = int(data) >> 1
        self.set_status_NZ(int(data))
        return int(data)

    def ROR_exec(self, data):
        """ROR"""
        t8 = ((int(data) >> 1) | (self.pc_state.P.get_C() << 7)) & 0xFF
        self.pc_state.P.set_C(int(data) & 1)
        self.set_status_NZ(t8)
        return t8

    def LDY_exec(self, data):
        """LDY"""
        self.pc_state.Y.set_value(int(data))
        self.set_status_NZ(self.pc_state.Y.get_value())
        return 0

    def LDA_exec(self, data):
        """LDA"""
        self.pc_state.A.set_value(int(data))
        self.set_status_NZ(self.pc_state.A.get_value())
        return 0

    def LDX_exec(self, data):
        """LDX"""
        self.pc_state.X.set_value(int(data))
        self.set_status_NZ(self.pc_state.X.get_value())
        return 0

    def CMP_exec(self, data):
        """CMP"""
        self.cmp(self.pc_state.A.get_value(), int(data))
        return 0

    def CPX_exec(self, data):
        """CPX"""
        self.cmp(self.pc_state.X.get_value(), int(data))
        return 0

    def CPY_exec(self, data):
        """CPY"""
        self.cmp(self.pc_state.Y.get_value(), int(data))
        return 0

    def ADC_exec(self, data):
        """ADC"""
        self.pc_state.A.set_value(self.addc(self.pc_state.A.get_value(), int(data), self.pc_state.P.get_C()))
        return 0

    def SBC_exec(self, data):
        """SBC"""
        self.pc_state.A.set_value(self.subc(self.pc_state.A.get_value(), int(data), 1 - self.pc_state.P.get_C()))
        return 0

    def INC_exec(self, data):
        """INC"""
        data += 1
        self.set_status_NZ(int(data))
        return int(data)

    def TNoStatus_exec(self, data):
        """TNoStatus"""
        return int(data)

    def TStatus_exec(self, data):
        """TStatus"""
        self.set_status_NZ(int(data))
        return int(data)

    def STA_exec(self, data):
        """STA"""
        return self.pc_state.A.get_value()

    def STY_exec(self, data):
        """STY"""
        return self.pc_state.Y.get_value()

    def STX_exec(self, data):
        """STX"""
        return self.pc_state.X.get_value()

    def SAX_exec(self, data):
        """SAX"""
        return self.pc_state.A.get_value() & self.pc_state.X.get_value()

    def DEC_exec(self, data):
        """DEC"""
        data -= 1
        self.set_status_NZ(int(data))
        return int(data)

    def DCP_exec(self, data):
        """DCP"""
#      TODO: Fix cycle times.
#    DCM abcd        ;CF cd ab    ;No. Cycles= 6
#    DCM abcd,X      ;DF cd ab    ;            7
#    DCM abcd,Y      ;DB cd ab    ;            7
#    DCM ab          ;C7 ab       ;            5
#    DCM ab,X        ;D7 ab       ;            6
#    DCM (ab,X)      ;C3 ab       ;            8
#    DCM (ab),Y      ;D3 ab       ;            8
        data -= 1
        self.set_status_NZ(int(data))
        self.cmp(self.pc_state.A.get_value(), int(data))
        return data

#   Illigal instructions.
    def SLO_exec(self, data):
        """SLO"""
        self.pc_state.P.set_C((int(data) >> 7) & 0x1)
        data = (int(data) << 1) & 0xFF
        self.pc_state.A.set_value(self.pc_state.A.get_value() | int(data))
        self.set_status_NZ(self.pc_state.A.get_value())
        return self.pc_state.A.get_value()

    def LAX_exec(self, data):
        """LAX"""
        # Undocumented op code
        self.pc_state.X.set_value(int(data))
        self.pc_state.A.set_value(int(data))
        self.set_status_NZ(self.pc_state.X.get_value())
        return 0

    def ASR_exec(self, data):
        """ASR"""
        # Undocumented op code
        self.pc_state.A.set_value(((self.pc_state.A.get_value() & int(data)) >> 1) & 0x7F)
        self.set_status_NZ(self.pc_state.A.get_value())
        return 0

    def SBX_exec(self, data):
        """STB"""
        # Undocumented op code
        self.pc_state.X.set_value(self.pc_state.A.get_value() & self.pc_state.X.get_value())
        self.pc_state.X.set_value(self.subc(self.pc_state.X.get_value(), int(data), 0))
        return 0


    def set_status_NZ(self, value):
        self.pc_state.P.set_N((0,1)[0x80 == (value & 0x80)])
        self.pc_state.P.set_Z((0,1)[0x00 == (value & 0xFF)])

    def addc(self, a, b, c):

        if 0 == self.pc_state.P.get_D():
            r  = ctypes.c_short(a + b + c).value
            rc = ctypes.c_byte(a + b + c).value
            self.pc_state.P.set_N((0,1)[0x80 == (rc & 0x80)])
            self.pc_state.P.set_Z((0,1)[rc == 0x0])
            self.pc_state.P.set_V((0,1)[rc != r])   # Overflow

            r = ((a & 0xFF) + (b & 0xFF) + c) & 0xFFFF
            self.pc_state.P.set_C((0,1)[0x100 == (r & 0x100)])
            result = (a + b + c)
        elif 1 == self.pc_state.P.get_D():
            # Decimal Addition
            # FIXME need to fix flags
            #
            r = ctypes.c_short(((a >> 4) & 0xF)* 10+ ((a & 0xF) %10) + ((b>>4) & 0xF)* 10 + ((b & 0xF) %10) + c).value
            rc = ctypes.c_byte(a + b + c).value # ???? TODO
            self.pc_state.P.set_N((0,1)[r < 0])
            self.pc_state.P.set_Z((0,1)[rc == 0x0])
            # self.pc_state.P.V = (rc != r) ? 1:0;   # Overflow

            self.pc_state.P.set_C((0,1)[(r > 99) or (r < 0)])
            result = ((((int(r/10) % 10) << 4) & 0xf0) + (r%10))

        return result & 0xFF

    def subc(self, a, b, c):

        if 0 == self.pc_state.P.get_D():
            r  = ctypes.c_short(ctypes.c_byte(a).value - ctypes.c_byte(b).value - ctypes.c_byte(c).value).value
            rs = ctypes.c_byte((a - b - c) & 0xFF).value
            self.pc_state.P.set_N((0,1)[0x80 == (rs & 0x80)]) # Negative
            self.pc_state.P.set_Z((0,1)[rs == 0])   # Zero
            self.pc_state.P.set_V((0,1)[r != rs])   # Overflow

            r = a - b - c 
            self.pc_state.P.set_C((1,0)[0x100 == (r & 0x100)]) # Carry (not borrow
            result = a - b - c
        elif 1 == self.pc_state.P.get_D():
            # Decimal subtraction
            # FIXME need to fix flags

            r = ctypes.c_short(((a >> 4) & 0xF)* 10+ ((a & 0xF) %10) - (((b>>4) & 0xF)* 10 + ((b & 0xF) %10)) - c).value

            # rc = a + b + c
            self.pc_state.P.set_N((0,1)[r < 0])
            self.pc_state.P.set_Z((0,1)[r == 0x0])
            #  Need to check/fix conditions for V
            # self.pc_state.P.V = (rc != r) ? 1:0;   # Overflow
            self.pc_state.P.set_V(1)   # Overflow

            self.pc_state.P.set_C((0,1)[(r >= 0) and (r <= 99)])
            result = (((int(r/10) % 10) << 4) & 0xf0) + (r%10)

        return result & 0xFF

    def cmp(self, a, b):
        r = ctypes.c_short(ctypes.c_byte(a).value - ctypes.c_byte(b).value).value
        rs = ctypes.c_byte(a - b).value
        self.pc_state.P.set_N((0,1)[0x80 == (rs & 0x80)])    # Negative
        self.pc_state.P.set_Z((0,1)[rs == 0])              # Zero
        r = (a & 0xFF) - (b & 0xFF)
        self.pc_state.P.set_C((1,0)[0x100 == (r & 0x100)]) # Carry (not borrow)

class Instruction(object):

    def __init__(self, clocks, pc_state, instruction_exec):
        self.clocks = clocks
        self.pc_state = pc_state
        self.instruction_exec = instruction_exec

    def execute(self):
        pass

    def _exec(self, data):
        return self.instruction_exec(data)

    def page_clocks_delay(self, a, b):
        # If pages don't match, add a cycle.
        if (a & 0xF00) != (b & 0xF00):
            self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

class ReadWriteInstruction(Instruction):
    def __init__(self, clocks, pc_state, address, read, write, instruction_exec, additional_delay = 0):
        super(ReadWriteInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.pc_state         = pc_state
        self.address          = address
        self.read             = read
        self.write            = write
        self.additional_delay = additional_delay 

    def execute(self):
        a = self.address
        r = self.read
        w = self.write

        addr         = a.address(True)
 
        execute_time = a.get_addressing_time()
        value        = r.read(addr)

        execute_time += r.get_reading_time()
        data = self._exec(value) & 0xFF
        self.clocks.system_clock   += execute_time + self.additional_delay + w.get_writing_time()

        w.write(addr, data)

        #print ("%s $%x %s -> %s (+%d)"%(str(self.instruction_exec.__doc__), addr, a.address.__doc__, value, execute_time))

        self.pc_state.PC += a.get_addressing_size() + 1

class BreakInstruction(Instruction):
    """BreakInstruction"""

    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(BreakInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        adl = self.memory.read(0xFFFE)

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.write(self.pc_state.S.get_value(), self.pc_state.get_PCH())
        self.pc_state.S -= 1

        self.pc_state.PC += 1
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.write(self.pc_state.S.get_value(), self.pc_state.get_PCL())
        self.pc_state.S -= 1

        # The 'B' flag, only alters the value on the stack, not ongoing status.
        self.pc_state.P.set_B(1)
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.write(self.pc_state.S.get_value(), self.pc_state.P.value)
        self.pc_state.S -= 1
        self.pc_state.P.set_B(0)

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        adh = self.memory.read(0xFFFF) & 0xFF

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC = adl + (adh << 8)
        #print ("%s"%(str(self.__doc__)))

class JumpSubRoutineInstruction(Instruction):
    """JumpSubRoutineInstruction"""
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(JumpSubRoutineInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        adl = self.memory.read(self.pc_state.PC)

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

        # Increment before store, to catch low to high carry.
        self.pc_state.PC += 1
        self.memory.write(self.pc_state.S.get_value(), self.pc_state.get_PCH())
        self.pc_state.S -= 1

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.write(self.pc_state.S.get_value(), self.pc_state.get_PCL())
        self.pc_state.S -= 1

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        adh = self.memory.read(self.pc_state.PC)

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC = adl + (adh << 8)

        #print ("%s"%(str(self.__doc__)))

class ReturnFromSubRoutineInstruction(Instruction):
    """ReturnFromSubRoutineInstruction"""
    
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(ReturnFromSubRoutineInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        # T1 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        # T2 - Stack Ptr
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        # T3 - Stack Ptr + 1 -> PCL
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.set_PCL(self.memory.read(self.pc_state.S.get_value()))
        # T4 - Stack Ptr + 1 -> PCL
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.set_PCH(self.memory.read(self.pc_state.S.get_value()))
        # T5 - discarded
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.read(self.pc_state.PC)
        # T0 - Next instruction
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1

        #print ("%s"%(str(self.__doc__)))

class ReturnFromInterrupt(Instruction):
    """ReturnFromInterrupt"""

    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(ReturnFromInterrupt, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.P.value = self.memory.read(self.pc_state.S.get_value())

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.set_PCL(self.memory.read(self.pc_state.S.get_value()))

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.set_PCH(self.memory.read(self.pc_state.S.get_value()))

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.read(self.pc_state.PC)

        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

        #print ("%s"%(str(self.__doc__)))

class BranchInstruction(Instruction):
    """BranchInstruction"""

    def __init__(self, clocks, pc_state, memory, condition_mask, condition, instruction_exec):
        super(BranchInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory
        self.condition_mask = condition_mask
        self.condition = condition

    def execute(self):
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        if (self.pc_state.P.value & self.condition_mask) == self.condition:
            tmp16 = self.pc_state.PC
            delta = self.memory.read(self.pc_state.PC + 1) & 0xFF
            if delta & 0x80:
                self.pc_state.PC += delta - 0x100
            else:
                self.pc_state.PC += delta
            # If branch to same page add 1, else add 2
            # TODO: Confirm if starting address is 'tmp16' or 'tmp16+2'
            self.page_clocks_delay(tmp16+2, self.pc_state.PC+2)
            self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

        self.pc_state.PC += 2
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

        #print ("%s"%(str(self.__doc__)))

class SingleByteInstruction(Instruction):
    """SingleByteInstruction"""
    def __init__(self, clocks, pc_state, src, dst, instruction_exec):
        super(SingleByteInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.src = src
        self.dst = dst

    def execute(self):
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.dst.set_value(self.instruction_exec(self.src))
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        #print ("%s -> (+??)"%(str(self.instruction_exec.__doc__)))

class JumpInstruction(Instruction):
    """JumpInstruction"""

    def __init__(self, clocks, pc_state, address, instruction_exec):
        super(JumpInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.address = address

    def execute(self):
        self.clocks.system_clock += 1 * self.pc_state.CYCLES_TO_CLOCK
        addr    = self.address.address(False)
        execute_time = self.address.get_addressing_time()
        self.clocks.system_clock += execute_time
        self.pc_state.PC = addr
        #print ("%s"%(str(self.__doc__)))

class PHPInstruction(Instruction):
    """PHPInstruction"""
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(PHPInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory
    def execute(self):
        # T1 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        # T2 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.P.set_B(1)
        self.pc_state.P.set_X1(1)
        self.memory.writeSp(self.pc_state.S.get_value(), self.pc_state.P.value)
        self.pc_state.S -= 1
        # T0 - Next kid
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK

        #print ("%s"%(str(self.__doc__)))

class PLPInstruction(Instruction):
    """PLPInstruction"""
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(PLPInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory
    def execute(self):
        # T1 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        # T2 Stack Ptr. (Discard data)
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.readSp(self.pc_state.S.get_value())
        # T3 Stack Ptr + 1.
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.P.value = self.memory.readSp(self.pc_state.S.get_value())
        # T0 - Next instruction
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        #print ("%s"%(str(self.__doc__)))

class PHAInstruction(Instruction):
    """PHAInstruction"""
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(PHAInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        # T1 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        # T2 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.writeSp(self.pc_state.S.get_value(), self.pc_state.A.get_value())
        self.pc_state.S -= 1
        # T0 - Next kid
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        #print ("%s"%(str(self.__doc__)))

class PLAInstruction(Instruction):
    """PLAInstruction"""
    def __init__(self, clocks, pc_state, memory, instruction_exec):
        super(PLAInstruction, self).__init__(clocks, pc_state, instruction_exec)
        self.memory = memory

    def execute(self):
        # T1 - PC + 1 
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.PC += 1
        # T2 Stack Ptr. (Discard data)
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.memory.readSp(self.pc_state.S.get_value())
        # T3 Stack Ptr + 1.
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        self.pc_state.S += 1
        self.pc_state.A.set_value(self.memory.readSp(self.pc_state.S.get_value()))
        self.set_status_NZ(self.pc_state.A.get_value())
        # T0 - Next instruction
        self.clocks.system_clock += self.pc_state.CYCLES_TO_CLOCK
        #print ("%s"%(str(self.__doc__)))

    def set_status_NZ(self, value):
        self.pc_state.P.set_N((0,1)[0x80 == (value & 0x80)])
        self.pc_state.P.set_Z((0,1)[0x00 == (value & 0xFF)])
