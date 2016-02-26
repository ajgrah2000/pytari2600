from . import addressing
from . import instructions
from . import pc_state

class Core(object):
    """
        CPU Core - Contains op code mappings.
    """
    def __init__(self, clocks, memory, pc_state):
        self.clocks    = clocks
        self.memory    = memory
        self.pc_state  = pc_state

        # Different addressing modes
        self.aIZX    = addressing.AddressIZX(self.pc_state, self.memory)
        self.aIZY    = addressing.AddressIZY(self.pc_state, self.memory)
        self.aIMM    = addressing.AddressIMM(self.pc_state, self.memory)
        self.aZP     = addressing.AddressZP (self.pc_state, self.memory)
        self.aZPX    = addressing.AddressZPX(self.pc_state, self.memory)
        self.aZPY    = addressing.AddressZPY(self.pc_state, self.memory)
        self.aAbs    = addressing.AddressAbs(self.pc_state, self.memory)
        self.aAbx    = addressing.AddressAbx(self.pc_state, self.memory)
        self.aAby    = addressing.AddressAby(self.pc_state, self.memory)
        self.aInd    = addressing.AddressIndirect(self.pc_state, self.memory)
        self.aAcc    = addressing.AddressAccumulator(self.pc_state, self.memory)

        # Different instruction types
        self.r       = instructions.Reading(self.pc_state, self.memory)
        self.nullR   = instructions.NullReading(self.pc_state, self.memory)
        self.aR      = instructions.AccumulatorReading(self.pc_state, self.memory)

        self.w       = instructions.Writing(self.pc_state, self.memory)
        self.regW    = instructions.RegWriting(self.pc_state, self.memory)
        self.nullW   = instructions.NullWriting(self.pc_state, self.memory)
        self.aW      = instructions.AccumulatorWriting(self.pc_state, self.memory)

        self.instruction_exe = instructions.InstructionExec(self.pc_state)

        self.instruction_lookup = [False] * 256

        self.PROGRAM_ENTRY_ADDR = 0xFFFC

        self.memory = memory

        self.pc_state.P.value = 0
        self.pc_state.PC = 0x1000

    def get_save_state(self):
        state = {}
        state['pc_state'] = self.pc_state.get_save_state()
        return state

    def set_save_state(self, state):
        self.pc_state.set_save_state(state['pc_state'])

    def reset(self):
        # 6502 Reset vector location.
        self.pc_state.PC = self.memory.read16(self.PROGRAM_ENTRY_ADDR)

    def initialise(self):
        # 6502 Reset vector location.
        self.populate_instruction_map()

    def step(self):
        op_code = self.memory.read(self.pc_state.PC)
    
        # This will raise an exception for unsupported op_code
        self.instruction_lookup[op_code].execute()

    def populate_instruction_map(self):
        dummy = pc_state.PC_Register()
        # Single byte instructions (including ASL, ROL and LSR in accumulator modes)
        self.instruction_lookup[0xEA] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.A, self.pc_state.A, self.instruction_exe.NOP_exec)

        self.instruction_lookup[0x0A] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.A, self.pc_state.A, self.instruction_exe.ASL_exec)
        self.instruction_lookup[0x4A] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.A, self.pc_state.A, self.instruction_exe.LSR_exec)
        self.instruction_lookup[0xE8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.X, self.pc_state.X, self.instruction_exe.INC_exec)
        self.instruction_lookup[0xC8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.Y, self.pc_state.Y, self.instruction_exe.INC_exec)
        self.instruction_lookup[0xCA] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.X, self.pc_state.X, self.instruction_exe.DEC_exec)
        self.instruction_lookup[0x88] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.Y, self.pc_state.Y, self.instruction_exe.DEC_exec)
        self.instruction_lookup[0x18] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.CLC_exec)
        self.instruction_lookup[0xD8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.CLD_exec)
        self.instruction_lookup[0x58] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.CLI_exec)
        self.instruction_lookup[0xB8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.CLV_exec)
    
        self.instruction_lookup[0x38] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.SEC_exec)
        self.instruction_lookup[0x78] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.SEI_exec)
        self.instruction_lookup[0xF8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, dummy, dummy, self.instruction_exe.SED_exec)
    
        # Break instruction, software 'interrupt'
        self.instruction_lookup[0x00] = instructions.BreakInstruction(self.clocks, self.pc_state, self.memory, None)
    
        # Register Transfers
        self.instruction_lookup[0x9A] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.X, self.pc_state.S, self.instruction_exe.TNoStatus_exec)
        self.instruction_lookup[0xBA] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.S, self.pc_state.X, self.instruction_exe.TNoStatus_exec)
        self.instruction_lookup[0x8A] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.X, self.pc_state.A, self.instruction_exe.TStatus_exec)
        self.instruction_lookup[0xAA] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.A, self.pc_state.X, self.instruction_exe.TStatus_exec)
        self.instruction_lookup[0xA8] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.A, self.pc_state.Y, self.instruction_exe.TStatus_exec)
        self.instruction_lookup[0x98] = instructions.SingleByteInstruction(self.clocks, self.pc_state, self.pc_state.Y, self.pc_state.A, self.instruction_exe.TStatus_exec)
    
        # ADC
        self.instruction_lookup[0x61] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x69] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x65] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x75] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x71] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x6D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x7D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.ADC_exec)
        self.instruction_lookup[0x79] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.ADC_exec)
    
        # ASL
        self.instruction_lookup[0x06] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.ASL_exec)
        self.instruction_lookup[0x16] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.ASL_exec)
        self.instruction_lookup[0x0E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.ASL_exec)
        self.instruction_lookup[0x1E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.ASL_exec)
    
        # AND
        self.instruction_lookup[0x21] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x29] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x25] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x35] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x31] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x2D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x3D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.AND_exec)
        self.instruction_lookup[0x39] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.AND_exec)
    
        # BIT
        self.instruction_lookup[0x24] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.BIT_exec)
        self.instruction_lookup[0x2C] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.BIT_exec)
    
        # CMP
        self.instruction_lookup[0xC1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xC9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xC5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xD5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xD1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xCD] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xDD] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.CMP_exec)
        self.instruction_lookup[0xD9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.CMP_exec)
    
        # CPX
        self.instruction_lookup[0xE0] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.CPX_exec)
        self.instruction_lookup[0xE4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.CPX_exec)
        self.instruction_lookup[0xEC] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.CPX_exec)
    
        # CPY
        self.instruction_lookup[0xC0] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.CPY_exec)
        self.instruction_lookup[0xC4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.CPY_exec)
        self.instruction_lookup[0xCC] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.CPY_exec)
    
        # DEC
        self.instruction_lookup[0xC6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.DEC_exec)
        self.instruction_lookup[0xD6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.DEC_exec)
        self.instruction_lookup[0xCE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.DEC_exec)
        self.instruction_lookup[0xDE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.DEC_exec)
    
        # EOR
        self.instruction_lookup[0x41] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x49] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x45] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x55] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x51] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x4D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x5D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.EOR_exec)
        self.instruction_lookup[0x59] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.EOR_exec)
    
        # INC
        self.instruction_lookup[0xE6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.INC_exec)
        self.instruction_lookup[0xF6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.INC_exec)
        self.instruction_lookup[0xEE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.INC_exec)
        self.instruction_lookup[0xFE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.INC_exec)
    
        # LDA
        self.instruction_lookup[0xA1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xA9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xA5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xB5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xB1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xAD] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xBD] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.LDA_exec)
        self.instruction_lookup[0xB9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.LDA_exec)
    
        # LDX
        self.instruction_lookup[0xA2] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.LDX_exec)
        self.instruction_lookup[0xA6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.LDX_exec)
        self.instruction_lookup[0xB6] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPY, self.r, self.nullW, self.instruction_exe.LDX_exec)
        self.instruction_lookup[0xAE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.LDX_exec)
        self.instruction_lookup[0xBE] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.LDX_exec)
    
        # LDY
        self.instruction_lookup[0xA0] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.LDY_exec)
        self.instruction_lookup[0xA4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.LDY_exec)
        self.instruction_lookup[0xB4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.LDY_exec)
        self.instruction_lookup[0xAC] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.LDY_exec)
        self.instruction_lookup[0xBC] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.LDY_exec)
    
        # LSR
        self.instruction_lookup[0x46] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.LSR_exec)
        self.instruction_lookup[0x56] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.LSR_exec)
        self.instruction_lookup[0x4E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.LSR_exec)
        self.instruction_lookup[0x5E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.LSR_exec)
    
        # OR
        self.instruction_lookup[0x01] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x09] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x05] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x15] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x11] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x0D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x1D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.OR_exec)
        self.instruction_lookup[0x19] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.OR_exec)
    
        # ROL
        self.instruction_lookup[0x26] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.ROL_exec)
        self.instruction_lookup[0x36] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.ROL_exec)
        self.instruction_lookup[0x2E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.ROL_exec)
        self.instruction_lookup[0x3E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.ROL_exec)
        self.instruction_lookup[0x2A] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAcc, self.aR, self.aW, self.instruction_exe.ROL_exec)
    
        # ROR
        self.instruction_lookup[0x66] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.ROR_exec)
        self.instruction_lookup[0x76] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.ROR_exec)
        self.instruction_lookup[0x6E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.ROR_exec)
        self.instruction_lookup[0x7E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.ROR_exec)
        self.instruction_lookup[0x6A] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAcc, self.aR, self.aW, self.instruction_exe.ROR_exec)
    
        # SBC
        self.instruction_lookup[0xE1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xE9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xE5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xF5] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xF1] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xED] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xFD] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.nullW, self.instruction_exe.SBC_exec)
        self.instruction_lookup[0xF9] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.SBC_exec)
    
        # STA
        self.instruction_lookup[0x81] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.nullR, self.regW, self.instruction_exe.STA_exec)
        self.instruction_lookup[0x85] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.nullR, self.regW, self.instruction_exe.STA_exec)
        self.instruction_lookup[0x95] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.STA_exec)
        self.instruction_lookup[0x91] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.nullR, self.regW, self.instruction_exe.STA_exec, self.pc_state.CYCLES_TO_CLOCK)
        self.instruction_lookup[0x8D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.nullR, self.regW, self.instruction_exe.STA_exec)
        self.instruction_lookup[0x9D] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.nullR, self.regW, self.instruction_exe.STA_exec, self.pc_state.CYCLES_TO_CLOCK)
        self.instruction_lookup[0x99] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.nullR, self.regW, self.instruction_exe.STA_exec, self.pc_state.CYCLES_TO_CLOCK)
    
        # SAX
        self.instruction_lookup[0x83] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.nullR, self.regW, self.instruction_exe.SAX_exec)
        self.instruction_lookup[0x87] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.nullR, self.regW, self.instruction_exe.SAX_exec)
        self.instruction_lookup[0x8F] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.nullR, self.regW, self.instruction_exe.SAX_exec)
        self.instruction_lookup[0x97] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPY, self.nullR, self.regW, self.instruction_exe.SAX_exec)
    
    
        # STX
        self.instruction_lookup[0x86] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.nullR, self.regW, self.instruction_exe.STX_exec)
        self.instruction_lookup[0x96] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPY, self.nullR, self.regW, self.instruction_exe.STX_exec)
        self.instruction_lookup[0x8E] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.nullR, self.regW, self.instruction_exe.STX_exec)
    
        # STY
        self.instruction_lookup[0x84] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.nullR, self.regW, self.instruction_exe.STY_exec)
        self.instruction_lookup[0x94] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.STY_exec)
        self.instruction_lookup[0x8C] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.nullR, self.regW, self.instruction_exe.STY_exec)
    
        # DCP
        self.instruction_lookup[0xC3] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xC7] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xD7] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xD3] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xCF] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xDF] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbx, self.r, self.w, self.instruction_exe.DCP_exec)
        self.instruction_lookup[0xDB] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.w, self.instruction_exe.DCP_exec)
    
        # JSR
        self.instruction_lookup[0x20] = instructions.JumpSubRoutineInstruction(self.clocks, self.pc_state, self.memory, None)
    
        # Barnch
        # BPL case 0x10: if (self.pc_state.P.status.N == 0)
        self.instruction_lookup[0x10] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x80, 0x00, None)
        # BMI case 0x30: if (self.pc_state.P.status.N == 1)
        self.instruction_lookup[0x30] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x80, 0x80, None)
        # BVC case 0x50: if (self.pc_state.P.status.V == 0)
        self.instruction_lookup[0x50] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x40, 0x00, None)
        # BVS case 0x70: if (self.pc_state.P.status.V == 1)
        self.instruction_lookup[0x70] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x40, 0x40, None)
        # BCC case 0x90: if (self.pc_state.P.status.C == 0)
        self.instruction_lookup[0x90] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x01, 0x00, None)
        # BCS case 0xB0: if (self.pc_state.P.status.C == 1)
        self.instruction_lookup[0xB0] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x01, 0x01, None)
        # BNE case 0xD0: self.clocks += 2*CYCLES_TO_CLOCK if (self.pc_state.P.status.Z == 0)
        self.instruction_lookup[0xD0] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x02, 0x00, None)
        # BEO case 0xF0: if (self.pc_state.P.status.Z == 1)
        self.instruction_lookup[0xF0] = instructions.BranchInstruction(self.clocks, self.pc_state, self.memory, 0x02, 0x02, None)
    
        self.instruction_lookup[0x40] = instructions.ReturnFromInterrupt(self.clocks, self.pc_state, self.memory, None)
        # RTS
        self.instruction_lookup[0x60] = instructions.ReturnFromSubRoutineInstruction(self.clocks, self.pc_state, self.memory, None)
    
        # JMP, absolute (effectively immediate)
        self.instruction_lookup[0x4C] = instructions.JumpInstruction(self.clocks, self.pc_state, self.aAbs, None)
        # JMP, indirect (effectively absolute)
        self.instruction_lookup[0x6C] = instructions.JumpInstruction(self.clocks, self.pc_state, self.aInd, None)
    
        # PHP
        self.instruction_lookup[0x08] = instructions.PHPInstruction(self.clocks, self.pc_state, self.memory, None)
        # PLP
        self.instruction_lookup[0x28] = instructions.PLPInstruction(self.clocks, self.pc_state, self.memory, None)
        # PHA
        self.instruction_lookup[0x48] = instructions.PHAInstruction(self.clocks, self.pc_state, self.memory, None)
        # PLA
        self.instruction_lookup[0x68] = instructions.PLAInstruction(self.clocks, self.pc_state, self.memory, None)
    
        # Illigal instructions
        # SLO
        self.instruction_lookup[0x07] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP, self.r, self.nullW, self.instruction_exe.SLO_exec)

        # Undocumented instructions
        self.instruction_lookup[0x04] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x14] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x34] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x44] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x54] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x64] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x74] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x80] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x82] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0x89] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0xC2] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0xD4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0xE2] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.nullR, self.regW, self.instruction_exe.NOP_exec)
        self.instruction_lookup[0xF4] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPX, self.nullR, self.regW, self.instruction_exe.NOP_exec)

        # LAX
        self.instruction_lookup[0xA7] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZP,  self.r, self.nullW, self.instruction_exe.LAX_exec)
        self.instruction_lookup[0xB7] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aZPY, self.r, self.nullW, self.instruction_exe.LAX_exec)
        self.instruction_lookup[0xAF] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAbs, self.r, self.nullW, self.instruction_exe.LAX_exec)
        self.instruction_lookup[0xBF] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aAby, self.r, self.nullW, self.instruction_exe.LAX_exec)
        self.instruction_lookup[0xA3] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZX, self.r, self.nullW, self.instruction_exe.LAX_exec)
        self.instruction_lookup[0xB3] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIZY, self.r, self.nullW, self.instruction_exe.LAX_exec)

        # ASR
        self.instruction_lookup[0x4B] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.ASR_exec)

        # SBX
        self.instruction_lookup[0xCB] = instructions.ReadWriteInstruction(self.clocks, self.pc_state, self.aIMM, self.r, self.nullW, self.instruction_exe.SBX_exec)
