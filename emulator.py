from instr import *
from typing import Any, List, Union, Optional, Tuple, Dict

class Emulator:
	
	def __init__(self, regs : List[int] , labels : Dict[str, int], instrs : List[Instr]):
		self.regs = {}
		self.labels = labels
		self.instrs = instrs

		for i in range(len(regs)):
			self.regs[i] = regs[i]

		self.labels['HALT'] = len(self.instrs) 

	def init_reg(self, addr):
		if not addr in self.regs:
			self.regs[addr] = 0

	def run(self):
		print (self.regs)
		print(self.instrs)
		print(self.labels)
		
		pc = 0
		while pc < len(self.instrs):
		
			instr = self.instrs[pc]
		
			if instr.opcode == Opcode.INC:
				addr = instr.params[0]
				self.init_reg(addr)
				self.regs[addr] += 1
				pc += 1

			elif instr.opcode == Opcode.DECJZ:
				# if R[i] = 0 then goto j , else subtract 1 from R i
				
				addr = instr.params[0]
				self.init_reg(addr)
				target_branch = instr.params[1]

				if self.regs[addr] == 0: # jump to target_branch
					pc = self.labels[target_branch]
				else: # subtract 1
					self.regs[addr] -= 1
					pc += 1
			else:
				raise Exception("Unsupported opcode")

		print (self.regs)
		pass