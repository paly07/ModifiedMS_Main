# resetValues= []
# regData = []
parity_bit = ""
resetValues = [0x80,0x80, 0x80, 0x80, 0x00, 0x00,
	            0x60, 0x80, 0x7F, 0x80, 0x7F,0x80, 0x7F, 0x38, 0x38, 0x38,
	            0x01, 0x00, 0x00, 0x00, 0x00,0x00, 0xC9,
              ]

regData = [resetValues[i] for i in range(23)]
def set_regs(bit2set, data):
	if bit2set =="FP":
		regValue = regData[17]
		regValue &= ~(0x80)
		regValue |= (data << 7) & 0x80
		regData[17] = regValue
	elif bit2set =="PR":
		regValue = regData[17]
		regValue &= ~(0x10)
		regValue |= (data<< 4) & 0x10
		regData[17] = regValue
	elif bit2set == "TRIG":
		regValue = regData[16]
		regValue &= ~(0x30)
		regValue |= (data<< 4) & 0x30
		regData[16] = regValue
	elif bit2set == "MCM":
		regValue = regData[17]
		regValue &= ~(0x03)
		regValue |= (data<< 0) & 0x03
		regData[17] = regValue
def calcParity(parity_bit):
	y = 0
	if ((parity_bit != "FP") and (parity_bit != "PR")):
		return

	elif parity_bit =="FP":
		set_regs("FP", 1)
		y ^= regData[17]
		y ^= regData[19] >> 5 #upper 3 bits
	
	elif (parity_bit == "CP"):
		
		for i in range(7,13):
			y ^= regData[i]
	
		y ^= (regData[13] & 0x7F)#ignoring WA
		y ^= (regData[14] & 0x3F)#ignoring TST
		y ^= (regData[15] & 0x3F)#ignoring PH
		y ^= regData[16]
	# combine all bits of this byte (assuming each register is one byte)
	y = y ^ (y >> 1)
	y = y ^ (y >> 2)
	y = y ^ (y >> 4)
	# parity is in the LSB of y
	set_regs(parity_bit, y & 0x01)