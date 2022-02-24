import "regm/macro/goto.m" as GOTO
LOOP: decjz $0 2
GOTO LOOP

# convert the above to the following: 
# decjz $0 2
# GOTO 0