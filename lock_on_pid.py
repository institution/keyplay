# coding: utf-8
import os, sys, fcntl

# locking process ------------------------------------------------------

class lock_on_pid:
	def __init__(self, pidfile, errno=1):
		self.pidfile = pidfile
		self.errno = errno
				
	def __enter__(self):
		pid = str(os.getpid())
		self.fd = os.open(self.pidfile, os.O_WRONLY|os.O_CREAT)
		try:
			fcntl.lockf(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
			# print 'lock aquired'
			os.write(self.fd, pid)
			
		except IOError:
			sys.stderr.write(
				"another instance is running; pidfile={}\n".format(
					self.pidfile
				)
			)
			os.close(self.fd)			
			sys.exit(self.errno)
	
	def __exit__(self, *args):
		os.close(self.fd)
		os.unlink(self.pidfile)
		
		
