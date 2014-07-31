#!/usr/bin/python3

import dbus
import threading
import subprocess
import time
import uuid
import queue

class KillProcessOnStallThread(threading.Thread):
	def __init__(self, parent, name="Diewhendone"):
		threading.Thread.__init__(self, name=name)
		self.parent = parent
	def run(self):
		kill_process(self.parent)
		
def kill_process(parent):
	time.sleep((parent.get_duration()/1000000)-0.3)
	try:
		parent.stop()
		parent.outQueue.put("end")
	except:
		pass

class PlayerProcessThread(threading.Thread):
	def __init__(self, parent, name='playerThread'):
		threading.Thread.__init__(self, name=name)
		self.parent = parent
	def run(self):
		player_process(self.parent)

def player_process(parent):
	print("DBUSNAME = " + parent.dbusname)
	subprocess.call(["/usr/bin/omxplayer", "-o", "hdmi", parent.moviefile, "--dbus_name", parent.dbusname, "--win", "0", "0", "1919", "1079"], shell=False)
	print(parent.stopped)
	if parent.stopped == False:
		parent.stopped = True
		print("I got trough to the end")
		parent.outQueue.put("end")
	
class OMXPlayer(object):
	def __init__(self, moviefile, outQueue):
		self.paused = False
		self.moviefile = moviefile
		self.dbusname = self.generate_dbusname()
		self.dbusIfaceProp = None
		self.dbusIfaceKey = None
		self.outQueue = outQueue
		self.stopped = False
		self.overshoot = 32000 # very inscientifically defined delay when pause() is called
		self.go()
		
	def go(self):
		playerProcessThread = PlayerProcessThread(self)
		playerProcessThread.start()
		while True:
			try:
				omxplayerdbus = open('/tmp/omxplayerdbus').read().strip()
				if omxplayerdbus != "":
					break
			except:
				pass
		
		print("OMXPLAYERDBUS = " + omxplayerdbus)	
		bus = dbus.bus.BusConnection(omxplayerdbus)
		
		# Trying to make a connection to the dbus. Fail until ready.
		while True:
			try:
				dbusobject = bus.get_object(self.dbusname, '/org/mpris/MediaPlayer2', introspect=False)
				break
			except:
				if self.stopped:
					break
				pass
		self.dbusIfaceProp = dbus.Interface(dbusobject, 'org.freedesktop.DBus.Properties')
		self.dbusIfaceKey = dbus.Interface(dbusobject, 'org.mpris.MediaPlayer2.Player')
		
		# position will hang on 0 for a moment. Check until value changes.
		try:
			startpos = self.get_position()
			while True:
				if startpos != self.get_position():
					break
		# Try to get as close to pts 0 as possible. Try to guess when we need to press pause.
			delay = (-self.get_position() - self.overshoot)/1000000
			time.sleep(delay)
			self.toggle_pause()
		except:
			pass
		## killProcessOnStallThread = KillProcessOnStallThread(self)
		## killProcessOnStallThread.start()
		
		
	def generate_dbusname(self):
		return("org.mpris.MediaPlayer2.omxplayer" + str(uuid.uuid4()))
	
	def stop(self):
		self.stopped = True
		self.dbusIfaceKey.Stop()
		
	def toggle_pause(self):
		try:
			self.dbusIfaceKey.Pause()
			self.paused = not self.paused
		except:
			if self.stopped:
				pass
		
		
	def get_position(self):
		return self.dbusIfaceProp.Position()
			
	def get_duration(self): 
		return self.dbusIfaceProp.Duration()
		
	def seek(self, microseconds):
		self.dbusIfaceKey.Seek(dbus.Int64(str(microseconds)))