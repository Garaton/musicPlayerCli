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
class HelpTexts:
    q = "q - Current Queue - Prints the songs in the playlist w/ order along with the current song surrounded by []."
    s = "s - Skip Song - Ends the current song prematurely and moves onto the next one, with loop enable this acts as a restart."
    p = "p - Previous Song - End the current song prematurely and moves to the previous song, OVERRIDES LOOP."
    l = "l - Loop Current Song - Tells the audio player to replay the song instead of moving onto the next one."
    st = "st - Stop Song - This doesn't 'pause' the song, it turns off the volume and just loops the song. Hey give me some credit it's creative. PRESERVES PREVIOUS LOOPING STATUS."
    r = "r - Restart Playlist - Stops the song and then starts the play list from the start."
    h = "h - Shuffle Playlist - Shuffles the current playlist, does not preserve the current song."
    n = "n - New Playlist - Prompts you to give a new playlist to listen to."
    nh = "nh - New Playlist And Shuffle - I wonder if new playlist and shuffle, prompts you to get a new playlist, and shuffles it for you, hmm."
    v = "v - Set Volume - Asks for a volume from 0-1 from the user then sets the volume of this python application, usually."
    vf = "vf - Force Volume - In the case that volume isn't set to where you want it, spam this a few times."
    e = "e - Exit - 'Gracefully' exits the program, it's multithreaded so it's not that graceful but it's better."
    help = "help [cmd] - Help - Gives help about a single command, and if you input nothing, everything! Also weird to say help help, but you do you pal."

# Getting platform/os
platform = sys.platform
if platform == 'linux':
    platform = Os.LINUX
elif platform == 'win32' or platform == 'cygwin':
    platform = Os.WINDOWS
else:
    platform = Os.UNSUPPORTED

# Getting needed file variables
playlistPath:list = os.getcwd()+"/playlists"
playlistList:list = []
for file in os.listdir(playlistPath):
    fileExt = file.split('.')[-1]
    if fileExt == 'mplay' or fileExt == 'm3u8':
        playlistList.append(file)
musicPath:list = os.getcwd()+"/music"
musicList:list = os.listdir(musicPath)



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
        songs = file.read().split('\n')

        # check if we have controls
        firstLine = songs[0]
        comment = '/'
        firstSegment = firstLine[0:2]
        if firstLine[0] == '#':
            comment = '#' # m3u8 compatibility
        if firstSegment == comment*2:
            controls = [False, None, None]
            rawControls = firstLine.split(' ')
            
            # we're actually going into a different directory
            if 'd' in rawControls:
                usingDirectory = True
                usedPath = musicPath+'/'+songs[1] # TODO refactor this so we can accept multiple directories
                songs = os.listdir(usedPath)

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
        for rawSong in songs:
            song = rawSong.split(comment)[0].strip()
            if not usingDirectory:
                filepath = _isFileInList(musicList, song, usedPath)
            else:
                filepath = usedPath+'/'+song
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