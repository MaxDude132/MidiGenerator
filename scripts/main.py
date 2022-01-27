import generators
import chord_classes
import midi_classes
import mido_constants


INVERSION_TO_GET = {
	"A": 2,
	"B": 2,
	"C": 0,
	"D": 0,
	"E": 0,
	"F": 1,
	"G": 1
}


class Instrument:
	def __init__(self, metadata, nb_of_bars):
		self.meta_data = metadata
		self.nb_of_bars = nb_of_bars

		self.notes = self._get_notes()
		self.track = self._get_new_track()

		self._add_notes_to_track()

	def _get_notes():
		pass

	def _get_new_track(self):
		track = midi_classes.Track()
		return track

	def _add_notes_to_track(self):
		for note_group in self.notes:
			chord = chord_classes.DefinedNotesChord(note_group[0], 120, 0).get_chord()
			chord.add_chord_to_track(self.track, note_group[1])


class DrumInstrument(Instrument):
	def __init__(self, metadata, nb_of_bars):
		super().__init__(metadata, nb_of_bars)

	def _get_notes(self):
		return generators.DrumPatternGenerator(self.meta_data, self.nb_of_bars).get_drum_pattern()


class ChordInstrument(Instrument):
	def __init__(self, metadata, nb_of_bars):
		super().__init__(metadata, nb_of_bars)

	def _get_notes(self):
		return generators.ChordProgressionGenerator(self.meta_data, self.nb_of_bars).get_chord_progression()

	def _add_notes_to_track(self):
		for chord in self.notes:
			inversion_to_get = INVERSION_TO_GET[chord[0][0]]

			if "m" in chord[0]:
				chord_to_add = chord_classes.MinorChord(chord[0][:-1] + "3", 64, 0).get_chord(inversion_to_get)
			else:
				chord_to_add = chord_classes.MajorChord(chord[0] + "3", 64, 0).get_chord(inversion_to_get)

			chord_to_add.add_chord_to_track(self.track, chord[1])


class SimpleMelodyInstrument(Instrument):
	def __init__(self, chords, metadata, nb_of_bars):
		self.chords = chords
		super().__init__(metadata, nb_of_bars)

	def _get_notes(self):
		return generators.SimpleMelodyGenerator(self.chords, self.meta_data, self.nb_of_bars).get_melody()


class MainProcess:
	def __init__(self, nb_of_bars=4):
		self.nb_of_bars = nb_of_bars

		self.meta_data = self._get_met_data()

		self.drum_instrument = DrumInstrument(self.meta_data, self.nb_of_bars)
		self.chord_instrument = ChordInstrument(self.meta_data, self.nb_of_bars)
		self.simple_melody_instrument = SimpleMelodyInstrument(self.chord_instrument.notes, self.meta_data, self.nb_of_bars)

		self.file = self._get_file(self._get_filename())

		self._add_tracks_to_file()

	def _get_met_data(self):
		return generators.MetaDataGenerator()

	def _add_tracks_to_file(self):
		self.file.add_track(self.drum_instrument.track)
		self.file.add_track(self.chord_instrument.track)
		self.file.add_track(self.simple_melody_instrument.track)

	def _get_filename(self):
		filename = "TESTS/" + self.meta_data.key + "_" + str(self.meta_data.tempo) + "BPM_-_"

		for i, chord in enumerate(self.chord_instrument.notes):
			filename += "-" if i != 0 else ""
			filename += chord[0]

		return filename + ".mid"

	def _get_file(self, filename):
		return midi_classes.File(filename, self.meta_data.tempo, self.meta_data.time_signature, self.meta_data.key)

	def save(self):
		self.file.save()


if __name__ == '__main__':
	main_process = MainProcess()
	main_process.save()



