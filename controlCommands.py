#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


from random import shuffle
import sys
from collections.abc import Callable
from helpers import ControlSignals, getPlaylist, setVolume
from musicPlayer import curSong, playlist, argsPassToPlayer, currentSound, currentVolume, isStopped, movementControl, wasLooping, controlSignal, newPlaylist


# Command class/struct
class Command:
    helpText:str
    function:Callable[[list]]

    def __init__(self, function, helpText):
        self.helpText = helpText
        self.function = function


# Command Functions
def exitProg(args:list):
    global movementControl
    movementControl = ControlSignals.EXIT
    if currentSound is not None:
        currentSound.stop()
    sys.exit(0)

def queue(args:list):
    print("Songs in queue:")
    for i in range(len(playlist)):
        if i == curSong:
            print(f"-->\t[{playlist[i].split('/')[-1]}]")
        else:
            print(f"{i}\t{playlist[i].split('/')[-1]}")

def help(args:list):
    if len(args) > 1:
        if args[1] in commandDict:
            print(commandDict[args[1]].helpText)
        else:
            print(f"Command, {args[1]}, doesn't exist.")
    else:
        for command in commandDict.values():
            print(command.helpText)

def skip(args:list):
    if currentSound is not None:
        currentSound.stop()

def previous(args:list):
    global movementControl
    movementControl = ControlSignals.PREVIOUS
    if currentSound is not None:
        currentSound.stop()

def loop(args:list):
    global movementControl
    if movementControl != ControlSignals.LOOP:
        movementControl = ControlSignals.LOOP
    else:
        movementControl = None

def shufflePlay(args:list):
    global controlSignal
    controlSignal = ControlSignals.RESTART_SHUFFLE
    if currentSound is not None:
        currentSound.stop()

def newPlay(args:list):
    global newPlaylist
    global controlSignal
    global currentVolume
    gotPlaylist = getPlaylist()
    if newPlaylist != None:
        newPlaylist = gotPlaylist[0]
        startingControls = gotPlaylist[1]
        if startingControls != None:
            if startingControls[0]:
                shuffle(newPlaylist)
            if startingControls[2] != None and startingControls[1] != None:
                currentVolume = startingControls[1]
                setVolume(currentVolume)
        controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
        if currentSound is not None:
            currentSound.stop()

def newPlayShuffle(args:list):
    global newPlaylist
    global controlSignal
    global currentVolume
    gotPlaylist = getPlaylist()
    if newPlaylist != None:
        newPlaylist = gotPlaylist[0]
        startingControls = gotPlaylist[1]
        if startingControls[2] != None and startingControls[1] != None:
            currentVolume = startingControls[1]
            setVolume(currentVolume)
        shuffle(newPlaylist)
        controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
        if currentSound is not None:
            currentSound.stop()

def stop(args:list):
    global isStopped
    global movementControl
    global wasLooping
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

def restart(args:list):
    global controlSignal
    controlSignal = ControlSignals.RESTART
    if currentSound is not None:
        currentSound.stop()

def goToIndex(args:list):
    global argsPassToPlayer
    global movementControl
    if len(args) == 1:
        if args[0] < len(playlist):
            argsPassToPlayer = [args[0]]
            movementControl = ControlSignals.INDEX
        else:
            print(f"Index out of bounds for length {len(playlist)}.")
    else:
        print("Too few or too many arguments for command.\n\tUsage:\ti [song-index]")

def volumeForce(args:list):
    setVolume(currentVolume)

def volume(args:list):
    global currentVolume
    if len(args) == 1:
        newCurrentVolume = args[0]
        if newCurrentVolume > 1.0 or newCurrentVolume < 0.0:
            print("Entered volume was not between 0.0 and 1.0, moving back to control panel.")
        else:
            currentVolume = newCurrentVolume
            setVolume(currentVolume)
    else:
        print("Too few or too many arguments for command.\n\tUsage:\tv [value 0 to 1]")

# Command Dict
commandDict = {
    's': Command(skip, "s - Skip Song - Ends the current song prematurely and moves onto the next one, with loop enable this acts as a restart."),
    'p': Command(previous, "p - Previous Song - End the current song prematurely and moves to the previous song, OVERRIDES LOOP."),
    'st': Command(stop, "st - Stop Song - This doesn't 'pause' the song, it turns off the volume and just loops the song. Hey give me some credit it's creative. PRESERVES PREVIOUS LOOPING STATUS."),
    'q': Command(queue, "q - Current Queue - Prints the songs in the playlist w/ order along with the current song surrounded by []."),
    'help': Command(help, "help [cmd] - Help - Gives help about a single command, and if you input nothing, everything! Also weird to say help help, but you do you pal."),
    'i': Command(goToIndex, "i [song-index] - Index - Jumps to the song at index song-index for the playlist."),
    'l': Command(loop, "l - Loop Current Song - Tells the audio player to replay the song instead of moving onto the next one."),
    'r': Command(restart, "r - Restart Playlist - Stops the song and then starts the play list from the start."),
    'v': Command(volume, "v [value 0 to 1] - Set Volume - Uses the given volume from the user, and then sets the volume of this python application, usually."),
    'vf': Command(volumeForce, "vf - Force Volume - In the case that volume isn't set correctly, spam this a few times."),
    'e': Command(exitProg, "e - Exit - 'Gracefully' exits the program, it's multithreaded so it's not that graceful but it's better."),
    'h': Command(shufflePlay, "h - Shuffle Playlist - Shuffles the current playlist, does not preserve the current song."),
    'n': Command(newPlay, "n - New Playlist - Prompts you to give a new playlist to listen to."),
    'nh': Command(newPlayShuffle, "nh - New Playlist And Shuffle - I wonder if new playlist and shuffle, prompts you to get a new playlist, and shuffles it for you, hmm."),
}