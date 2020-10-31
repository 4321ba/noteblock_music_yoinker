# noteblock_music_yoinker
 Minecraft Forge mod for yoinking noteblock music you hear.

Requires Minecraft 1.15.2 and Forge.

# Usage

Press R to start recording music to the `.minecraft/recorded_music` folder. Press R again to stop recording.

File format:  
Music is recorded in csv format, every line is a new note.  
1st value is the instrument.  
2nd value is the number of ticks since the previous line.  
3rd value is the pitch ranging from 0.5 to 2.0.  
4th value is the volume ranging from 0 to 1, but it's sometimes 3 too (from real note block).

I also made a Python script to turn this data into a MIDI file, I'll put a link here when I upload it.
