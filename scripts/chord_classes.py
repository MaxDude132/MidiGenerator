import midi_classes
import errors


NOTE_STRING_TO_INT_DICT = {
	"C": 0,
	"C#": 1,
	"Db": 1,
	"D": 2,
	"D#": 3,
	"Eb": 3,
	"E": 4,
	"E#": 5,
	"Fb": 4,
	"F": 5,
	"F#": 6,
	"Gb": 6,
	"G": 7,
	"G#": 8,
	"Ab": 8,
	"A": 9,
	"A#": 10,
	"Bb": 10,
	"B": 11,
	"B#": 12,
	"Cb": 11
}

OCTAVE = 12


class ChordBase:
	def __init__(self, velocity, time):
		self.velocity = velocity
		self.time = time

	def _get_note_as_int(self, note):
		if isinstance(note, int):
			return note
		elif isinstance(note, str):
			return self._base_note_string_to_int(note)
		else:
			raise errors.InvalidBaseNoteType(note)

	def _base_note_string_to_int(self, note):
		if note[:-1] not in NOTE_STRING_TO_INT_DICT:
			print(note, NOTE_STRING_TO_INT_DICT)
			raise errors.InvalidBaseNoteValue(note)

		return int(note[-1]) * OCTAVE + OCTAVE * 2 + NOTE_STRING_TO_INT_DICT[note[:-1]]


class ThreeNoteChord(ChordBase):
	FIRST_INTERVAL = 0
	SECOND_INTERVAL = 0

	def __init__(self, base_note, velocity, time):
		self.base_note = base_note
		super().__init__(velocity, time)

		self._base_chord = None
		self._first_inversion = None
		self._second_inversion = None

		self._chord_inversions = {
			0: self._get_base_chord,
			1: self._get_first_inversion,
			2: self._get_second_inversion
		}

	def get_chord(self, inversion_number=0):
		fundamental = self._get_note_as_int(self.base_note)
		return self._chord_inversions[inversion_number](fundamental)

	def _get_base_chord(self, fundamental):
		notes = [
			midi_classes.Note(fundamental, self.velocity, self.time),
			midi_classes.Note(fundamental + self.FIRST_INTERVAL, self.velocity, 0),
			midi_classes.Note(fundamental + self.FIRST_INTERVAL + self.SECOND_INTERVAL, self.velocity, 0)
		]

		return midi_classes.Chord(notes)

	def _get_first_inversion(self, fundamental):
		notes = [
			midi_classes.Note(fundamental + self.FIRST_INTERVAL + self.SECOND_INTERVAL - OCTAVE, self.velocity, self.time),
			midi_classes.Note(fundamental, self.velocity, 0),
			midi_classes.Note(fundamental + self.FIRST_INTERVAL, self.velocity, 0),
		]

		return midi_classes.Chord(notes)

	def _get_second_inversion(self, fundamental):
		notes = [
			midi_classes.Note(fundamental + self.FIRST_INTERVAL - OCTAVE, self.velocity, self.time),
			midi_classes.Note(fundamental + self.FIRST_INTERVAL + self.SECOND_INTERVAL - OCTAVE, self.velocity, 0),
			midi_classes.Note(fundamental, self.velocity, 0)
		]

		return midi_classes.Chord(notes)


class MajorChord(ThreeNoteChord):
	FIRST_INTERVAL = 4
	SECOND_INTERVAL = 3

	def __init__(self, base_note, velocity, time):
		super().__init__(base_note, velocity, time)


class MinorChord(ThreeNoteChord):
	FIRST_INTERVAL = 3
	SECOND_INTERVAL = 4

	def __init__(self, base_note, velocity, time):
		super().__init__(base_note, velocity, time)


class DiminishedThreeNoteChord(ThreeNoteChord):
	FIRST_INTERVAL = 3
	SECOND_INTERVAL = 3

	def __init__(self, base_note, velocity, time):
		super().__init__(base_note, velocity, time)


class AugmentedThreeNoteChord(ThreeNoteChord):
	FIRST_INTERVAL = 4
	SECOND_INTERVAL = 4

	def __init__(self, base_note, velocity, time):
		super().__init__(base_note, velocity, time)


class DefinedNotesChord(ChordBase):
	def __init__(self, notes, velocity, time):
		self.notes = notes
		super().__init__(velocity, time)

	def get_chord(self):
		notes = []
		for i, note in enumerate(self.notes):
			note_value = self._get_note_as_int(note)
			time = self.time if i == 0 else 0

			notes.append(midi_classes.Note(note_value, self.velocity, time))

		return midi_classes.Chord(notes)


if __name__ == '__main__':
	file = midi_classes.File("test.mid", tempo=135)

	track = midi_classes.Track()
	file.add_track(track)

	track2 = midi_classes.Track(80)
	file.add_track(track2)

	first_chord = MajorChord("G3", 127, 0).get_chord(1)
	second_chord = MinorChord("E3", 118, 0).get_chord(0)

	first_chord.add_chord_to_track(track, 240)
	second_chord.add_chord_to_track(track, 240)

	first_chord.add_chord_to_track(track2, 240)
	second_chord.add_chord_to_track(track2, 240)

	print(file._tracks)

	file.save()