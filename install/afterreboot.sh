#!/bin/bash
if [ -e readonly_on ];
then
	mount -o remount,rw /
fi
mv /etc/rc.local.bak /etc/rc.local
apt-get update -y
apt-get upgrade -y
apt-get install omxplayer -y
apt-get install python3-dbus -y
apt-get install python-dbus -y
apt-get install lighttpd -y
cp ../locations/boot/runonboot.sh /boot/
cp -r ../locations/etc/lighttpd/* /etc/lighttpd/
cp ../locations/etc/rc.local /etc/rc.local
if [ ! -e readonly_on ];
then
	./make_fs_readonly.sh
fi
reboot
