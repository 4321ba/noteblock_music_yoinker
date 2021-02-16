# Noteblock Music Yoinker

Minecraft Forge mod for yoinking noteblock music you hear.  
Plus extra utility Python scripts to manipulate the data.

Requires Minecraft 1.12.2 or 1.15.2 and Forge, and Python 3 for the scripts.

Showcase video: https://youtu.be/corLmU4yWqk .

# Usage

Press R to start recording music to the `.minecraft/recorded_music` folder. Press R again to stop recording. Currently there's no indicator if you're recording or not, you have to see if the file size is growing or look back at the logs.

File format:  
Music is recorded in csv format separated with `,`, every line is a new note.  
1st value is the instrument.  
2nd value is the number of ticks since the previous line (1 tick = 1/40 second), integer.  
3rd value is the pitch ranging from 0.5 to 2.0.  
4th value is the volume ranging from 0.0 to 1.0, but it can be bigger (from real note blocks e.g.).  

# Releases

The new release for 1.15.2, `noteblock_music_yoinker-1.15.2-1.1.jar` fixes the issue #1 (and also #2).  
I also backported the mod for 1.12.2 (so that you can use it with Wynntils), and managed to improve the input handling: you can now remap the record key using the Controls menu in this version: `noteblock_music_yoinker-1.12.2-1.0.jar` (this version also doesn't have the issue #1 and #2).

# Differences between versions

The version for 1.12 records all note block sounds, even if they cut midway playing, or bug out early.  
1.15 on the other hand has a system to not play sounds if too many is playing, meaning there won't be cuts midway the notes (which don't matter while recording), instead there will be notes missing, in the recording too. That's why I suggest using the 1.12 version. This can be avoided with a resource pack that shortens the notes that play.

In 1.12 the tick used to record the music is synchronized with the note playback meaning the ticks will always be even (multiplicate of 2). This isn't the case with 1.15, meaning a laggy 4-4 tick delay mostly looks 6-2 in 1.12 and 5-3 in 1.15.  

This isn't related to Minecraft versions, but to the mod version, in 1.12 it uses keybinds and the key needs to be pressed while in the 3D view (in chest e.g. it doesn't work), while in 1.15 it uses a very hacky and bad way that gets the record key no matter where you are, even if you are typing in chat.

# Python scripts

Type --help for options if you want them for any of these.  
Use `midi_converter.py` to turn this data into a MIDI file.  
Use `nbs_converter.py` to turn this data into an NBS file.  
Use `antilagger.py` to even out the timings: e.g. replace 7 and then 5 with 6 and 6.  
Use `simplifier.py` to remove quiet notes and thus simplify the midi.  
Use `speed_changer.py` to multiply the speed by a constant.  
Use `amplifier.py` to amplify the beginning of the music, and compensate for the intro of Wynncraft.
