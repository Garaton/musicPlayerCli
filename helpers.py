#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


import sys, subprocess, os

# Defining Enums
class Os:
    LINUX = 0
    WINDOWS = 1
    UNSUPPORTED = 2
class ControlSignals():
    RESTART = 0
    RESTART_SHUFFLE = 1
    NEW_PLAYLIST = 2
    LOOP = 3
    PREVIOUS = 4
    EXIT = 5
    INDEX = 6

# Getting platform/os
platform = sys.platform
if platform == 'linux':
    platform = Os.LINUX
elif platform == 'win32' or platform == 'cygwin':
    platform = Os.WINDOWS
else:
    platform = Os.UNSUPPORTED

# Getting needed file variables
playlistPath:list = os.getcwd()+'/playlists'
playlistList:list = []
for file in os.listdir(playlistPath):
    fileExt = file.split('.')[-1]
    if fileExt == 'mplay' or fileExt == 'm3u8':
        playlistList.append(file)
musicPath:list = os.getcwd()+'/music'
filesInDir:list = os.listdir(musicPath)
musicList:list = [f for f in filesInDir if os.path.isfile(musicPath+'/'+f)]



def _isFileInList(fileList:list[str], goal:str, path:str) -> str|None:
    """
    Checks if the full filename/no file extension filename is within the directory found in list.
    
    :param fileList: The files within the directory
    :param path: Path to a directory with files
    :param goal: Wanted filename
    :return: Filepath to found file of goal, or None if not found
    """
    lowerGoal = goal.lower()
    for file in fileList:
        lowerFile = file.lower()
        name = lowerFile.split('.')[0]
        # if input is one of the files store the filepath then leave
        if name == lowerGoal or lowerFile == lowerGoal:
            return path+'/'+file
    return None



# SetVolume code, and OS specific variants
if platform == Os.WINDOWS:
    from pycaw.pycaw import AudioUtilities
def _setVolumeWin(vol:float):
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        volume = session.SimpleAudioVolume
        if session.Process and session.Process.name() == "python.exe":
            volume.SetMasterVolume(vol, None)

def _setVolumeLinux(vol:int):
    raw:str = subprocess.run(["pactl", "list", "sink-inputs"], capture_output=True, text=True).stdout
    if raw is None:
        return
    sinks = raw.split("Sink Input #")
    for session in sinks:
        if "gst-play-1.0" in session or "SDLAudio" in session:
            index = int(session.split("\n")[0])
            subprocess.run(["pactl", "set-sink-input-volume", f"{index}", f"{vol}%"], capture_output=True)

def setVolume(currentVolume):
    """
    Uses the given volume to set the volume of python.

    :param vol: float between 0 and 1.0
    """
    if platform == Os.LINUX:
        _setVolumeLinux(int(currentVolume*100))
    elif platform == Os.WINDOWS:
        _setVolumeWin(currentVolume)
    else:
        print("Volume unsupported for "+sys.platform)



def getPlaylist() -> list[list[str]]:
    """
    Used to ask the user for what playlist they want, it only accepts playlists found in the playlists directory.
    
    :return: The playlist chosen by the user.
    """
    # Printing the available playlists
    print("Found playlists:\n"+str(playlistList))

    while True:
        # Getting input, if exit exit
        chosenPlaylist:str = input("\nWhat playlist do you want to use ('e' to leave): ")
        if chosenPlaylist.lower() == 'e':
            return None

        # Checking if input in playlists
        chosenFile = _isFileInList(playlistList, chosenPlaylist, playlistPath)

        # If we chose a file leave, overwise prompt for input again
        if chosenFile is not None:
            break
        print("Not a playlist try again.")

    print("\nFile obtained: "+chosenFile)

    fetchedPlaylist = []
    controls = None # List of parts [do we shuffle, volume #, force volume as well]
    usedPath = musicPath
    usingDirectory = False

    with open(chosenFile, 'r') as file:
        lines = file.read().split('\n')

        # check if we have controls
        firstLine = lines[0]
        firstSegment = firstLine[0:2]
        if firstSegment == '##':
            controls = [False, None, None]
            rawControls = firstLine.split(' ')
            
            if 'y' in rawControls:
                controls[0] = True
            
            if 'v' in rawControls:
                indexV = rawControls.index('v')
                if len(rawControls) < indexV+2:
                    print('Incorrect formatting of playlist, there must be a float value after "v".\nIgnoring volume controls for this playlist.')
                else:
                    try:
                        volume = float(rawControls[indexV+1])
                        controls[1] = volume
                    except Exception:
                        print('Value after "v" in playlist isn\'t a float value.\nIgnoring volume controls for this playlist.')

            if 'f' in rawControls:
                controls[2] = True

        # get the songs
        for line in lines:
            song = line.split('#')[0].strip()
            
            # directory case
            if song != '' and song[-1] == '/' and song[:-1] in filesInDir and os.path.isdir(musicPath+'/'+song):
                for dirSong in os.listdir(usedPath+'/'+song):
                    if '.' in dirSong: # no recursive searching
                        fetchedPlaylist.append(usedPath+'/'+song+'/'+dirSong)
            # normal file case
            else:
                filepath = _isFileInList(musicList, song, usedPath)
                if filepath is not None:
                    fetchedPlaylist.append(filepath)
                elif song != '':
                    print(song+" is not found within "+usedPath)

    return [fetchedPlaylist, controls]



def installLibraries():
    subprocess.run(['pip', 'install', 'playsound3'])
    if platform == Os.WINDOWS:
        subprocess.run(['pip', 'install', 'pythoncom'])
        subprocess.run(['pip', 'install', 'pycaw'])