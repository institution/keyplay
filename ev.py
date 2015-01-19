#!/usr/bin/env python
# coding: utf-8
import os
import struct



if __name__ == '__main__':
	
	size = struct.calcsize('llHHI')
	
	stdin = open('/dev/stdin', 'r')
	
	with open('/dev/input/event0', 'wb') as f:
	
		while 1:
			r = stdin.read(size)
	
			if r == '':
				break
			f.write(r)
			f.flush()

