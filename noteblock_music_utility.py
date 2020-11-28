#!/usr/bin/python3

from csv import reader as csvreader
from sys import exit as sysexit
from os import listdir as oslistdir

def get_input_files(files):
    if len(files) == 0:
        return [i for i in oslistdir() if i[-4:] == ".csv"]
    else:
        return files

def import_csv_file(file):
    with open(file, newline='') as csv_file:
        csv_data = csvreader(csv_file, delimiter=',', quotechar='|')
        return [row for row in csv_data]

def create_csv_file(data, file):
    new_data = [','.join(i) for i in data]
    csv_string = '\n'.join(new_data) + '\n'
    with open(file, "w") as output_csv:
        output_csv.write(csv_string)

def get_metronome_info(data, metronome, return_timings): #metronome is the value defined by the user, -1 if nothing is defined
    
    if metronome != -1 and not return_timings:
        print("Metronome value is", metronome)
        return metronome
    
    #get timing info from data
    timings = {}
    for i in data:
        if not int(i[1]) in timings.keys():
            timings[int(i[1])] = 0
        timings[int(i[1])] += 1
    timings = {key: value for key, value in sorted(timings.items(), key = lambda item: -item[1])}
    
    #determine metronome value (the smallest timing used without the lag), mostly a frequent value
    if metronome == -1:
        possible_metronome_ticks = list(timings.keys())[0:3]
        if 0 in possible_metronome_ticks:
            possible_metronome_ticks.remove(0)
        possible_metronome_ticks = possible_metronome_ticks[0:2] #get 2 most frequent delays that aren't 0
        
        if len(possible_metronome_ticks) == 1:
            metronome = possible_metronome_ticks[0]
        elif (possible_metronome_ticks[0] / possible_metronome_ticks[1]).is_integer(): #one is the multiplicate of the other
            metronome = possible_metronome_ticks[1]
        elif (possible_metronome_ticks[1] / possible_metronome_ticks[0]).is_integer():
            metronome = possible_metronome_ticks[0]
        elif abs(possible_metronome_ticks[0] - possible_metronome_ticks[1]) == 1: #they're the same just the odd one is the one with lag
            if (possible_metronome_ticks[0] / 2).is_integer:
                metronome = possible_metronome_ticks[0]
            else:
                metronome = possible_metronome_ticks[1]
        else:
            sysexit("Couldn't find metronome value in " + str(possible_metronome_ticks) + " from " + str(timings))
    print("Metronome value is", metronome)

    if return_timings:
        return metronome, timings
    return metronome
