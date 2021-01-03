#!/usr/bin/python3

import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="speed up or slow down specific .csv files")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-s", "--speed_multiplier", type=float, default = 1.0, help="multiplies the delays with this value and makes it an integer afterwards")
    return vars(parser.parse_args())

def change_speed(data, speed_multiplier):
    new_data = []
    for i in data:
        new_data.append([i[0], str(int(int(i[1]) * speed_multiplier + 0.5)), i[2], i[3]])
    return new_data

def main():
    args = parse_arguments()
    for file in [i for i in noteblock_music_utility.get_input_files(args["input_files"]) if not i[-18:-4] == "_speed_changed"]:
        data = noteblock_music_utility.import_csv_file(file)
        data[0][1] = "0"
        data = change_speed(data, args["speed_multiplier"])
        noteblock_music_utility.create_csv_file(data, file[:-4] + "_speed_changed.csv")

if __name__ == '__main__':
    main()
