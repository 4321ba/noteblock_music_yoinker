#!/usr/bin/python3

import argparse
import noteblock_music_utility
from sys import exit as sysexit

def parse_arguments():
    parser = argparse.ArgumentParser(description="antilag specific .csv files by combining many laggy ones")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to merge")
    parser.add_argument("-o", "--output", default = "output.csv", metavar="filename", help="the output file to merge to")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible miditick difference between notes, e.g. 4 makes 3 or 5 round to 4")
    return vars(parser.parse_args())

def is_all_items_same(list):
    return list.count(list[0]) == len(list)

# Program to find most frequent  
# element in a list 
def most_frequent(list): 
    return max(set(list), key = list.count) 

def merge(data, metronome):
    if metronome == -1:
        new_metronome = noteblock_music_utility.get_metronome_info(data[0], -1, False)
        for i in data[1:]:
            previous_metronome = new_metronome
            new_metronome = noteblock_music_utility.get_metronome_info(i, -1, False)
            if previous_metronome != new_metronome:
                sysexit("Please specify a metronome value, it's ambiguous for me!")
        metronome = new_metronome
    
    lengths = [len(i) for i in data]
    max_lines = max(lengths)
    
    new_data = []
    for row_number in range(max_lines):
        
        current_line = []
        for i, d in enumerate(data):
            if lengths[i] > row_number:
                current_line.append(d[row_number])
        
        non_timing_compare = [[i[0], i[2], i[3]] for i in current_line]
        if not is_all_items_same(non_timing_compare):
            sysexit("The note at line " + str(row_number + 1) + " is not the same across the files, it is " + str(non_timing_compare))
        
        timing_compare = [i[1] for i in current_line]
        good_metronome_timings = [i for i in timing_compare if int(i) % metronome == 0]
        best_candidate = most_frequent(good_metronome_timings)
        second_candidate = most_frequent([i for i in good_metronome_timings if i != best_candidate]) if len(good_metronome_timings) > timing_compare.count(best_candidate) else ""
        
        antilagged_delay = -1
        if timing_compare.count(second_candidate) < timing_compare.count(best_candidate):
            antilagged_delay = best_candidate
        else:
            antilagged_delay = input("What's the best value from here at line " + str(row_number + 1) + " from " + ", ".join(timing_compare) + ": ")
        new_data.append([current_line[0][0], antilagged_delay, current_line[0][2], current_line[0][3]])
        
    return new_data

def main():
    args = parse_arguments()
    if len(args["input_files"]) == 0:
        sysexit("Please specify the input files!")
    data = [noteblock_music_utility.import_csv_file(file) for file in args["input_files"]]
    data = merge(data, args["metronome"])
    data[0][1] = "0"
    noteblock_music_utility.create_csv_file(data, args["output"])

if __name__ == '__main__':
    main()
