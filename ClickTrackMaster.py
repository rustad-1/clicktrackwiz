from mido import MidiFile, MidiTrack, MetaMessage, Message
import os

# Copyright (©) 2024 Rustad Publishing.

class ClickTrackWiz:
    """
    Class to generate click tracks with tempo, time signature, markers, and vamp sections.
    """

    def __init__(self, output_folder="MidiFiles", ticks_per_beat=480):
        """
        Initialize the MIDI file and output settings.
        Parameters:
            output_folder (str): Folder to save MIDI files.
            ticks_per_beat (int): Ticks per beat (default: 480).
        """
        self.midi = MidiFile(ticks_per_beat=ticks_per_beat)
        self.track = MidiTrack()
        self.midi.tracks.append(self.track)
        self.output_folder = output_folder
        self.measure_offset = 0
        self.beats_per_measure = 0
        self.current_measure = 1
        self.time_position = 0

    def initialize(self):
        """Start a new track with default tempo (120 BPM) and time signature (4/4)."""
        self.track = MidiTrack()
        self.midi.tracks = [self.track]
        self.track.append(MetaMessage('set_tempo', tempo=500000, time=0))
        self.track.append(MetaMessage('time_signature', numerator=4, denominator=4, time=0))
        self.time_position = 0

    def tempo(self, bpm):
        """
        Set tempo in BPM.
        Parameters:
            bpm (int): Beats per minute.
        """
        self.track.append(MetaMessage('set_tempo', tempo=int(60000000 / bpm), time=0))

    def apply_accel_decel_smooth(self, start_tempo, end_tempo, length):
        """
        Apply smooth tempo changes across measures.
        Parameters:
            start_tempo (int): Starting BPM.
            end_tempo (int): Ending BPM.
            length (int): Number of measures for the change.
        """
        if self.beats_per_measure == 0:
            raise ValueError("Set time signature first.")
        bpm_step = (end_tempo - start_tempo) / (length * self.beats_per_measure - 1)
        ticks_per_beat = self.midi.ticks_per_beat
        bpm = start_tempo
        for _ in range(length * self.beats_per_measure):
            self.track.append(MetaMessage('set_tempo', tempo=int(60000000 / bpm), time=0))
            self.track.append(Message('note_on', note=60, velocity=64, time=0))
            self.track.append(Message('note_off', note=60, velocity=64, time=ticks_per_beat))
            bpm += bpm_step

    def timesig(self, beats_per_measure, note_value):
        """
        Set time signature.
        Parameters:
            beats_per_measure (int): Beats per measure.
            note_value (int): Note value representing one beat.
        """
        self.beats_per_measure = beats_per_measure
        self.track.append(MetaMessage('time_signature', numerator=beats_per_measure, denominator=note_value, time=0))

    def count_in(self, num_measures):
        """
        Add count-in measures with silent notes.
        Parameters:
            num_measures (int): Number of count-in measures.
        """
        ticks_per_beat = self.midi.ticks_per_beat
        for _ in range(num_measures):
            self.track.append(Message('note_on', note=60, velocity=64, time=0))
            self.track.append(Message('note_off', note=60, velocity=64, time=ticks_per_beat * self.beats_per_measure))

    def insert_measures(self, num_measures):
        """
        Insert silent measures.
        Parameters:
            num_measures (int): Number of measures.
        """
        ticks_per_beat = self.midi.ticks_per_beat
        for _ in range(num_measures):
            self.track.append(Message('note_on', note=60, velocity=64, time=0))
            self.track.append(Message('note_off', note=60, velocity=64, time=ticks_per_beat * self.beats_per_measure))
        self.current_measure += num_measures

    def skip_measures(self, num_measures):
        """Skip measures without adding events."""
        self.current_measure += num_measures

    def unskip_measures(self, num_measures):
        """Set back measure count without adding events."""
        self.current_measure -= num_measures

    def rehearsal_number(self, measure=None):
        """
        Add rehearsal marker.
        Parameters:
            measure (int): Measure number to display (default: current measure).
        """
        self.track.append(MetaMessage('marker', text=f"m.{measure or self.current_measure}", time=0))

    def vamp(self, num_measures):
        """
        Add a vamp section with a marker. Trigger the "Vamp"
        Parameters:
            num_measures (int): Number of vamp measures.
        """
        self.track.append(MetaMessage('marker', text=f"Vamp m.{self.current_measure}", time=0))
        ticks_per_beat = self.midi.ticks_per_beat
        for _ in range(num_measures):
            self.track.append(Message('note_on', note=60, velocity=64, time=0))
            self.track.append(Message('note_off', note=60, velocity=64, time=ticks_per_beat * self.beats_per_measure))
        self.current_measure += num_measures

    def go(self):
        """Add a 'Go' marker and trigger the "Go" midi note."""
        self.track.append(MetaMessage('marker', text="Go", time=0))
        self.track.append(Message('note_on', note=73, velocity=127, time=0))
        self.track.append(Message('note_off', note=73, velocity=127, time=self.midi.ticks_per_beat * self.beats_per_measure))
        self.current_measure += 1

    def save_midi(self, filename):
        """
        Save the MIDI file.
        Parameters:
            filename (str): Name of the file.
        """
        os.makedirs(self.output_folder, exist_ok=True)
        self.midi.save(os.path.join(self.output_folder, f"{filename}.midi"))
        print(f"Saved to {self.output_folder}/{filename}.midi")
