#!/usr/bin/python3

import math
import os
import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="make specific .csv files' beginning louder")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible miditick difference between notes, e.g. 4, needed for the louding")
    return vars(parser.parse_args())

def make_beginning_louder(data, metronome):
    metronome = noteblock_music_utility.get_metronome_info(data, metronome, False)
    new_data = []
    current_tick = 0
    for i in data:
        current_tick += int(i[1])
        volume = float(i[3]) * 80 * metronome / (current_tick + 20 * metronome) if current_tick <= 60 * metronome else float(i[3])
        volume = int(volume * 10 + 0.5) / 10
        new_data.append([i[0], i[1], i[2], str(volume)])
    return new_data

def main():
    args = parse_arguments()
    for file in [i for i in noteblock_music_utility.get_input_files(args["input_files"]) if not i[-14:-4] == "_amplified"]:
        data = noteblock_music_utility.import_csv_file(file)
        data = make_beginning_louder(data, args["metronome"])
        data[0][1] = "0"
        noteblock_music_utility.create_csv_file(data, file[:-4] + "_amplified.csv")

if __name__ == '__main__':
    main()
