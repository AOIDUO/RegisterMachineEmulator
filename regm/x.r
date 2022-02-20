registers 114 514
inc r0 
inc r1
l1: decjz r0 HALT
	  decjz r1 HALT
      inc r5
      inc r114
l2: decjz r1 l1
inc r1
inc r8
decjz r1 HALT
decjz r-1 HALT