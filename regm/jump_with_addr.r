import "regm/macro/goto.m" as GOTO
import "regm/macro/clear.m" as CLR
registers 1 2
inc r2
CLR r0 # <- this macro is on line 1, hence add 1 to all int add reference in macro
GOTO 111
inc r0
inc r0
nop
