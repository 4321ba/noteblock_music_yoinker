#!/usr/bin/python3

import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="simplify specific .csv files by removing notes under a certain volume")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-v", "--volume", type=float, default = 0.71, help="removes the notes under this value")
    return vars(parser.parse_args())

def remove_quiet_notes(data, volume):
    new_data = []
    delay_to_add = 0
    for i in data:
        if float(i[3]) < volume:
            delay_to_add += int(i[1])
        else:
            new_data.append([i[0], str(int(i[1]) + delay_to_add), i[2], i[3]])
            delay_to_add = 0
    return new_data

def main():
    args = parse_arguments()
    for file in [i for i in noteblock_music_utility.get_input_files(args["input_files"]) if not i[-15:-4] == "_simplified"]:
        data = noteblock_music_utility.import_csv_file(file)
        data = remove_quiet_notes(data, args["volume"])
        data[0][1] = "0"
        noteblock_music_utility.create_csv_file(data, file[:-4] + "_simplified.csv")

if __name__ == '__main__':
    main()
