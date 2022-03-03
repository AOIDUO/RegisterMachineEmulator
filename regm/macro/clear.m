import "regm/macro/goto.m" as GOTO
LOOP: decjz $0 2
GOTO LOOP

# -----------------------------------------
# decjz $0 2+instr
# GOTO 0
