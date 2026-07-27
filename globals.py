def init():
    global playlist
    global newPlaylist
    global currentVolume
    global isStopped
    global wasLooping
    playlist = []
    newPlaylist = []
    currentVolume = 0.4
    isStopped = False
    wasLooping = False

    # Setting up playsong thread vars
    global currentSound
    global controlSignal
    global movementControl
    global curSong
    global argsPassToPlayer
    currentSound = None
    controlSignal = None
    movementControl = None
    curSong = 0
    argsPassToPlayer = None