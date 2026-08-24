#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


from random import shuffle
import sys
import globals
from collections.abc import Callable
from helpers import ControlSignals, getPlaylist, setVolume


# Very common command actions
def stopSong():
    """
    Typically used when sending a signal over to the music player
    """
    if globals.currentSound is not None:
        globals.currentSound.stop()


# Command class/struct
class Command:
    helpText:str
    function:Callable[[list[str]]]

    def __init__(self, function, helpText):
        self.helpText = helpText
        self.function = function


# Command Functions
def exitProg(args:list):
    globals.movementControl = ControlSignals.EXIT
    stopSong()
    sys.exit(0)

def queue(args:list):
    print("Songs in queue:")
    for i in range(len(globals.playlist)):
        if i == globals.curSong:
            print(f"-->\t[{globals.playlist[i].split('/')[-1]}]")
        else:
            print(f"{i}\t{globals.playlist[i].split('/')[-1]}")
    print("\nCurrently Playing:\n\t"+globals.playlist[globals.curSong].split('/')[-1])

def help(args:list[str]):
    if len(args) == 1:
        if args[0] in commandDict:
            print(commandDict[args[0]].helpText)
        else:
            print(f"Command, {args[0]}, doesn't exist.")
    else:
        for command in commandDict.values():
            print(command.helpText)

def skip(args:list):
    stopSong()

def previous(args:list):
    globals.movementControl = ControlSignals.PREVIOUS
    stopSong()

def loop(args:list):
    if globals.movementControl != ControlSignals.LOOP:
        globals.movementControl = ControlSignals.LOOP
    else:
        globals.movementControl = None

def shufflePlay(args:list):
    globals.controlSignal = ControlSignals.RESTART_SHUFFLE
    stopSong()

def newPlay(args:list):
    gotPlaylist = getPlaylist()
    if globals.newPlaylist != None:
        globals.newPlaylist = gotPlaylist[0]
        startingControls = gotPlaylist[1]
        if startingControls != None:
            if startingControls[0]:
                shuffle(globals.newPlaylist)
            if startingControls[2] != None and startingControls[1] != None:
                globals.currentVolume = startingControls[1]
                setVolume(globals.currentVolume)

        globals.controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
        stopSong()

def newPlayShuffle(args:list):
    gotPlaylist = getPlaylist()
    if globals.newPlaylist != None:
        globals.newPlaylist = gotPlaylist[0]
        startingControls = gotPlaylist[1]
        if startingControls[2] != None and startingControls[1] != None:
            globals.currentVolume = startingControls[1]
            setVolume(globals.currentVolume)
        shuffle(globals.newPlaylist)

        globals.controlSignal = ControlSignals.NEW_PLAYLIST # new playlist
        stopSong()

def stop(args:list):
    if not globals.isStopped:
        if globals.movementControl == ControlSignals.LOOP:
            globals.wasLooping = True
        globals.isStopped = True
        setVolume(0)
        globals.movementControl = ControlSignals.LOOP
    else:
        globals.isStopped = False
        if not globals.wasLooping:
            globals.movementControl = None
        globals.wasLooping = False
        setVolume(globals.currentVolume)

def restart(args:list):
    globals.controlSignal = ControlSignals.RESTART
    stopSong()

def goToIndex(args:list[str]):
    if len(args) == 1:
        if args[0].isdigit():
            indexSong = int(args[0])
            if indexSong < len(globals.playlist) and indexSong >= 0:
                globals.argsPassToPlayer = [indexSong]
                globals.movementControl = ControlSignals.INDEX
                stopSong()
            else:
                print(f"Index out of bounds for length {len(globals.playlist)}.")
        else:
            print("Please enter a number for the index not a string.")
    else:
        print("Too few or too many arguments for command.\n\tUsage:\ti [song-index]")

def volumeForce(args:list):
    setVolume(globals.currentVolume)

def volume(args:list[str]):
    if len(args) == 1:
        try:
            newCurrentVolume = float(args[0])
            if newCurrentVolume > 1.0 or newCurrentVolume < 0.0:
                print("Entered volume was not between 0.0 and 1.0, moving back to control panel.")
            else:
                globals.currentVolume = newCurrentVolume
                setVolume(globals.currentVolume)
        except ValueError:
            print("Please enter a number for the index not a string.")
    else:
        print("Too few or too many arguments for command.\n\tUsage:\tv [value 0 to 1]")

# Command Dict
commandDict = {
    's': Command(skip, "s\tSkip Song - Ends the current song prematurely and moves onto the next one, with loop enable this acts as a restart."),
    'p': Command(previous, "p\tPrevious Song - End the current song prematurely and moves to the previous song, OVERRIDES LOOP."),
    'st': Command(stop, "st\tStop Song - This doesn't 'pause' the song, it turns off the volume and just loops the song. Hey give me some credit it's creative. PRESERVES PREVIOUS LOOPING STATUS."),
    'q': Command(queue, "q\tCurrent Queue - Prints the songs in the playlist w/ order along with the current song surrounded by []."),
    'help': Command(help, "help [cmd]\tHelp - Gives help about a single command, and if you input nothing, everything! Also weird to say help help, but you do you pal."),
    'i': Command(goToIndex, "i [song-index]\tIndex - Jumps to the song at index song-index for the playlist."),
    'l': Command(loop, "l\tLoop Current Song - Tells the audio player to replay the song instead of moving onto the next one."),
    'r': Command(restart, "r\tRestart Playlist - Stops the song and then starts the play list from the start."),
    'v': Command(volume, "v [value 0 to 1]\tSet Volume - Uses the given volume from the user, and then sets the volume of this python application, usually."),
    'vf': Command(volumeForce, "vf\tForce Volume - In the case that volume isn't set correctly, spam this a few times."),
    'e': Command(exitProg, "e\tExit - 'Gracefully' exits the program, it's multithreaded so it's not that graceful but it's better."),
    'h': Command(shufflePlay, "h\tShuffle Playlist - Shuffles the current playlist, does not preserve the current song."),
    'n': Command(newPlay, "n\tNew Playlist - Prompts you to give a new playlist to listen to."),
    'nh': Command(newPlayShuffle, "nh\tNew Playlist And Shuffle - I wonder if new playlist and shuffle, prompts you to get a new playlist, and shuffles it for you, hmm."),
}