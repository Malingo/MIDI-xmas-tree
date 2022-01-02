# MIDI-xmas-tree

## Description of program

The program reads in the 3D coordinates of the LEDs in the tree from a CSV file in GIFT format. It also reads in a song from a MIDI file.

The highest and lowest pitch used in the song are identified, and the total number of semitones between them are divvied up among the LEDs in z-coordinate order. As an example, suppose there are 500 total LEDs on the tree, and the MIDI song has a range from A4 to G5. This range spans 25 semitones, so each pitch will be assigned to 500 / 25 = 20 LEDs. A4 will be assigned to the 20 LEDs with the lowest z-coordinate values, A#4 to the next 20, and so on up the tree's height.

With the LEDs thusly assigned to pitches, the animation is generated. For each note in the MIDI file, the LEDs corresponding to that pitch are lit for the duration of that note. The color is selected from one of 12 equally-spaced colors in RGB space based on the pitch (e.g., G is #B4B400), and the brightness is determined by the velocity of the note within the MIDI file.

The animation is preceded by an 8-beat countdown sequence, which can be helpful if one wishes to cue the music at the same time the animation begins.

## Parameters

There are several adjustable parameters at the top of the program. All filepaths should be specified relative to the location of `xmaslights_MIDI.py`:

* `COORDS_FILENAME` specifies the location of the CSV file containing the LED coordinates in GIFT format.
* `MIDI_FILENAME` specifies the location of the MIDI file containing the song to be animiated.
* `OUTPUT_FILENAME` specifies the location of the CSV file where the resulting animation data should be saved.
* `OVERALL_BRIGHTNESS` can be set between 0 and 255 to control the LED intensity corresponding to a maximum-velocity (127) note in the MIDI file.
* `FRAME_RATE` specifies the number of animation frames that will displayed on the tree per second. If this value does not match the frame rate used to play back the animation file on the tree, then the animation and the music will not be in sync.

## Dependencies

The code requires the `mido` library for interacting with MIDI libraries and the `scipy` library for some of the list manipulations. These can be installed like so:

    pip install mido
    pip install scipy
