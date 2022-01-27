import mido

import mido_constants
import errors


class File:
	def __init__(self, file_name, tempo=120, time_signature=(4, 4), tonality="C"):
		self._file = mido.MidiFile(ticks_per_beat=mido_constants.TICK_SIZE)
		self.file_name = file_name
		self.tempo = tempo
		self.time_signature = time_signature
		self.tonality = tonality

		self._tracks = {}

	def add_track(self, track):
		if track.track_id in self._tracks:
			raise errors.NoteAlreadyInTrackError()

		self._add_meta_messages(track, self.tempo, self.time_signature)

		mido_track = track.get_track()

		self._tracks[track.track_id] = mido_track
		self._file.tracks.append(mido_track)

	def save(self):
		self._file.save(self.file_name)

	def _add_meta_messages(self, track, tempo, time_signature):
		track.add_message(Tempo(tempo))
		track.add_message(TimeSignature(time_signature))


class Track:
	CURRENT_ID = 0

	def __init__(self, program_change=0):
		self._track = mido.MidiTrack()
		self.track_id = self._get_new_track_id()

		self._messages = {}

		self.program_change = ProgramChange(program_change)
		self.add_message(self.program_change)

	def add_message(self, message):
		if message.message_id in self._messages:
			raise errors.NoteAlreadyInTrackError()

		self._messages[message.message_id] = message.get_message()
		self._track.append(message.get_message())

	def get_track(self):
		return self._track

	def _get_new_track_id(self):
		track_id = Track.CURRENT_ID
		Track.CURRENT_ID += 1
		return track_id


class Message:
	CURRENT_ID = 0

	def __init__(self):
		self.message_id = self._get_new_message_id()

	def get_message(self):
		return self.message

	def _get_new_message_id(self):
		message_id = Message.CURRENT_ID
		Message.CURRENT_ID += 1
		return message_id


class ProgramChange(Message):
	def __init__(self, program):
		super().__init__()
		self.message = mido.Message('program_change', program=program)

	def get_program(self):
		return self.message.program


class Tempo(Message):
	def __init__(self, tempo):
		super().__init__()
		self.message = mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(tempo))

	def get_tempo(self):
		return mido.tempo2bpm(self.message.tempo)


class TimeSignature(Message):
	def __init__(self, time_signature):
		super().__init__()
		self.message = mido.MetaMessage('time_signature', numerator=time_signature[0], denominator=time_signature[1])

	def get_time_signature(self):
		return self.message.numerator, self.message.denominator


class NoteOnOff(Message):
	def __init__(self):
		super().__init__()


class NoteOn(NoteOnOff):
	def __init__(self, note, velocity, time):
		super().__init__()
		self.message = mido.Message('note_on', note=note, velocity=velocity, time=time)


class NoteOff(NoteOnOff):
	def __init__(self, note, velocity, time):
		super().__init__()
		self.message = mido.Message('note_off', note=note, velocity=velocity, time=time)


class Note:
	def __init__(self, note, velocity, time):
		self.note = note
		self.velocity = velocity
		self.time = time

		self._note_on = NoteOn(note, velocity, self.time)
		self._note_off = None

	def get_note_on_off(self):
		if self._note_off is None:
			return [self._note_on]

		return self._note_on, self._note_off

	def get_note_attrs(self):
		attrs = {
			"note": self.note,
			"velocity": self.velocity,
			"time": self.time,
		}
		return attrs

	def create_off_note(self, length):
		self._note_off = NoteOff(self.note, self.velocity, length)
		return self._note_off

	def add_note_start_to_track(self, track):
		track.add_message(self._note_on)

	def add_note_end_to_track(self, track):
		track.add_message(self._note_off)


class Chord:
	def __init__(self, notes):
		self._notes = notes

	def get_notes(self):
		return self._notes

	def add_chord_to_track(self, track, length=mido_constants.HALF_NOTE_LENGTH):
		self._set_end_of_chord(length)
		for note in self._notes:
			note.add_note_start_to_track(track)
		for note in self._notes:
			note.add_note_end_to_track(track)

	def _set_end_of_chord(self, length):
		for i, note in enumerate(self._notes):
			if i != 0:
				length = 0
			note.create_off_note(length)


if __name__ == "__main__":
	file = File("test.mid")

	track = Track()
	file.add_track(track)
