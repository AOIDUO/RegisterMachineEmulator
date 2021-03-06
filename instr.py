from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Union, Optional, Tuple

from pytest import param

class Opcode(Enum):
	DECJZ = auto()
	INC = auto()
	NOP = auto()

@dataclass
class Param:
	value: Any = None

	def __repr__(self) -> str: 
		str(self.value)


class Instr:
	def __init__(self, opcode : Opcode, params : List[Param], label:str=None):
		self.opcode = opcode
		self.params = params
		self.label = label

	def __repr__(self) -> str: 
		ret = ""
		if self.label != None:
			ret += "{label}: ".format(label=self.label) 
		
		ret += "{opcode} {params}".format(opcode=self.opcode.name, params=self.params)

		return ret 
		return "{label}: {opcode} {params}".format(label=self.label.value, opcode=self.opcode.name, params=self.params) 
		
		return "{opcode} ".format(opcode=self.opcode.name) 