#!/usr/bin/python3

import sys
from nbswave import render_audio

def export(in_file):
    render_audio(in_file, in_file[:-4] + ".wav", default_sound_path="/home/balint/Documents/GitHub/nbs-audio/sounds")

if __name__ == '__main__':
    export(sys.argv[1])
