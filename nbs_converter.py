#!/usr/bin/python3

import math
import argparse
import noteblock_music_utility

def parse_arguments():
    parser = argparse.ArgumentParser(description="convert specific .csv files to .nbs files")
    parser.add_argument("input_files", nargs="*", default = [], help="csv files to convert, leave blank for all from current directory")
    parser.add_argument("-m", "--metronome", type=int, default = -1, help="the smallest possible tick difference between notes, e.g. 4, can be determined automatically, 40 / metronome = tempo")
    parser.add_argument("-d", "--dumb_note_placement", action='store_false', dest="is_note_placement_smart", help="doesn't make gaps between notes that are at the same tick, where it thinks it makes sense")
    parser.add_argument("-l", "--loopable", action='store_true', dest="is_loopable", help="this turns the nbs file loop on")
    return vars(parser.parse_args())

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

def convert_to_nbs_file(data, metronome, is_loopable, is_note_placement_smart, filename):
    
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
    tempo = int(160 / metronome + 0.5) * 25
    
    max_layer_count = 0
    layer_offsets = [] #stores the value for each note in the same order as data
    if is_note_placement_smart:
        layers = [] #e.g. [["harp", 3], ["bass", 4], ["harp", 2], ...] the number of layers with instruments
        current_layers = [[data[0][0], 0]] #same structure as layers
        data.append(["harp", "1", "1.0", "1.0"]) #adding a note to the end to trigger the analization of the last real notes
        for i in data:
            if i[1] == "0":
                if current_layers[-1][0] == i[0]:
                    current_layers[-1][1] += 1
                else:
                    current_layers.append([i[0], 1])
            else:
                print("current:", current_layers)
                layer_index = 0
                for layer in current_layers:
                    if len(layers) <= layer_index:
                        layers.append(layer)
                    elif layers[layer_index][0] == layer[0]:
                        if layer[1] > layers[layer_index][1]:
                            layers[layer_index][1] = layer[1]
                        layer_index += 1
                    else:
                        found_layer = -1
                        for jndex, j in enumerate(layers[layer_index:]):
                            if j[0] == layer[0]:
                                found_layer = jndex
                                break
                        print("new layer", layer, ", found index:", found_layer, "at spliced layers:", layers[layer_index:], ", normal layers:", layers)
                        if found_layer == -1:
                            layers.insert(layer_index + 1, layer)
                            layer_index += 2
                        else:
                            layer_index += found_layer
                            print("testing found index, total:", layer_index)
                            if layer[1] > layers[layer_index][1]:
                                layers[layer_index][1] = layer[1]
                print("overall:", layers)
                current_layers = [[i[0], 1]]
        data.pop() #removing the added note at the end
        
        new_layers = layers.copy()
        notes_in_current_instrument = 0
        for i in data:
            jumps = 1
            if i[1] != "0":
                new_layers = layers.copy()
                notes_in_current_instrument = 0
            if new_layers[0][0] != i[0]:
                while new_layers[0][0] != i[0]:
                    jumps += new_layers.pop(0)[1]
                jumps -= notes_in_current_instrument
                notes_in_current_instrument = 1
            else:
                notes_in_current_instrument += 1
            layer_offsets.append(jumps)
        print(layer_offsets)
        
        for i in layers:
            max_layer_count += i[1]
    
    else:
        current_layer_count = 0
        for i in data:
            if i[1] == "0":
                current_layer_count += 1
            else:
                if current_layer_count > max_layer_count:
                    max_layer_count = current_layer_count
                current_layer_count = 1
        if current_layer_count > max_layer_count:
            max_layer_count = current_layer_count
    
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
            write_short(file, layer_offsets.pop(0) if is_note_placement_smart else 1) #jumps to next layer
            write_byte(file, instruments[i[0]]) #instrument
            write_byte(file, int(math.log(float(i[2]), 2) * 12 + 45.5)) #pitch
            write_byte(file, int(float(i[3]) * 100 + 0.5)) #volume
            write_byte(file, 100) #panning
            write_short(file, 0) #pitch fine tuning
        write_short(file, 0) #closing last tick
        write_short(file, 0) #closing the notes section
        
        for i in range(max_layer_count): #this part is said to be optional, except ONBS hangs when not provided
            write_string(file, "")
            write_byte(file, 0)
            write_byte(file, 100)
            write_byte(file, 100)
        write_byte(file, 0)

def main():
    args = parse_arguments()
    for file in noteblock_music_utility.get_input_files(args["input_files"]):
        data = noteblock_music_utility.import_csv_file(file)
        convert_to_nbs_file(data, args["metronome"], args["is_loopable"], args["is_note_placement_smart"], file[:-4])

if __name__ == '__main__':
    main()
