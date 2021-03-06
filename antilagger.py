#!/usr/bin/python3

import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="antilag specific .csv files by rounding timing numbers to the base metronome (it can analyze that)")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible miditick difference between notes, e.g. 4 makes 3 or 5 round to 4")
    parser.add_argument("-p", "--precision", type=float, default = 0.16, help="portion of the metronome value to not antilag in e.g. the default 0.16 makes it so that the numbers 3 and 5 won't be rounded with a metronome value of 8 (4 +- 8 * 0.16)")
    parser.add_argument("-a", "--analyze", action='store_true', dest="analyze", help="doesn't make a new file, just prints the information")
    return vars(parser.parse_args())

def antilag(data, metronome, precision):
    metronome, timings = noteblock_music_utility.get_metronome_info(data, metronome, True)
    
    #determine the correction and print info about it
    lag_correction = {}
    for i in timings:
        lag_correction[i] = int(i / metronome + 0.5) * metronome if not 0.5 - precision < (i / metronome) % 1 < 0.5 + precision else i
        print(i, "to", lag_correction[i], "was found", timings[i], "times")
    
    #apply correction
    new_data = []
    for i in data:
        new_data.append([i[0], str(lag_correction[int(i[1])]), i[2], i[3]])
        
    return new_data

def main():
    args = parse_arguments()
    for file in [i for i in noteblock_music_utility.get_input_files(args["input_files"]) if not i[-12:-4] == "_antilag"]:
        data = noteblock_music_utility.import_csv_file(file)
        data[0][1] = "0"
        data = antilag(data, args["metronome"], args["precision"])
        if not args["analyze"]:
            noteblock_music_utility.create_csv_file(data, file[:-4] + "_antilag.csv")

if __name__ == '__main__':
    main()
