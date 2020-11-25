#!/usr/bin/python3

import math
import os
import csv
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="antilag specific .csv files by rounding timing numbers to the base metronome (it can analyze that)")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible miditick difference between notes, e.g. 4 makes 3 or 5 round to 4")
    return vars(parser.parse_args())

def get_input_files(files):
    if len(files) == 0:
        return [i for i in os.listdir() if i[-4:] == ".csv" and not i[-12:-4] == "_antilag"]
    else:
        return files

def import_csv_file(file):
    with open(file, newline='') as csv_file:
        csv_data = csv.reader(csv_file, delimiter=',', quotechar='|')
        return [row for row in csv_data]

def antilag(data, metronome):
    
    #get timing info from data
    timings = {}
    for i in data:
        if not int(i[1]) in timings.keys():
            timings[int(i[1])] = 0
        timings[int(i[1])] += 1
    timings = {key: value for key, value in sorted(timings.items(), key = lambda item: 1.0 / item[1])}
    
    #determine metronome value (the smallest timing used without the lag), mostly a frequent value
    if metronome == -1:
        possible_metronome_ticks = list(timings.keys())[0:3]
        if 0 in possible_metronome_ticks:
            possible_metronome_ticks.remove(0)
        possible_metronome_ticks = possible_metronome_ticks[0:2]
        if (possible_metronome_ticks[0] / possible_metronome_ticks[1]).is_integer():
            metronome = possible_metronome_ticks[1]
        elif (possible_metronome_ticks[1] / possible_metronome_ticks[0]).is_integer():
            metronome = possible_metronome_ticks[0]
        else:
            print("Couldn't find metronome value in", possible_metronome_ticks, "from", timings)
            return []
        print("Found metronome value", metronome)
    else:
        print("Metronome value is given:", metronome)
    
    #determine the correction and print info about it
    lag_correction = {}
    for i in timings:
        lag_correction[i] = int(i / metronome + 0.5) * metronome if not (i / metronome + 0.5).is_integer() else i
        print(i, "to", lag_correction[i], "was found", timings[i], "times")
    
    #apply correction
    new_data = []
    for i in data:
        new_data.append([i[0], str(lag_correction[int(i[1])]), i[2], i[3]])
        
    return new_data

def create_file(data, file):
    new_data = [','.join(i) for i in data]
    csv_string = '\n'.join(new_data) + '\n'
    with open(file, "w") as output_csv:
        output_csv.write(csv_string)

def main():
    args = parse_arguments()
    for file in get_input_files(args["input_files"]):
        data = import_csv_file(file)
        data = antilag(data, args["metronome"])
        data[0][1] = "0"
        create_file(data, file[:-4] + "_antilag.csv")

if __name__ == '__main__':
    main()
