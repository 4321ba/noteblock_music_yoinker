#!/usr/bin/python3

import argparse
import noteblock_music_utility
from sys import exit as sysexit

def parse_arguments():
    parser = argparse.ArgumentParser(description="split a recording into many csv files, name will be [oldname]_split_n.csv")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to split")
    return vars(parser.parse_args())

def is_all_items_same(list):
    return list.count(list[0]) == len(list)

# Program to find most frequent  
# element in a list 
def most_frequent(list): 
    if len(list) == 0:
        return ""
    return max(set(list), key = list.count) 

def split(data):
    loop_length = 0
    for possible_loop_length in range(1, len(data) // 2 + 1):
        found_good_loop = True
        possible_loop = [(i[0], i[2], i[3]) for i in data[0:possible_loop_length]]
        for loop_begin in range(possible_loop_length, len(data) // 2 + 1, possible_loop_length):
            if possible_loop != [(i[0], i[2], i[3]) for i in data[loop_begin : loop_begin+possible_loop_length]]:
                found_good_loop = False
                #print(f"ll {possible_loop_length} at loopbegin {loop_begin} not good: {possible_loop} and {[(i[0], i[2], i[3]) for i in data[loop_begin : loop_begin+possible_loop_length]]} are not the same")
                break
        if found_good_loop:
            loop_length = possible_loop_length
            break
            
    if loop_length == 0:
        sysexit("Couldn't find the loop length, nothing was reoccuring.")
    
    print(f"Data is {len(data)} long, found loop length of {loop_length}, it loops {len(data) // loop_length} times, cutting out {len(data) % loop_length} notes at the end.")
    new_data = []
    for i in range(0, len(data) - loop_length, loop_length):
        new_data.append(data[i:i+loop_length])
    # TODO maybe output the remaining notes into a file too?
    return new_data

def main():
    args = parse_arguments()
    for file in [i for i in noteblock_music_utility.get_input_files(args["input_files"]) if not "split" in i]:
        data = noteblock_music_utility.import_csv_file(file)
        data[0][1] = "0"
        data = split(data)
        for i, part_data in enumerate(data):
            noteblock_music_utility.create_csv_file(part_data, file[:-4] + f"_split_{i}.csv")

if __name__ == '__main__':
    main()
