from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List, Union, Optional, Tuple

from pytest import param

class Opcode(Enum):
	DECJZ = auto()
	INC = auto()

@dataclass
class Param:
	value: Any = None

	def __repr__(self) -> str: 
		str(self.value)


class Instr:
	def __init__(self, opcode : Opcode, params : List[Param], label=None):
		self.opcode = opcode
		self.params = params
		self.label = label
	pass