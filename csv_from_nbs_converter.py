#!/usr/bin/python3

import math
import argparse
import noteblock_music_utility
from sys import exit as sysexit
from os import listdir as oslistdir

def parse_arguments():
    parser = argparse.ArgumentParser(description="convert old format .nbs files to specific .csv files")
    parser.add_argument("input_files", nargs="*", default=[], help="nbs files to convert, leave blank for all from current directory")
    return vars(parser.parse_args())

def get_input_nbs_files(files):
    if len(files) == 0:
        return [i for i in oslistdir() if i[-4:] == ".nbs"]
    else:
        return files
    
def read_byte(file):
    return bytearray(file.read(1))[0]

def read_short(file):
    return read_byte(file) + 256 * read_byte(file)

def read_integer(file):
    return read_short(file) + 65536 * read_short(file)

def read_string(file):
    binary_string = file.read(read_integer(file))
    return binary_string.decode("latin-1", "replace")

def convert_to_csv_file(filename):
    
    instruments = {
        0: "harp",
        1: "bass",
        3: "snare",
        4: "hat",
        2: "basedrum",
        7: "bell",
        6: "flute",
        8: "chime",
        5: "guitar",
        9: "xylophone",
    }
    
    noteblocks = []
    layer_volumes = []
    tempo = -1
    with open(filename, "rb") as file:
        song_length = read_short(file)
        print("Song length: " + str(song_length))
        if song_length == 0:
            sysexit("This script can't read OpenNBS formatted .nbs files, please convert them first to the old (stuffbydavid) format!")
        song_height = read_short(file)
        print("Song height: " + str(song_height))
        print("Song name: " + read_string(file))
        print("Song author: " + read_string(file))
        print("Original song author: " + read_string(file))
        print("Song description: " + read_string(file))
        tempo = read_short(file)
        print("Tempo: " + str(tempo))
        print("Auto-saving: " + str(read_byte(file)))
        print("Auto-saving duration: " + str(read_byte(file)))
        print("Time signature: " + str(read_byte(file)))
        print("Minutes spent: " + str(read_integer(file)))
        print("Left clicks: " + str(read_integer(file)))
        print("Right clicks: " + str(read_integer(file)))
        print("Blocks added: " + str(read_integer(file)))
        print("Blocks removed: " + str(read_integer(file)))
        print("MIDI/Schematic file name: " + read_string(file))
        
        #original code from https://www.stuffbydavid.com/mcnbs/format
        while True:
            horizontal_jumps = read_short(file)
            if horizontal_jumps == 0:
                break
            delta = horizontal_jumps
            layer = -1;
            while True:
                vertical_jumps = read_short(file)
                if vertical_jumps == 0:
                    break
                layer += vertical_jumps;
                instrument = read_byte(file)
                note = read_byte(file)
                noteblocks.append([instrument, delta, note, layer])
                delta = 0
        noteblocks[0][1] = 0
        
        for i in range(song_height):
            print("Layer name: " + read_string(file))
            volume = read_byte(file)
            print("Layer volume: " + str(volume))
            layer_volumes.append(volume)
    
    metronome = int(4000 / tempo + 0.5)
    print("Metronome: " + str(metronome))
    fine_tuning = metronome * tempo / 4000
    print("Fine tuning necessary: " + str(fine_tuning))
    data = []
    for note in noteblocks:
        instrument = instruments[note[0]]
        delta = str(note[1] * metronome)
        pitch = str(round(2 ** ((note[2] - 45) / 12), 2))
        volume = str(layer_volumes[note[3]] / 100)
        data.append([instrument, delta, pitch, volume])
    return data
    
def main():
    args = parse_arguments()
    for filename in get_input_nbs_files(args["input_files"]):
        data = convert_to_csv_file(filename)
        noteblock_music_utility.create_csv_file(data, filename[:-4] + ".csv")

if __name__ == '__main__':
    main()
