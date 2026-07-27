#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


from playsound3 import playsound

from random import shuffle
from typing import Any
import sys
import globals
from helpers import Os, ControlSignals, platform, getPlaylist, setVolume

if platform == Os.WINDOWS:
    import pythoncom # windows has weird audio issues


# Using function to get playlist
def playlist_init():
    gotPlaylist = getPlaylist()
    if gotPlaylist == None:
        sys.exit(-1)
    globals.playlist = gotPlaylist[0]
    startingControls = gotPlaylist[1]
    if startingControls == None:
        firstRestart = input("Do you wish to shuffle (y/n) : ")
        if firstRestart.lower() == 'y' or firstRestart.lower() == 'yes':
            shuffle(globals.playlist)
    else:
        if startingControls[0]:
            shuffle(globals.playlist)
        if startingControls[1] != None:
            globals.currentVolume = startingControls[1]


def playsongs():
    restart = False
    if platform == Os.WINDOWS:
        pythoncom.CoInitialize() # So volume works
    while True:
        globals.curSong = 0
        while globals.curSong < len(globals.playlist):
            song = globals.playlist[globals.curSong]
            if platform == Os.WINDOWS:
                setVolume(globals.currentVolume)
            globals.currentSound = playsound(song, block=False)
            if platform == Os.WINDOWS:
                setVolume(globals.currentVolume)
            globals.currentSound.wait()

            # If we have a control signal check what it is
            if globals.controlSignal != None:
                match globals.controlSignal:
                    case ControlSignals.NEW_PLAYLIST:
                        globals.playlist= globals.newPlaylist
                        restart = True
                    case ControlSignals.RESTART_SHUFFLE:
                        shuffle(globals.playlist)
                        restart = True
                    case ControlSignals.RESTART:
                        restart = True
                    case _:
                        print("ERROR UNRECOGNIZED CONTROL SIGNAL "+controlSignal)
                
                controlSignal = None # Reset control signal to None

                # If we were ordered to restart do so
                if restart:
                    globals.movementControl = None
                    restart = False
                    break
            
            if globals.movementControl != None:
                match globals.movementControl:
                    case ControlSignals.PREVIOUS:
                        if globals.curSong == 0:
                            curSong = len(globals.playlist)
                        globals.curSong -= 1
                    case ControlSignals.INDEX:
                        globals.curSong = globals.argsPassToPlayer[0]
                    case ControlSignals.LOOP:
                        pass
                    case _:
                        globals.curSong += 1
                if globals.movementControl != ControlSignals.LOOP:
                    globals.movementControl = None
            else:
                globals.curSong += 1