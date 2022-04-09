#!/usr/bin/python3

import argparse
import noteblock_music_utility
from sys import exit as sysexit

def parse_arguments():
    parser = argparse.ArgumentParser(description="antilag specific .csv files by combining many laggy ones")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to merge")
    parser.add_argument("-o", "--output", default = "output.csv", metavar="filename", help="the output file to merge to")
    return vars(parser.parse_args())

def is_all_items_same(list):
    return list.count(list[0]) == len(list)

# Program to find most frequent  
# element in a list 
def most_frequent(list): 
    if len(list) == 0:
        return ""
    return max(set(list), key = list.count) 

def average(data):
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
        
        timing_compare = [int(i[1]) for i in current_line]
        average = int(sum(timing_compare) / len(timing_compare) + 0.5);
        new_data.append([current_line[0][0], str(average), current_line[0][2], current_line[0][3]])
        
    return new_data

def main():
    args = parse_arguments()
    if len(args["input_files"]) == 0:
        sysexit("Please specify the input files!")
    data = [noteblock_music_utility.import_csv_file(file) for file in args["input_files"]]
    data = average(data)
    data[0][1] = "0"
    noteblock_music_utility.create_csv_file(data, args["output"])

if __name__ == '__main__':
    main()
