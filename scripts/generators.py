import random

import drum_constants
import chord_classes
import mido_constants
import scale_constants
import errors

from mido_constants import *


CHORD_LENGTHS = [HALF_NOTE_LENGTH, WHOLE_NOTE_LENGTH]


class MetaDataGenerator:
	def __init__(self):
		self.key = self._generate_key()
		self.tempo = self._generate_tempo()
		self.time_signature = (4, 4)

	def _generate_key(self):
		key = scale_constants.KEYS[random.randrange(len(scale_constants.KEYS))]

		if key in ("B", "E"):
			return key + "m"

		if key in ("F"):
			return key

		mode = scale_constants.MODES[random.randrange(len(scale_constants.MODES))]

		return key + mode

	def _generate_tempo(self):
		tempo_range = list(range(60, 140)) + list(range(80, 120))

		return tempo_range[random.randrange(len(tempo_range))]


class DataGenerator:
	def __init__(self, meta_data, nb_of_bars):
		self.meta_data = meta_data
		self.tick_length = TICK_SIZE * meta_data.time_signature[0] * nb_of_bars
		self.tick_length_left = self.tick_length


class ChordProgressionGenerator(DataGenerator):
	def __init__(self, meta_data, nb_of_bars=4):
		super().__init__(meta_data, nb_of_bars)

		self.scale = scale_constants.SCALES[meta_data.key]
		self.scale_notes = [note for note in self.scale]

		self.previous_note = None
		self.chord_progression = self._get_chord_progression()

	def get_chord_progression(self):
		return self.chord_progression

	def _get_chord_progression(self):
		chord_progression = []

		while self.tick_length_left > 0:
			chord_progression.append(self._get_chord(len(chord_progression) == 0))

		if self.scale_notes[4] in chord_progression[-1][0] and "m" in chord_progression[-1][0]:
			chord_progression[-1][0] = self.scale_notes[4]

		return chord_progression

	def _get_chord(self, is_first_chord):
		note = self.scale_notes[0] if is_first_chord else self._get_random_chord_note()
		chord_attr = self.scale[note]

		while chord_attr == "mb5" or note == self.previous_note:
			note = self._get_random_chord_note()
			chord_attr = self.scale[note]

		self.previous_note = note
		return [note + chord_attr, self._get_random_chord_duration()]

	def _get_random_chord_note(self):
		return self.scale_notes[random.randrange(len(self.scale_notes))]

	def _get_random_chord_duration(self):
		duration = min(CHORD_LENGTHS[random.randrange(len(CHORD_LENGTHS))], self.tick_length_left)
		self.tick_length_left -= duration
		return duration


class DrumPatternGenerator(DataGenerator):
	NOTE_DURATION = EIGHTH_NOTE_LENGTH

	def __init__(self, meta_data, nb_of_bars=4):
		super().__init__(meta_data, nb_of_bars)

		self.current_position = 0
		self.drum_pattern = self._get_drum_pattern()

	def get_drum_pattern(self):
		return self.drum_pattern

	def _get_drum_pattern(self):
		drum_pattern = []

		while self.tick_length_left > 0:
			drum_pattern.append(self._get_hit())
			self.tick_length_left -= self.NOTE_DURATION

		return drum_pattern

	def _get_hit(self):
		if self.meta_data.tempo < 100:
			self.NOTE_DURATION = SIXTEENTH_NOTE_LENGTH

		hit = self._get_hit_func()

		self.current_position += self.NOTE_DURATION
		return (hit, self.NOTE_DURATION)

	def _get_hit_func(self):
		func = self._get_simple_time_hit

		if self.NOTE_DURATION == SIXTEENTH_NOTE_LENGTH:
			func = self._get_double_time_hit

		return func()

	def _get_simple_time_hit(self):
		return self._get_full_hit()

	def _get_double_time_hit(self):
		base_multiplier = 8
		snare_multiplier = 4

		return self._get_full_hit(base_multiplier=base_multiplier, snare_multiplier=snare_multiplier)

	def _get_full_hit(self, base_multiplier=4,  kick_multiplier=0, snare_multiplier=2):
		hit = []

		if self.current_position % (self.NOTE_DURATION * base_multiplier) == self.NOTE_DURATION * kick_multiplier:
			hit.append(drum_constants.KICK)

		if self.current_position % (self.NOTE_DURATION * base_multiplier) == self.NOTE_DURATION * snare_multiplier:
			hit.append(drum_constants.SNARE)

		hit.append(drum_constants.HH_CLOSED)

		return hit


class SimpleMelodyGenerator(DataGenerator):
	def __init__(self, chords, meta_data, nb_of_bars=4):
		super().__init__(meta_data, nb_of_bars)
		self.chords = self._get_chord_dict(chords)
		self.tick_iterator = 0
		print(self.chords)

	def get_melody(self):
		melody = []

		while self.tick_length_left > 0:
			note = self._get_note()
			melody.append(note)
			self.tick_iterator += note[1]
			self.tick_length_left -= note[1]

		print(melody)
		return melody

	def _get_note(self, previous_note=None):
		note = ["".join([char for char in self._get_current_chord() if char != "m"]) + "3"]
		length = self._get_note_length()

		return (note, length)

	def _get_current_chord(self):
		reversed_chords = list(self.chords.items())
		reversed_chords.reverse()
		reversed_chords = {key : value for (key, value) in reversed_chords}

		for i, tick_position in enumerate(reversed_chords):
			if self.tick_iterator >= tick_position or i == len(self.chords):
				print (self.tick_iterator)
				return self.chords[tick_position]

	def _get_note_length(self):
		return mido_constants.QUARTER_NOTE_LENGTH

	def _get_chord_dict(self, chords):
		tick_iterator = 0
		chord_dict = {}

		for chord in chords:
			chord_dict[tick_iterator] = chord[0]
			tick_iterator += chord[1]

		return chord_dict






if __name__ == '__main__':
	meta_data = MetaDataGenerator()
	chord_progression = ChordProgressionGenerator(meta_data)
	print(chord_progression.get_chord_progression())