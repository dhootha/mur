#!/usr/bin/python3

import dbus
import threading
import subprocess
import time
import uuid

class OMXPlayer(object):
	def __init__(self, moviefile):
		self.paused = False
		self.moviefile = moviefile
		self.dbusname
		self.dbusIfaceProp
		self.dbusIfaceKey
		self.overshoot = 32000 # very inscientifically defined delay when pause() is called
		self.go()
		
	def go(self):
		subprocess.Popen("omxplayer %s --dbus_name %s" % (self.moviefile, self.dbusname), shell=True)
		omxplayerdbus = open('/tmp/omxplayerdbus').read().strip()
		bus = dbus.bus.BusConnection(omxplayerdbus)
		# Trying to make a connection to the dbus. Fail until ready.
		while True:
			try:
				dbusobject = bus.get_object(self.dbusname, '/org/mpris/MediaPlayer2', introspect=False)
				break
			except:
				pass
		self.dbusIfaceProp = dbus.Interface(dbusobject, 'org.freedesktop.DBus.Properties')
		self.dbusIfaceKey = dbus.Interface(dbusobject, 'org.mpris.MediaPlayer2.Player')
		
		# position will hang on 0 for a moment. Check until value changes.
		startpos = self.get_position()
		while True:
			if startpos != self.get_position():
				break
		# Try to get as close to pts 0 as possible. Try to guess when we need to press pause.
		delay = (-self.get_position() - self.overshoot)/1000000
		time.sleep(delay)
		self.toggle_pause()
		
		
	def generate_dbusname(self):
		self.dbusname = "org.mpris.MediaPlayer2.omxplayer" + str(uuid.uuid4())
		
	def toggle_pause(self):
		self.dbusIfaceKey.pause()
		self.paused = not self.paused
		
	def get_position(self):
		return self.dbusIfaceProp.Position()
		
	def get_duration(self): 
		return self.dbusIfaceProp.Duration()
		
	def seek(self, microseconds):
		self.dbusIfaceKey.Seek(dbus.Int64(str(microseconds)))