# Kobbra
2004-ish FUSE server emulator made in python 3.7 

## Dependencies
Gevent library: go `pip install gevent` on your favorite shell before running

### Kobbra is a self deployable system
It will deploy itself in its first run. It as a ini file to edit some text based settings such as the binding IP. If it doesn't exist, it will also create and initialize a sqlite db for itself. You can change the settings after the first run. You can also change the default init values directly in the python code, because python lets you do this. 
