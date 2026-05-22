# Music Player CLI
> By: Garathon

## Overview
I wanted to make a non GUI music player just to listen to music locally in the background, so I did that, then I wanted to control it so I made a control thread and a play thread.

## How To Use
Move music you want to listen to into the music directory, you can create sub directories.

Make a playlist file of type "mplay" or "m3u8" (it's not m3u8) where you have the song filepath as found within the music directory then newline (refer to test.mplay). Basically the filename with/without the extension, and if you have a subdirectory include that subdirectory "sub/test" and "test".

Finally run python on player.py.

## CLI Help
Use the help command. I ain't writing allat.

## Known Issues
Volume is weird AF, which is why vf (volume force) exists, it sometimes doesn't work and you'll have to run vf.

## Playlist File Settings
On the first like you have two comments (/ for mplay, # for m3u8, yes that's the only difference what the comment is), then you have different flags to determine behavior.
- d: Treat files as directories (when you don't want to list out every single file/update this file when you add music) (yes you can do multiple)
- y: Yes shuffle playlist
- n: Don't shuffle playlist
- v [vol %]: Sets volume to vol %
- f: Do force volume (prevents some bugs)