#!/usr/bin/python3

import math
import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="convert specific .csv files to the Version 4 .nbs format files")
    parser.add_argument("input_files", nargs="*", default=[], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-m", "--metronome", type=int, default=-1, help="the smallest possible tick difference between notes, e.g. 4, can be determined automatically, 40 / metronome = tempo")
    parser.add_argument("-f", "--speed_fine_tune", type=float, default = 1, help="my solution to obscure tempo: metronome value must be integer, but if in theory it is 10/3 e.g. (meaning 40/(10/3)=12 tps in NBS) and in reality it is 3, you should set this to 3/(10/3) = 0.9 meaning the speed will be multiplied by 0.9 and it will be slower then expected")
    parser.add_argument("-s", "--smartness", type=int, default=1, help="how smart the program makes gaps between notes, 0: no gaps, 1 (default): orders the notes by instrument and makes gaps between instruments, 2: keeps original order and uses a quite good algorithm, 3: uses original order, tests all possible scenarios and may be very slow for large files")
    parser.add_argument("-l", "--loopable", action='store_true', dest="is_loopable", help="this turns the nbs file loop on")
    return vars(parser.parse_args())

def get_dummy_note_placement(data):
    max_layer_count = 0
    layer_offsets = []
    layer_names = []
    
    current_layer_count = 0
    for i in data:
        if i[1] == "0":
            current_layer_count += 1
        else:
            if current_layer_count > max_layer_count:
                max_layer_count = current_layer_count
            current_layer_count = 1
        layer_offsets.append(1) #we only want to have jumps=1 every time here
    if current_layer_count > max_layer_count:
        max_layer_count = current_layer_count
    for i in range(max_layer_count):
        layer_names.append("Mix " + str(i + 1)) #so we can see which is the last line there's information in
    return max_layer_count, layer_offsets, layer_names
    
def get_all_layer_counts(data):
    #Here we get all the information from data, how many notes are in each instrument at the ticks, in the same group
    all_layers = [[[data[0][0], 0]]] #e.g. [[["harp", 3], ["bass", 4], ["harp", 2], ...], [["bass", 1], ...], ...] 3D list, 1st D: time, 2nd D: instruments, 3rd: instrument name and the number of layers with it
    for i in data:
        if i[1] == "0":
            if all_layers[-1][-1][0] == i[0]: #if the last note's name is the same
                all_layers[-1][-1][1] += 1
            else:
                all_layers[-1].append([i[0], 1])
        else:
            all_layers.append([[i[0], 1]])
    return all_layers
    
def get_best_layers_with_preference_algorithm(all_layers):
    #Here we determine what order the layers will be in, based on the preference value
    layers = [] #e.g. [["harp", 3], ["bass", 4], ["harp", 2], ...] the number of layers with that instrument
    while len(all_layers) > 0:
        preference = {} #{"harp": [*preference value*, *max number of notes*], "bass": [*preference value*, *max number of notes*], ...}
        for tick in all_layers:
            if tick[0][0] not in preference:
                preference[tick[0][0]] = [0, 0]
            preference[tick[0][0]][0] += len(tick) ** 2 #preference value is calculated by how many different instruments are behind the particular instrument, squared; the biggest value wins
            if preference[tick[0][0]][1] < tick[0][1]:
                preference[tick[0][0]][1] = tick[0][1]
        preference = {key: value for key, value in sorted(preference.items(), key = lambda item: -item[1][0])} #this not only finds the biggest value, but organizes it descending, which we may not really want
        chosen_instrument = list(preference.keys())[0]
        layers.append([chosen_instrument, preference[chosen_instrument][1]])
#        print(preference, chosen_instrument)
        new_layers = []
        for tick in all_layers: #deleting the instruments that got chosen
            if tick[0][0] != chosen_instrument:
                new_layers.append(tick)
            elif len(tick) > 1:
                new_layers.append(tick[1:])
        all_layers = new_layers
    return layers
    
def get_jumps_and_layer_names(data, layers):
    max_layer_count = 0
    layer_offsets = []
    layer_names = []
    #Here we populate the layer_offsets, based on the layers data
    new_layers = layers.copy()
    notes_in_current_instrument = 0
    for i in data:
        jumps = 1
        if i[1] != "0":
            new_layers = layers.copy()
            notes_in_current_instrument = 0
        if new_layers[0][0] == i[0]:
            notes_in_current_instrument += 1
        else:
            while new_layers[0][0] != i[0]:
                jumps += new_layers.pop(0)[1]
            jumps -= notes_in_current_instrument
            notes_in_current_instrument = 1
        layer_offsets.append(jumps)
    #Here we get the names for the layers
    for layer in layers:
        max_layer_count += layer[1]
        for i in range(layer[1]):
            layer_names.append(layer[0].capitalize() + " " + str(i + 1))
    return max_layer_count, layer_offsets, layer_names
    
def get_smart_note_placement(data):
    all_layers = get_all_layer_counts(data)
    layers = get_best_layers_with_preference_algorithm(all_layers)
    print("Identified layers:", layers)
    return get_jumps_and_layer_names(data, layers)

def recursive_analyzer(all_layers, max_count, recursive_counter):
    if recursive_counter >= max_count:
        return False
    preference = {} #e.g. {"harp": 3, "bass": 2, ...}, the number is the max number of notes
    best_layer = []
    for tick in all_layers:
        if tick[0][0] not in preference.keys():
            preference[tick[0][0]] = 0
        if preference[tick[0][0]] < tick[0][1]:
            preference[tick[0][0]] = tick[0][1]
    if len(preference) + recursive_counter >= max_count:
        return False
    for chosen_instrument in preference:
        new_layers = []
        for tick in all_layers: #deleting the instruments that got chosen
            if tick[0][0] != chosen_instrument:
                new_layers.append(tick)
            elif len(tick) > 1:
                new_layers.append(tick[1:])
        if len(new_layers) == 0:
            return [preference[chosen_instrument], [chosen_instrument, preference[chosen_instrument]]]
        recursed_info = recursive_analyzer(new_layers, max_count, recursive_counter + 1)
        if recursed_info and (len(best_layer) == 0 or preference[chosen_instrument] + recursed_info[0] < best_layer[0]):
            best_layer = [preference[chosen_instrument] + recursed_info[0], [chosen_instrument, preference[chosen_instrument]]] + recursed_info[1:]
    return best_layer
    
def get_recursive_note_placement(data):
    all_layers = get_all_layer_counts(data)
    layers = get_best_layers_with_preference_algorithm(all_layers)
    original_layer_count = sum(i[1] for i in layers)
    layers = recursive_analyzer(all_layers, len(layers), 0)[1:]
    print("Identified layers:", layers)
    print("Saved lines:", original_layer_count - sum(i[1] for i in layers))
    return get_jumps_and_layer_names(data, layers)
    
def reorganizer(data, instruments):
    new_data = [[]] #e.g.: [[["harp", "0", "1.0", "1.0"], [...], ...], [[...], [...], ...]]
    delays = [data[0][1]]
    layers = {}
    data[0][1] = "0"
    for i in data:
        if i[1] == "0":
            new_data[-1].append(i)
        else:
            delays.append(i[1])
            new_data.append([[i[0], "0", i[2], i[3]]])
    
    data = []
    for index, tick in enumerate(new_data):
        tick.sort(key = lambda x: instruments[x[0]])
        tick[0][1] = str(delays[index])
        data += tick
        instrument_count = {}
        for note in tick:
            if not note[0] in instrument_count.keys():
                instrument_count[note[0]] = 0
            instrument_count[note[0]] += 1
        for instrument in instrument_count:
            if instrument not in layers.keys() or layers[instrument] < instrument_count[instrument]:
                layers[instrument] = instrument_count[instrument]
    
    new_layers = []
    for instrument in [key for key, value in sorted(instruments.items(), key = lambda item: item[1])]:
        if instrument in layers.keys():
            new_layers.append([instrument, layers[instrument]])
    print("Identified layers:", new_layers)
    max_layer_count, layer_offsets, layer_names = get_jumps_and_layer_names(data, new_layers)
    return max_layer_count, layer_offsets, layer_names, data
    
def write_byte(file, number):
    file.write(bytearray([number]))

def write_short(file, number):
    file.write(bytearray([number % 256, number // 256]))

def write_integer(file, number):
    file.write(bytearray([number % 256, number // 256 % 256, number // 65536 % 256,  number // 16777216]))

def write_string(file, string):
    binary_string = string.encode("latin-1", "replace")
    write_integer(file, len(binary_string))
    file.write(binary_string)

def convert_to_nbs_file(data, metronome, is_loopable, smartness, filename, speed_fine_tune):
    
    instruments = {
        "harp": 0,
        "bass": 1,
        "snare": 3,
        "hat": 4,
        "basedrum": 2,
        "bell": 7,
        "flute": 6,
        "chime": 8,
        "guitar": 5,
        "xylophone": 9,
        "iron_xylophone": 10,
        "cow_bell": 11,
        "didgeridoo": 12,
        "bit": 13,
        "banjo": 14,
        "pling": 15,
    }
    
    metronome = noteblock_music_utility.get_metronome_info(data, metronome, False)
    tempo = int(160 * speed_fine_tune / metronome + 0.5) * 25 #rounding to multiplicate of 25 because ONBS can't be more precise and we don't trust that it can round well
    
    max_layer_count = 0
    layer_offsets = [] #stores the "jumps to next layer" value for each note in the same order as data stores the notes
    layer_names = [] #smart note placement names the track based on the instrument

    if smartness == 0:
        max_layer_count, layer_offsets, layer_names = get_dummy_note_placement(data)
    elif smartness == 1:
        max_layer_count, layer_offsets, layer_names, data = reorganizer(data, instruments)
    elif smartness == 2:
        max_layer_count, layer_offsets, layer_names = get_smart_note_placement(data)
    else:
        max_layer_count, layer_offsets, layer_names = get_recursive_note_placement(data)
    
    #file format: https://opennbs.org/nbs
    with open(filename + ".nbs", "wb") as file:
        write_short(file, 0) #new format always starts this way
        write_byte(file, 4) #version of the NBS format
        write_byte(file, 16) #vanilla instrument count
        write_short(file, 0) #song length, not used
        write_short(file, max_layer_count) #layer count
        write_string(file, "") #song name
        write_string(file, "") #song author
        write_string(file, "") #song original author
        write_string(file, "") #song description
        write_short(file, tempo) #tempo
        write_byte(file, 0) #auto-saving, not used
        write_byte(file, 10) #auto-saving interval, not used
        write_byte(file, 4) #time signature
        write_integer(file, 0) #minutes spent
        write_integer(file, 0) #left-clicks
        write_integer(file, 0) #right-clicks
        write_integer(file, 0) #note blocks added
        write_integer(file, 0) #note blocks removed
        write_string(file, filename + ".csv") #imported file name
        write_byte(file, int(is_loopable)) #looping on or off
        write_byte(file, 0) #max loop count
        write_short(file, 0) #loop start tick
        
        write_short(file, 1 + int(int(data[0][1]) / metronome + 0.5))
        data[0][1] = "0"
        for i in data: #writing the notes
            if int(int(i[1]) / metronome + 0.5) > 0:
                write_short(file, 0) #close previous tick
                write_short(file, int(int(i[1]) / metronome + 0.5)) #jumps to next tick
            write_short(file, layer_offsets.pop(0)) #jumps to next layer
            write_byte(file, instruments[i[0]]) #instrument
            write_byte(file, int(math.log(float(i[2]), 2) * 12 + 45.5)) #pitch
            write_byte(file, int(min(float(i[3]), 1.0) * 100 + 0.5)) #volume
            write_byte(file, 100) #panning
            write_short(file, 0) #pitch fine tuning
        write_short(file, 0) #closing last tick
        write_short(file, 0) #closing the notes section
        
        for i in range(max_layer_count): #this part is said to be optional, except ONBS hangs when not provided
            write_string(file, layer_names[i])
            write_byte(file, 0)
            write_byte(file, 100)
            write_byte(file, 100)
        write_byte(file, 0)

def main():
    args = parse_arguments()
    for file in noteblock_music_utility.get_input_files(args["input_files"]):
        data = noteblock_music_utility.import_csv_file(file)
        convert_to_nbs_file(data, args["metronome"], args["is_loopable"], args["smartness"], file[:-4], args["speed_fine_tune"])

if __name__ == '__main__':
    main()
