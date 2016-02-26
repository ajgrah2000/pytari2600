import pytari2600.cpu.instructions as instructions
import pytari2600.cpu.addressing as addressing
import pytari2600.cpu.pc_state as pc_state
import unittest

class DummyClocks(object):
    def __init__(self):
        self.system_clock = 0

class DummyMemory(object):
    def __init__(self):
        self.dummy_read     = 8
        self.dummy_read16   = 16
        self.dummy_sp_write = 19
        self.dummy_read_sp  = 23

    def read(self, address):
        return self.dummy_read

    def read16(self, address):
        return self.dummy_read16

    def readSp(self, address):
        return self.dummy_read_sp

    def write(self, address, data):
        self.dummy_write = data

    def writeSp(self, address, data):
        self.dummy_write_sp = data

class TestInstructions(unittest.TestCase):

    def test_reading(self):
        current_pc_state = pc_state.PC_State()
        memory   = DummyMemory()

        memory.dummy_read = 2
        reading = instructions.Reading(current_pc_state, memory)
        self.assertEqual(reading.get_reading_time(), 2*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(reading.read(1), 2)

        memory.dummy_read = 4
        reading = instructions.NullReading(current_pc_state, memory)
        self.assertEqual(reading.get_reading_time(), 1*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(reading.read(1), 0) # Null read does nothing

        current_pc_state.A = 8
        reading = instructions.AccumulatorReading(current_pc_state, memory)
        self.assertEqual(reading.get_reading_time(), 1*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(reading.read(1), 8)

    def test_writing(self):
        current_pc_state = pc_state.PC_State()
        memory   = DummyMemory()
        writing = instructions.Writing(current_pc_state, memory)
        writing.write(0,20)
        self.assertEqual(writing.get_writing_time(), 2*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(memory.dummy_write, 20)

        writing = instructions.NullWriting(current_pc_state, memory)
        writing.write(0,21)
        self.assertEqual(writing.get_writing_time(), 0*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(memory.dummy_write, 20) # Null write doesn't do anything

        writing = instructions.AccumulatorWriting(current_pc_state, memory)
        writing.write(0,22)
        self.assertEqual(writing.get_writing_time(), 1*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(current_pc_state.A, 22)

        writing = instructions.RegWriting(current_pc_state, memory)
        writing.write(0,23)
        self.assertEqual(writing.get_writing_time(), 1*current_pc_state.CYCLES_TO_CLOCK)
        self.assertEqual(memory.dummy_write, 23)

class TestInstructionExec(unittest.TestCase):

    def test_simple_exec(self):
        current_pc_state = pc_state.PC_State()
        instruction_exec = instructions.InstructionExec(current_pc_state)

        data = 7
        instruction_exec.NOP_exec(data)
        instruction_exec.OR_exec(data)
        instruction_exec.ASL_exec(data)
        instruction_exec.AND_exec(data)
        instruction_exec.CLC_exec(data)
        instruction_exec.CLD_exec(data)
        instruction_exec.CLI_exec(data)
        instruction_exec.CLV_exec(data)
        instruction_exec.SEC_exec(data)
        instruction_exec.SED_exec(data)
        instruction_exec.SEI_exec(data)
        instruction_exec.BIT_exec(data)
        instruction_exec.ROL_exec(data)
        instruction_exec.EOR_exec(data)
        instruction_exec.LSR_exec(data)
        instruction_exec.ROR_exec(data)
        instruction_exec.LDY_exec(data)
        instruction_exec.LDA_exec(data)
        instruction_exec.LDX_exec(data)
        instruction_exec.CMP_exec(data)
        instruction_exec.CPX_exec(data)
        instruction_exec.CPY_exec(data)
        instruction_exec.ADC_exec(data)
        instruction_exec.SBC_exec(data)
        instruction_exec.INC_exec(data)
        instruction_exec.TNoStatus_exec(data)
        instruction_exec.TStatus_exec(data)
        instruction_exec.STA_exec(data)
        instruction_exec.STY_exec(data)
        instruction_exec.STX_exec(data)
        instruction_exec.SAX_exec(data)
        instruction_exec.DEC_exec(data)
        instruction_exec.DCP_exec(data)
        instruction_exec.SLO_exec(data)
        instruction_exec.set_status_NZ(data)
        (a, b, c) = (1, 2, 3)
        instruction_exec.subc(a, b, c)
        instruction_exec.cmp(a, b)

class TestInstructions(unittest.TestCase):
    def test_execute(self):

        clocks = DummyClocks()
        clocks.system_clocks = 10000
        current_pc_state = pc_state.PC_State()
        memory   = DummyMemory()
        instruction_exec = instructions.InstructionExec(current_pc_state).OR_exec
        read  = instructions.Reading(current_pc_state, memory)
        write = instructions.Writing(current_pc_state, memory)
        address = addressing.AddressIZX(current_pc_state, memory)

        instruction = []
        instruction.append(instructions.Instruction(clocks, current_pc_state, instruction_exec))
        instruction.append(instructions.ReadWriteInstruction(clocks, current_pc_state, address, read, write, instruction_exec))
        instruction.append(instructions.BreakInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.JumpSubRoutineInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.ReturnFromSubRoutineInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.ReturnFromInterrupt(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.BranchInstruction(clocks, current_pc_state, memory, 0x80, 0x80, instruction_exec))
        instruction.append(instructions.SingleByteInstruction(clocks, current_pc_state, current_pc_state.A, current_pc_state.A, instruction_exec))
        instruction.append(instructions.JumpInstruction(clocks, current_pc_state, address, instruction_exec))
        instruction.append(instructions.PHPInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.PLPInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.PHAInstruction(clocks, current_pc_state, memory, instruction_exec))
        instruction.append(instructions.PLAInstruction(clocks, current_pc_state, memory, instruction_exec))

        for ins in instruction:
            ins.execute()

if __name__ == '__main__':
    unittest.main()
