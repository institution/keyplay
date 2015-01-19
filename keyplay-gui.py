#!/usr/bin/python
import gtk
from functools import partial
import gobject, os, re
from subprocess import call
import time

import os
#from stat import *
import mimetypes
#import mimeapps
import subprocess
import sys

from ll import packs, key
from lock_on_pid import lock_on_pid
from parser import parse
from instruct import HLD,REL,NUL,CMD,SRC
from keycode import get_keycode

def buffered_stdin_lines():	
	while 1:
		try:
			x = raw_input()	
			
		except EOFError: 
			break
		
		yield x


from subprocess import Popen, PIPE, STDOUT

# long list filter app
class KeyPlayGui(object):

	
	def delete_event(self, widget, event):
		print "delete event occurred"
		# Change FALSE to TRUE and the main window will not be destroyed
		# with a "delete_event".
		return False

	def destroy(self):
		gtk.main_quit()

	def poke_button(self, x):
		ABORT = 'Abort!'
		if self.button.get_label() == ABORT:
			# self.clear_keyboard()
			self.clear_mods()
			self.destroy()
		
		self.button.set_label(ABORT)
		self.play()		
		
		
		
	def load_script(self, fname):
		if fname == '/dev/stdin':
			f = sys.stdin
		else:
			f = open(fname, 'r')
		
		
		self.seq = list(parse(f))
		self.button.set_label("Play")
		self.pos = 0
		self.f_stop = 0
		self.f_unlink = 0
		
	def sends(self, ev):
		self.evproc.stdin.write(packs(ev))
	
	def reset_kb(self):

		import commands
		x = commands.getoutput('xset q | grep LED')[65]
		
		capslock_on = (int(x) & 1)
		if capslock_on:
			self.sends(key(get_keycode('CAPSLOCK'), 1))
			self.sends(key(get_keycode('CAPSLOCK'), 0))
	
		self.clear_mods()
	
	def clear_mods(self):
		self.sends(key(get_keycode('LEFTCTRL'), 0))
		self.sends(key(get_keycode('LEFTSHIFT'), 0))
		self.sends(key(get_keycode('LEFTALT'), 0))
		
		self.sends(key(get_keycode('RIGHTCTRL'), 0))
		self.sends(key(get_keycode('RIGHTSHIFT'), 0))
		self.sends(key(get_keycode('RIGHTALT'), 0))
			

	def play(self):
		while not self.f_stop and self.pos < len(self.seq):
			cmd,arg = self.seq[self.pos]
			self.pos += 1
		
			print cmd, repr(arg)
			
			if cmd == HLD:			
				self.sends(key(get_keycode(arg), 1))
				
			elif cmd == REL:
				self.sends(key(get_keycode(arg), 0))
				
			elif cmd == NUL:
				gobject.timeout_add(arg, self.play)  # resume after arg ms
				return
				
			elif cmd == CMD:
				if arg == 'pause':
					self.button.set_label("Continue...")
					return
					
				elif arg == 'clear':
					# reset keyboard state
					self.reset_kb()
					
				elif arg == 'unlink':
					self.f_unlink = 1
				else:
					raise Exception('unknown command')
					
			elif cmd == SRC:
				#print cmd, arg
				pass
				
			else:
				raise Exception('unknown instruction')
		
		if self.f_unlink and self.fname != '/dev/stdin':
			os.unlink(self.fname)
		
		self.button.set_label("Load...")
		self.destroy()
		#print 'f_unlink = {}'.format(f_unlink)
			
			
			
			
			
			

	def __init__(self, fname):
		self.fname = fname
		
		
		
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_default_size(140, 70)
		window.connect("delete_event", self.delete_event)
		window.connect("destroy", lambda _: self.destroy() )
		
		window.set_title("KeyPlayGui")
		window.set_accept_focus(False)
		window.set_skip_pager_hint(True)
		window.set_skip_taskbar_hint(True)
		window.set_urgency_hint(True)
		window.set_keep_above(True)
		window.stick()
		window.show()
		
		button = gtk.Button("Load...")
		button.connect("clicked", self.poke_button)
		# button.connect("clicked", lambda _: window.destroy() )
		button.show()
		
		window.add(button)
		
		self.window = window
		self.button = button
		
		ev_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'ev.py'))
		self.evproc = Popen(['sudo', ev_path], stdin=PIPE)
				
		self.load_script(fname)
		
				
	def run_event_loop(self):
		gtk.main()








def main():
	
	with lock_on_pid('/tmp/keyplay.pid'):
		
		if len(sys.argv) >= 2:
			fname = sys.argv[-1]
		else:
			fname = '/dev/stdin'

		a = KeyPlayGui(fname = fname)
		a.run_event_loop()
		
		
		#with open('/dev/input/event0', 'wb') as f:
		#	#with open('/dev/input/event0', 'rb') as fr:
		#	f_unlink = play(f, seq)

		#if f_unlink:
		#	os.unlink(fname)
	
	

	

if __name__ == "__main__":
	main()









