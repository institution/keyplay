# coding: utf-8

from instruct import HLD,REL,NUL,CMD,SRC

# parser ---------------------------------------------------------------


ZERO_DELAY = 0     # time between two holds or two releases of control keys when combining
MICRO_DELAY = 2     # time beetwen ctrl hold and char hold when combining
HOLD_DELAY = 15    # time between hold and release during typing
AFTER_DELAY = 35    # time between release and hold during typing
PAUSE_DELAY = 100  # time to wait per dot


def is_char(c):
	return isinstance(c, unicode) and len(c) == 1

def is_lower_char(c):
	assert is_char(c)
	return u'0' <= c <= u'9' or u'a' <= c <= u'z'
	
def is_upper_char(c):
	assert is_char(c)
	return u'A' <= c <= u'Z'
	
	
		
def type_seq(cc):
	c = cc.upper()
	
	yield (HLD, c)
	yield (NUL, HOLD_DELAY)
	yield (REL, c)
	yield (NUL, AFTER_DELAY)
		
def shift_type_seq(cc):
	c = cc.upper()
	
	yield (HLD, 'LEFTSHIFT')
	yield (NUL, MICRO_DELAY)			
	yield (HLD, c)
	yield (NUL, HOLD_DELAY)
	yield (REL, c)
	yield (NUL, MICRO_DELAY)
	yield (REL, 'LEFTSHIFT')
	yield (NUL, AFTER_DELAY)

def gtkunicode_type_seq(c):
	yield (HLD, 'LEFTCTRL')
	yield (NUL, ZERO_DELAY)
	yield (HLD, 'LEFTSHIFT')
	yield (NUL, MICRO_DELAY)
	yield (HLD, 'U')
	yield (NUL, MICRO_DELAY)	
	yield (REL, 'U')
	yield (NUL, MICRO_DELAY)
	yield (REL, 'LEFTSHIFT')
	yield (NUL, ZERO_DELAY)
	yield (REL, 'LEFTCTRL')
	yield (NUL, MICRO_DELAY)
		
	for hex_digit in '{:x}'.format(ord(c)):
		hd = hex_digit.upper()
		
		yield (HLD, hd)
		yield (NUL, MICRO_DELAY)
		yield (REL, hd)
		yield (NUL, MICRO_DELAY)

	yield (HLD, 'ENTER')
	yield (NUL, MICRO_DELAY)
	yield (REL, 'ENTER')
	yield (NUL, AFTER_DELAY)


	
def char_seq(c):
	assert is_char(c), repr(c)
		
	if is_lower_char(c):
		for x in type_seq(c):
			yield x
		
	elif is_upper_char(c):
		for x in shift_type_seq(c):
			yield x
	else:
		for x in gtkunicode_type_seq(c):
			yield x



class Parser:
	""" Input program (text) -> commands (list of tuples)
	
	ex.
	"A" --> 
		(HLD leftshift) (NUL 1)
		(HLD a) (NUL 5)
		(REL a) (NUL 1)
		(REL leftshift) (NUL 1) 
		
	"ala" +ENTER -ENTER "ma kota" A L A SPACE M A SPACE K O T A 

	:::: tab :::: "ROMANOWICZ S.C." : backspace

	"""
	
	def __init__(self, f):
		self.pos = 0
		self.input = f.read().decode('utf-8')
		self.stack = []

	def get(self):
		if self.pos >= len(self.input):
			self.pos += 1
			return "EOF"
			
		else:
			x = self.input[self.pos]
			self.pos += 1
			return x
			
		
	def unget(self):
		if self.pos > 0:
			self.pos -= 1
		else:
			raise Exception('unget not possible')
	
	
	
	
	def parse(self):
		get = self.get
		unget = self.unget
		
		READY = 0
		STRING = 1
		IDENT = 2
		ESCAPE = 3
		COMMAND = 4
		op = ''
		ident = []
		
		
		state = READY
		

		while 1:
			x = get()
				
			if state == READY:
				
				if x == '+':
					op = '+'
					
				elif x == '-':
					op = '-'
					
				elif x == '(':
					assert op == ''		
					assert not ident
					state = COMMAND
				
				elif x == '"':
					assert op == ''
					state = STRING
						
				elif x == '.':
					yield (SRC, u'.')
					yield (NUL, PAUSE_DELAY)
				
				elif x == ':':
					yield (SRC, u':')
					yield (NUL, PAUSE_DELAY * 2)
					
					
				elif x in "qazwsxedcrfvtgbyhnujmikolpQAZXSWEDCRFVTGBYHNUJMIKLOP_":
					unget()
					state = IDENT
					
				elif x == 'EOF':							
					assert state == READY
					assert op == ''
					assert ident == []				
					return;
					
				elif x in " \n\t":
					pass
					
				else:
					raise Exception("invalid char "+x)
			
			elif state == COMMAND:
				
				if x in u"qazwsxedcrfvtgbyhnujmikolpQAZXSWEDCRFVTGBYHNUJMIKLOP_1234567890":
					ident += x
					
				elif x == u')':
					symb = u''.join(ident)
					
					assert symb in ['pause', 'unlink', 'clear']
					
					yield (SRC, u'({})'.format(symb))
					yield (CMD, symb)
					ident = []
					op = ''
					state = READY
				
				elif x == 'EOF':							
					raise Exception('EOF inside command')
									
				else:
					raise Exception('unexcpected char {}'.format(repr(x)))
					
	
			elif state == STRING:
				
				if x == '"':
					state = READY
				elif x == '\\':
					state = ESCAPE		
				elif x == 'EOF':
					raise Exception("EOF inside string")			
				else:
					assert op == ''
					yield (SRC, u'"{}"'.format(x))
					for _ in char_seq(x):
						yield _
					
					
			elif state == ESCAPE:
							
				if x == 'EOF':
					raise Exception('EOF after ESCAPE')
				else:
					yield (SRC, u'"\{}"'.format(x))
					for _ in char_seq(x):
						yield _
					state = STRING
				
			elif state == IDENT:
				
				if x in "qazwsxedcrfvtgbyhnujmikolpQAZXSWEDCRFVTGBYHNUJMIKLOP_1234567890":
					ident += x.upper()
					
				else:
					unget()
					
					symb = u''.join(ident)
					if op == '+':
						yield (SRC, '+'+symb)
						yield (HLD, symb)
						yield (NUL, MICRO_DELAY)
						
					elif op == '-':
						yield (SRC, '-'+symb)
						yield (REL, symb)
						yield (NUL, MICRO_DELAY)
						
					else:	
						yield (SRC, symb)						
						yield (HLD, symb)
						yield (NUL, HOLD_DELAY)
						yield (REL, symb)
						yield (NUL, AFTER_DELAY)
					
					ident = []
					op = ''
					state = READY
					
						
					
					
			else:
				raise Exception('corrupt state')
				
		
				
	

def parse(inp):
	for _ in Parser(inp).parse():
		yield _


# test -----------------------------------------------------------------

if __name__ == '__main__':
	import sys
	
	assert len(sys.argv) >= 2

	p = Parser(open(sys.argv[-1], 'r'))
	for x in p.parse():
		print x
