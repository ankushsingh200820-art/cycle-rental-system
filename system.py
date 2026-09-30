# system.py
# The CycleSystem class. It is the "brain" of the program:
# it remembers how many cycles are at every station, books rides,
# keeps the history, and saves/loads everything to a JSON file.

import json
import os
from datetime import datetime

from stations import (ALL_STATIONS, HOSTELS, LOCATIONS,
                      CYCLES_PER_HOSTEL, MAX_CYCLES_PER_STATION,
                      get_distance)
from fares import calculate_fare


class CycleSystem:

    def __init__(self):
        # cycles is a dictionary:  station name -> how many cycles are there
        # history is a list of ride records (each record is a dictionary)
        self.cycles = {}
        self.history = []
        self.reset()

    def reset(self):
        """Go back to the starting state.

        Every hostel gets 30 cycles and the campus locations get none,
        so the total is always 11 * 30 = 330 cycles.
        """
        self.cycles = {}
        for hostel in HOSTELS:
            self.cycles[hostel] = CYCLES_PER_HOSTEL
        for place in LOCATIONS:
            self.cycles[place] = 0

        self.history = []

    def ride(self, student, start, end):
        """Book one ride from start to end.

        Checks the rules first. If everything is fine, one cycle moves
        from start to end, the ride is saved in history, and the record
        is returned so the menu can print it.
        Raises a ValueError with a clear message if the ride is not allowed.
        """
        # get_distance also checks that the station names are valid.
        distance = get_distance(start, end)

        # Rule 1: there must be a cycle available at the pickup station.
        if self.cycles[start] == 0:
            raise ValueError("No cycles available at " + start + ".")

        # Rule 2: the drop station must not be full.
        if self.cycles[end] >= MAX_CYCLES_PER_STATION:
            raise ValueError(end + " is full, cannot park more cycles there.")

        # The ride is allowed. Move one cycle and find the fare.
        fare = calculate_fare(distance)
        self.cycles[start] = self.cycles[start] - 1
        self.cycles[end] = self.cycles[end] + 1

        # Save what happened, so it can be shown in the history later.
        record = {
            "ride_no": len(self.history) + 1,
            "student": student,
            "from": start,
            "to": end,
            "distance": distance,
            "fare": fare,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M"),
        }
        self.history.append(record)
        return record

    def total_earnings(self):
        """Add up the fare of every ride so far."""
        total = 0
        for record in self.history:
            total = total + record["fare"]
        return total

    def low_stations(self, limit=10):
        """Hostels with fewer than `limit` cycles left.

        Students may not find a cycle there, so they need attention.
        """
        low = []
        for name in HOSTELS:
            if self.cycles[name] < limit:
                low.append(name)
        return low

    def crowded_stations(self, limit=45):
        """Stations with more than `limit` cycles.

        Cycles are piling up there, so some should be moved out.
        """
        crowded = []
        for name in ALL_STATIONS:
            if self.cycles[name] > limit:
                crowded.append(name)
        return crowded

    def save(self, path):
        """Write the cycle counts and the history to a JSON file."""
        # Make sure the data folder exists before writing into it.
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)

        data = {"cycles": self.cycles, "history": self.history}

        file = open(path, "w")
        json.dump(data, file, indent=2)
        file.close()

    def load(self, path):
        """Load a previously saved JSON file.

        Returns True if it worked.
        If the file does not exist yet (first run) it just returns False.
        If the file is damaged, we start fresh instead of crashing.
        """
        try:
            file = open(path)
            data = json.load(file)
            file.close()

            # Basic check that the saved data makes sense before using it.
            cycles = data["cycles"]
            for name in ALL_STATIONS:
                if not isinstance(cycles[name], int):
                    raise ValueError("bad cycle count")

            self.cycles = cycles
            self.history = data["history"]
            return True

        except FileNotFoundError:
            # First run, nothing was saved yet. That is fine.
            return False

        except (ValueError, KeyError, TypeError):
            # The file exists but something is wrong with it.
            print("Saved data looks damaged or out of date, starting fresh.")
            self.reset()
            return False
