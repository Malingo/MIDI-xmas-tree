### SETTINGS #######################################################################################

COORDS_FILENAME = 'input/coords_2021.csv'  # LED coordinates, in GIFT format
MIDI_FILENAME = 'input/short_example.mid'  # song to animate, in MIDI format
OUTPUT_FILENAME = 'output/xmas_tree_short_example.csv'  # filename to save CSV output
OVERALL_BRIGHTNESS = 255  # adjust overall animation brightness up to a maximum of 255
FRAME_RATE = 60.0  # frame rate of the animation in frames per second

####################################################################################################

# predefined color for each note in the 12-tone scale [C C# D D# E F F# G G# A A# B]
RGB_COLORS = ((0., 0.577, 0.816), (0., 0., 1.), (0.577, 0., 0.816), (0.707, 0., 0.707),
              (0.816, 0., 0.577), (1., 0., 0.), (0.816, 0.577, 0.), (0.707, 0.707, 0.),
              (0.577, 0.816, 0.), (0., 1., 0.), (0., 0.816, 0.577), (0., 0.707, 0.707))

from mido import MidiFile
import csv
from scipy.stats import rankdata

class LED:
	"""Representation of a single bulb on the LED string."""

	def __init__(self, pitch):
		"""Assign a pitch to this LED, and the corresponding color for that pitch."""
		self.pitch = pitch
		self.color = RGB_COLORS[pitch % 12]
		self.set_intensity(0)  # start unlit by default

	def set_intensity(self, intensity):
		"""Assign an intensity to this LED between 0 and 127."""
		self.rgb_value = [int(OVERALL_BRIGHTNESS * intensity / 127 * cmp) for cmp in self.color]

def _convert_time_to_frame(time, tempo):
	"""Convert a MIDI timestamp (in ticks) to a frame number."""
	# frames = ticks / (ticks/beat) * (µsec/beat) / (sec/µsec) * (frames/sec)
	return round(time / ticks_per_beat * tempo / 1_000_000 * FRAME_RATE)

####################################################################################################

### Read in MIDI file
min_pitch = 128
max_pitch = 0
messages = []
prior_time = -7680  # length of intro_file
with MidiFile('input/countdown.mid') as intro_file, MidiFile(MIDI_FILENAME) as midi_file:
	ticks_per_beat = midi_file.ticks_per_beat
	for track in ([intro_file.tracks[0]] + midi_file.tracks):
		for message in track:
			message.time += prior_time  # convert from time since last message to time since start of song
			prior_time = message.time
			messages.append(message)
			if message.type == 'note_on':
				min_pitch = min(min_pitch, message.note)
				max_pitch = max(max_pitch, message.note + 1)
			elif message.type == 'end_of_track':
				prior_time = 0
	messages.sort(key=lambda message: message.time)

### Read in LED coordinates
with open(COORDS_FILENAME, newline='', encoding='utf-8-sig') as coord_file:
	coord_reader = csv.reader(coord_file, quoting=csv.QUOTE_NONNUMERIC)
	heights = [z for (x, y, z) in coord_reader]
	height_ranks = rankdata(heights, method='ordinal')
LED_COUNT = len(height_ranks)  # 500

### Create LED string and assign pitch to each LED based on height
led_string = []
for rank in height_ranks:
	pitch = int((max_pitch - min_pitch) / LED_COUNT * rank) + min_pitch
	led_string.append(LED(pitch))

### Generate the LED data for each frame of the animation based on the MIDI messages
frame_list = []
current_tempo = 500_000
message = messages[0]
for next_message in messages[1:]:
	if message.type == 'set_tempo':
		current_tempo = message.tempo
	elif message.type.startswith('note_'):
		velocity = message.velocity if message.type == 'note_on' else 0
		for led in led_string:
			if led.pitch == message.note: led.set_intensity(velocity)
	if message.time != next_message.time:  # done with this frame
		frame_no = _convert_time_to_frame(message.time, current_tempo)
		next_frame_no = _convert_time_to_frame(next_message.time, current_tempo)
		for _ in range(frame_no, next_frame_no):
			frame_list.append([led.rgb_value for led in led_string])
	message = next_message
frame_list.append([[0, 0, 0] for led in led_string])  # clear tree as final frame of animation

### Print animation to output CSV file
with open(OUTPUT_FILENAME, 'w') as out_file:
	print('FRAME_ID', *[f'R_{i},G_{i},B_{i}' for i in range(LED_COUNT)], sep=',', file=out_file)
	for frame_id, frame_data in enumerate(frame_list):
		print(frame_id, *[cmp for led in frame_data for cmp in led], sep=',', file=out_file)
