# coding: utf-8
import struct
import time

# low-level ------------------------------------------------------------

def get_curr_ts():
	""" Return timestamp as (sec,milisec) """
	t = time.time()
	sec = int(t)
	msec = int((t - float(sec)) * 10**6)
	return sec, msec
	
# Event def = (type,code,value)

def raw(type,code,value):
	return type,code,value
	
def key(ident, state):	
	"""
	state -- 1:pressed, 0:depressed
	"""
	return raw(1, ident, state)

def led(code, value):
	# code 1 == LED_CAPSL
	return raw(17, code, value)

def syn():	
	return raw(0,0,0)

def pack(ts, ev):
	return struct.pack('llHHI', *(ts + ev))

def packs(ev):	
	ts = get_curr_ts()
	return pack(ts, ev) + pack(ts, syn())


def send(f, ts, ev):
	""" Send event """	
	f.write(pack(ts, ev))
	f.flush()

def sends(f, ev):
	""" Send event and syn """
	ts = get_curr_ts()
	send(f, ts, ev)
	send(f, ts, syn())
			
		





if __name__ == '__main__':
		
	
	with open('/dev/input/event0', 'wb') as f:
		
		sends(f, led(1, 0))
		sends(f, key(30, 1))
		sends(f, key(30, 0))

	
