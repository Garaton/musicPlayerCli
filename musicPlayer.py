#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


from playsound3 import playsound

from random import shuffle
from typing import Any
import sys
from helpers import Os, ControlSignals, platform, getPlaylist, setVolume

if platform == Os.WINDOWS:
    import pythoncom # windows has weird audio issues

playlist:list[str] = []
newPlaylist:list[str] = []
chosenFile:str = None
currentVolume:float = 0.4
isStopped:bool = False
wasLooping:bool = False

# Using function to get playlist
gotPlaylist = getPlaylist()
if gotPlaylist == None:
    sys.exit(-1)
playlist = gotPlaylist[0]
startingControls = gotPlaylist[1]
if startingControls == None:
    firstRestart = input("Do you wish to shuffle (y/n) : ")
    if firstRestart.lower() == 'y' or firstRestart.lower() == 'yes':
        shuffle(playlist)
else:
    if startingControls[0]:
        shuffle(playlist)
    if startingControls[1] != None:
        currentVolume = startingControls[1]

# Setting up playsong thread+globals
currentSound:Any = None
controlSignal:int = None
movementControl:int = None
curSong:int = 0
argsPassToPlayer:list = None

def playsongs():
    global currentSound
    global controlSignal
    global movementControl
    global playlist
    global newPlaylist
    global curSong
    global argsPassToPlayer

    restart = False
    first = True
    if platform == Os.WINDOWS:
        pythoncom.CoInitialize() # So volume works
    while True:
        curSong = 0
        while curSong < len(playlist):
            song = playlist[curSong]
            if platform == Os.WINDOWS:
                setVolume(currentVolume)
            currentSound = playsound(song, block=False)
            if platform == Os.WINDOWS:
                setVolume(currentVolume)
            currentSound.wait()

            # If we have a control signal check what it is
            if controlSignal != None:
                match controlSignal:
                    case ControlSignals.NEW_PLAYLIST:
                        playlist = newPlaylist
                        restart = True
                    case ControlSignals.RESTART_SHUFFLE:
                        shuffle(playlist)
                        restart = True
                    case ControlSignals.RESTART:
                        restart = True
                    case _:
                        print("ERROR UNRECOGNIZED CONTROL SIGNAL "+controlSignal)
                
                controlSignal = None # Reset control signal to None

                # If we were ordered to restart do so
                if restart:
                    movementControl = None
                    restart = False
                    break
            
            if movementControl != None:
                match movementControl:
                    case ControlSignals.PREVIOUS:
                        if curSong == 0:
                            curSong = len(playlist)
                        curSong -= 1
                        movementControl = None
                    case ControlSignals.INDEX:
                        curSong = argsPassToPlayer[0]
                    case ControlSignals.LOOP:
                        pass
                    case _:
                        curSong += 1