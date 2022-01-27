import os
import unittest

print(os.getcwd())
os.chdir('scripts')
print(os.getcwd())

import midi_classes, chord_classes, generators, main




class TestMidiClasses(inittest.TestCase):

	def test_file_class():
		filename = "test.mid"
		tempo = 140
		time_signature = (5, 4)
		tonality = "B"

		file = midi_classes.File(filename, tempo, time_signature, tonality)

		self.assertEqual(file.filename, filename)
		self.assertEqual(file.tempo, tempo)
		self.assertEqual(file.time_signature, time_signature)
		self.assertEqual(file.tonality, tonality)

