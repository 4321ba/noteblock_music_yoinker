#!/usr/bin/python3

import argparse
import noteblock_music_utility

from splitter import split
from speed_changer import change_speed
from antilagger import antilag
from merger import merge
from averager import average

from new_nbs_converter import convert_to_nbs_file

def parse_arguments():
    parser = argparse.ArgumentParser(description="apply many transformations to a looped piece to remove lag, calls the many other .py files")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for one? from current directory")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible miditick difference between notes, multiplied by 100, e.g.: 10tps = 400 (*100 HERE ONLY)")
    return vars(parser.parse_args())

def main():
    args = parse_arguments()
    file = noteblock_music_utility.get_input_files(args["input_files"])[0]
    data = noteblock_music_utility.import_csv_file(file)
    
    data = split(data)
    
    new_data = []
    for part in data:
        new_data.append(change_speed(part, 100))
    data = new_data
    
    #TODO a system for determining metronome value
    if (args["metronome"] == -1):
        raise SystemExit("pls gimme metronome value")
    metronome = args["metronome"]
    metronome = metronome // 2 # halving metronome, in case there are just a very few doublespeed notes sprinkled in
    
    # doing it one way: first antilagging the individual loops, then mergeing them into one loop
    data_antilagged_full_metronome = []
    data_antilagged_half_metronome = []
    for part in data:
        data_antilagged_full_metronome.append(antilag(part, metronome*2, 0.05)) # 0.16 TODO
        print(""); # TODO verbose=False?
        data_antilagged_half_metronome.append(antilag(part, metronome,   0.05)) # 0.16 TODO
        print("");
    data_merged_full = merge(data_antilagged_full_metronome, metronome*2, verbose=False)
    data_merged_half = merge(data_antilagged_half_metronome, metronome,   verbose=False)
    
    # doing it the other way: first averaging them, then antilag that one loop
    data_averaged = average(data)
    data_averaged_full = antilag(data_averaged, metronome*2, 0)
    print("");
    data_averaged_half = antilag(data_averaged, metronome,   0)
    print("");
    
    # merging the 4 different ways we tried to remove lag, to see if they are the same
    print("4 different ways of antilagging, in order: [merged half metronome], [merged full metronome], [averaged half metronome], [averaged full metronome]");
    data = [data_merged_half, data_merged_full, data_averaged_half, data_averaged_full]
    data = merge(data, metronome)
    
    # we slowed down the whole thing by *100, to be able to fine tune the delays (they are int)
    # now we need to speed them back up, however also compensating for fine tuning
    target_metronome = int(0.5 + metronome / 100)
    data = change_speed(data, target_metronome / metronome)
    
    # 40 = tick in the csv file per second
    fine_tuning_imprecise = 100 * target_metronome / metronome
    tps_imprecise = 40 / target_metronome * fine_tuning_imprecise
    tps_precise = int(0.5 + tps_imprecise * 4) / 4
    fine_tuning_precise = tps_precise * target_metronome / 40
    print(f"Needed fine-tuning will be {fine_tuning_precise}.")
    
    data[0][1] = "0"
    noteblock_music_utility.create_csv_file(data, file[:-4] + "_mastered.csv")

if __name__ == '__main__':
    main()
