#!/usr/bin/env python3
"""Solar Rift music player
Play the adaptive music from Solar Rift,
with the ability to adjust the danger level.

This code is under the Creative Commons Attribution 4.0 license.
See https://creativecommons.org/licenses/by/4.0/ for details.

S.D.G.
"""

import glob
import os
import tempfile
import tkinter as tk
from tkinter import ttk
import pydub
from pygame import mixer

# OST save location
OST_PATH = __file__[:__file__.rfind(os.sep)]
print(OST_PATH)

# Period of silence at the beginning and end of each track set, in seconds
TRIM_VALUES = {
    "Moras": (0.15, 0.033),
    "Niveus": (0.1, 0.07),
    "Pyre": (0.1, 0.031),
    }

# The loudest we can set a sound volume to
MAX_AUDIO_VOL = 0.5

# The highest level of danger on the scale
MAX_DANGER_LEVEL = 100

# The names of the various areas in-game
GAME_AREA_NAMES = list(TRIM_VALUES.keys())

# Get all the filenames of the OST mp3s
print("Looking for renamed MP3s")
aafs = glob.glob("*.mp3", root_dir=OST_PATH)
aafs.sort()  # Files may not be in order if we are in temp exe storage
ALL_AUDIO_FNS = aafs
for fn in ALL_AUDIO_FNS:
    print(OST_PATH + os.sep + fn)

# Start PyGame Mixer
mixer.init()


class AreaMusicPlayer:
    """Handle looping and danger levels of area music"""

    def __init__(self):
        """Handle looping and danger levels of area music"""

        # Get and load the tracks that are associated with an area
        print("Loading and trimming files")
        self.game_area_tracks = {
            # For each area name
            an: [
                # Load the sound in PyGame Mixer after trimming off the silence
                self.load_and_trim(fn, an)
                # If the sound filename contains the area name
                for fn in ALL_AUDIO_FNS if an in fn
                ]
            for an in GAME_AREA_NAMES
            }

        # Name of area being played, or None if silence
        self.__area = None

        # Current danger level
        self.__danger_level = 0

    def load_and_trim(self, fn, an):
        """Load an audio into PyGame after trimming it as needed

        Args:
            fn (str): The filename to load.
            an (str): The area name that this file belongs to.

        Returns:
            music (pygame.mixer.Sound): The loopable music sound.
        """

        # Get the filename extension
        file_suffix = "." + fn.split(".")[-1]

        # Load the audio into PyDub
        pds = pydub.AudioSegment.from_file(OST_PATH + os.sep + fn)

        # Trim off the silence for the area
        pds = pds[TRIM_VALUES[an][0] * 1000: -TRIM_VALUES[an][1] * 1000]

        # Save the trimmed audio to a tempfile
        tf = tempfile.NamedTemporaryFile(suffix=file_suffix)
        pds.export(tf)
        tf.file.flush()

        # Load the tempfile into PyGame, then delete it
        s = mixer.Sound(tf)
        tf.close()

        print("Loaded", fn)

        return s

    @property
    def cur_area_tracks(self):
        """Tracks for the current area"""

        if not self.area:
            return []

        return self.game_area_tracks[self.area]

    @property
    def area(self):
        """The current area to play the music of"""
        return self.__area

    @area.setter
    def area(self, new):
        """The current area to play the music of, set to None to stop"""
        # Stop the current music
        for track in self.cur_area_tracks:
            track.stop()

        # All we had to do was stop the music
        if new is None:
            self.__area = None
            return

        assert new in GAME_AREA_NAMES, "Invalid area setting"

        self.__area = new

        self.__update_music_volumes()

        for track in self.cur_area_tracks:
            track.play(-1)

    @property
    def danger_level(self):
        """The current danger level"""
        return self.__danger_level

    @danger_level.setter
    def danger_level(self, new):
        """The current danger level"""
        assert 0 <= new <= MAX_DANGER_LEVEL, "Invalid danger level setting"
        self.__danger_level = new
        self.__update_music_volumes()

    def __update_music_volumes(self):
        """Update the  area music volumes based off of our current danger level"""
        # No area currently loaded, so no volume changes needed
        if not self.area:
            return

        # The combined volumes of all the tracks above the base one,
        # should be between 0 and 3
        vol_to_spread = (self.danger_level / MAX_DANGER_LEVEL) * len(self.cur_area_tracks[1:])

        # For each track, set the volume appropriately
        self.cur_area_tracks[0].set_volume(MAX_AUDIO_VOL)
        for i, track in enumerate(self.cur_area_tracks[1:]):
            track.set_volume(min((max((vol_to_spread - i, 0)), 1)) * MAX_AUDIO_VOL)


class MainWindow(tk.Tk):
    """The main application GUI window"""

    def __init__(self):
        """The main application GUI window"""
        super().__init__()
        self.title("Solar Rift Area Music Player")
        self.geometry("300x100")
        self.player = AreaMusicPlayer()
        print("Starting GUI")
        self.build()
        self.mainloop()

    def build(self):
        """Build the GUI widgets"""
        # Choose an area
        self.area_choice = tk.StringVar(self)
        self.area_choice.set("None")
        self.area_chooser = tk.OptionMenu(
            self,
            self.area_choice,
            *GAME_AREA_NAMES,
            "None",
            command=self.update_area_choice,
            )
        self.area_chooser.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.rowconfigure(0, weight=1)

        # Danger level slider
        tk.Label(self, text="Danger level:").grid(row=1, column=0, sticky=tk.E)
        self.danger_level = tk.DoubleVar(self)
        self.danger_slider = ttk.Scale(
            self,
            to=MAX_DANGER_LEVEL,
            orient="horizontal",
            command=self.update_danger_level,
            variable=self.danger_level,
            )
        self.danger_slider.grid(row=1, column=1, sticky=tk.E + tk.W)
        self.rowconfigure(1, weight=1)

        self.columnconfigure(1, weight=1)

    def update_area_choice(self, a):
        """The area choice has been updated"""
        if a == "None":
            self.player.area = None
            return

        self.player.area = a

    def update_danger_level(self, new):
        """The selected danger level has been updated"""
        self.player.danger_level = float(new)

MainWindow()
mixer.quit()
print("Exit. S.D.G.")
