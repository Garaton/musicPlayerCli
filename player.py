
try:
    from playsound3 import playsound
except Exception:
    from helpers import installLibraries
    installLibraries()
    from playsound3 import playsound

from random import shuffle
from time import sleep
from typing import Any
import sys, threading
from helpers import Os, ControlSignals, HelpTexts, platform, getPlaylist, setVolume

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

def playsongs():
    global currentSound
    global controlSignal
    global movementControl
    global playlist
    global newPlaylist
    global curSong

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
                if movementControl == ControlSignals.PREVIOUS:
                    if curSong == 0:
                        curSong = len(playlist)
                    curSong -= 1
                    movementControl = None
            else:
                curSong += 1


player = threading.Thread(target=playsongs)
player.daemon = True

player.start()

if platform == Os.WINDOWS:
    pythoncom.CoInitialize() # So volume works

# Control panel
while True:
    print(f"""
Controls:
q - current queue | s - skip song | p - previous song
st - stop and wait ({isStopped}) | l - loop current ({movementControl==ControlSignals.LOOP})
r - restart | h - shuffle | n - new playlist | nh - new + shuffle
v - set volume | vf - force volume to {currentVolume}
e - exit | help [cmd] - command help
""")
    control:str = input().lower().strip()
    match control:
        case 's':
            if currentSound is not None:
                currentSound.stop()
        case 'st':
            if not isStopped:
                if movementControl == ControlSignals.LOOP:
                    wasLooping = True
                isStopped = True
                setVolume(0)
                movementControl = ControlSignals.LOOP
            else:
                isStopped = False
                if not wasLooping:
                    movementControl = None
                wasLooping = False
                setVolume(currentVolume)
        case 'p':
            movementControl = ControlSignals.PREVIOUS
            if currentSound is not None:
                currentSound.stop()
        case 'e':
            movementControl = ControlSignals.EXIT
            if currentSound is not None:
                currentSound.stop()
            sys.exit(0)
        case 'v':
            newCurrentVolume = float(input("Please enter a number between 1.0 and 0: "))
            if currentVolume > 1.0 or currentVolume < 0.0:
                print("Entered volume was not between 0.0 and 1.0, moving back to control panel.")
            else:
                currentVolume = newCurrentVolume
                setVolume(currentVolume)
        case 'vf':
            setVolume(currentVolume)
        case 'l':
            if movementControl != ControlSignals.LOOP:
                movementControl = ControlSignals.LOOP
            else:
                movementControl = None
        case 'r':
            controlSignal = ControlSignals.RESTART
            if currentSound is not None:
                currentSound.stop()
        case 'h':
            controlSignal = ControlSignals.RESTART_SHUFFLE
            if currentSound is not None:
                currentSound.stop()
        case 'n':
            gotPlaylist = getPlaylist()
            if newPlaylist != None:
                newPlaylist = gotPlaylist[0]
                startingControls = gotPlaylist[1]
                if startingControls != None:
                    if startingControls[0]:
                        shuffle(newPlaylist)
                    if startingControls[2] == 'f' and startingControls[1] != None:
                        currentVolume = startingControls[1]
                        setVolume(currentVolume)
                controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
                if currentSound is not None:
                    currentSound.stop()
        case 'nh':
            gotPlaylist = getPlaylist()
            if newPlaylist != None:
                newPlaylist = gotPlaylist[0]
                if startingControls != None and startingControls[2] == 'f' and startingControls[1] != None:
                    currentVolume = startingControls[1]
                    setVolume(currentVolume)
                shuffle(newPlaylist)
                controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
                if currentSound is not None:
                    currentSound.stop()
        case 'q':
            print("Songs in queue:")
            for i in range(len(playlist)):
                if i == curSong:
                    print("-->\t["+playlist[i].split('/')[-1]+"]")
                else:
                    print("\t"+playlist[i].split('/')[-1])
        case _:
            controlArgs = control.split(' ')
            if controlArgs[0] == 'help':
                if len(controlArgs) > 1:
                    match controlArgs[1]:
                        case 'q':
                            print(HelpTexts.q)
                        case 's':
                            print(HelpTexts.s)
                        case 'p':
                            print(HelpTexts.p)
                        case 'l':
                            print(HelpTexts.l)
                        case 'st':
                            print(HelpTexts.st)
                        case 'r':
                            print(HelpTexts.r)
                        case 'h':
                            print(HelpTexts.h)
                        case 'n':
                            print(HelpTexts.n)
                        case 'nh':
                            print(HelpTexts.nh)
                        case 'v':
                            print(HelpTexts.v)
                        case 'vf':
                            print(HelpTexts.vf)
                        case 'e':
                            print(HelpTexts.e)
                        case 'help':
                            print(HelpTexts.help)
                        case _:
                            print(f"Command, {controlArgs[1]}, isn't supported by help, or doesn't exist.")
                else:
                    print(HelpTexts.q, HelpTexts.s, HelpTexts.p, HelpTexts.l, HelpTexts.st, HelpTexts.r, HelpTexts.h, HelpTexts.n, HelpTexts.nh, HelpTexts.v, HelpTexts.vf, HelpTexts.e, HelpTexts.help, sep = '\n')
            else:
                print(f"{control} is not a valid control command.")