#
# Author: Garathon
#
# Copywrite: LOLOLOL
#


import threading

import globals
from musicPlayer import playsongs, playlist_init
from controlCommands import commandDict
from helpers import platform, Os, ControlSignals

if platform == Os.WINDOWS:
    import pythoncom # windows has weird audio issues


def main():
    globals.init()
    playlist_init()

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
    st - stop and wait ({globals.isStopped}) | l - loop current ({globals.movementControl==ControlSignals.LOOP})
    r - restart | h - shuffle | n - new playlist | nh - new + shuffle
    v - set volume | vf - force volume to {globals.currentVolume}
    e - exit | help [cmd] - command help\n""")
        controls:str = input().lower().strip().split(' ')
        if controls[0] in commandDict:
            commandDict[controls[0]].function(controls[1:])
        else:
            print(f"{controls[0]} is not a valid control command.")


if __name__ == '__main__':
    main()