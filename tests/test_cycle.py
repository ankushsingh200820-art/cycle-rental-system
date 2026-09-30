# tests for the cycle system
# run them from the project folder with:
#   python -m unittest discover -s tests -v

import os
import sys
import tempfile
import unittest

# add the project folder to the path so the imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stations import ALL_STATIONS, HOSTELS, find_station, get_distance
from fares import calculate_fare
from system import CycleSystem


class FareTests(unittest.TestCase):
    """The fare at the edges of each slab."""

    def test_slabs(self):
        self.assertEqual(calculate_fare(300), 5)    # last m of slab 1
        self.assertEqual(calculate_fare(301), 10)  # first m of slab 2
        self.assertEqual(calculate_fare(600), 10)
        self.assertEqual(calculate_fare(601), 15)
        self.assertEqual(calculate_fare(1000), 15)
        self.assertEqual(calculate_fare(1001), 20) # above the last slab


class DistanceTests(unittest.TestCase):
    """The distance table."""

    def test_both_directions_same(self):
        # the distance A to B must equal B to A for every pair
        for a in ALL_STATIONS:
            for b in ALL_STATIONS:
                if a != b:
                    self.assertEqual(get_distance(a, b), get_distance(b, a))

    def test_given_values(self):
        self.assertEqual(get_distance("Block 1", "AB2"), 750)
        self.assertEqual(get_distance("Block 5", "Lab Complex"), 1850)
        self.assertEqual(get_distance("Girls Block 1", "AB1"), 650)
        self.assertEqual(get_distance("Girls Block 2", "AB1"), 700)
        self.assertEqual(get_distance("Girls Block 1", "AB2"), 500)
        self.assertEqual(get_distance("Girls Block 2", "Lab Complex"), 850)
        self.assertEqual(get_distance("AB1", "AB2"), 1100)

    def test_boys_ab1_in_range(self):
        # the problem says boys hostels are 1350 to 1650 m from AB1
        for name in ["Block 1", "Block 2", "Block 3", "Block 4", "Block 5",
                     "Block 6", "Block 7", "Block 8A", "Block 8B"]:
            self.assertTrue(1350 <= get_distance(name, "AB1") <= 1650)

    def test_invalid(self):
        # same station twice makes no sense
        with self.assertRaises(ValueError):
            get_distance("AB1", "AB1")
        # a station that does not exist
        with self.assertRaises(ValueError):
            get_distance("AB1", "Library")


class FindStationTests(unittest.TestCase):
    """Changing user input into a proper station name."""

    def test_variants(self):
        self.assertEqual(find_station("b8a"), "Block 8A")
        self.assertEqual(find_station(" Block 8B "), "Block 8B")
        self.assertEqual(find_station("g2"), "Girls Block 2")
        self.assertEqual(find_station("girls block 1"), "Girls Block 1")
        self.assertEqual(find_station("lab"), "Lab Complex")
        self.assertEqual(find_station("Lab Complex"), "Lab Complex")
        self.assertEqual(find_station("ab1"), "AB1")
        self.assertEqual(find_station("3"), "Block 3")  # plain number

    def test_unknown(self):
        self.assertIsNone(find_station("9"))      # there is no Block 9
        self.assertIsNone(find_station("8"))
        self.assertIsNone(find_station("library"))
        self.assertIsNone(find_station(""))


class RideTests(unittest.TestCase):
    """Booking rides and the ride rules."""

    def setUp(self):
        # a fresh system before every test
        self.system = CycleSystem()

    def test_start_counts(self):
        # every hostel starts with 30, locations with 0, total 330
        for hostel in HOSTELS:
            self.assertEqual(self.system.cycles[hostel], 30)
        self.assertEqual(self.system.cycles["AB1"], 0)
        self.assertEqual(self.system.cycles["AB2"], 0)
        self.assertEqual(self.system.cycles["Lab Complex"], 0)
        self.assertEqual(sum(self.system.cycles.values()), 330)

    def test_ride_moves_cycle(self):
        self.system.ride("Asha", "Block 8A", "AB1")
        self.assertEqual(self.system.cycles["Block 8A"], 29)
        self.assertEqual(self.system.cycles["AB1"], 1)
        self.assertEqual(len(self.system.history), 1)

    def test_hostel_to_hostel_allowed(self):
        record = self.system.ride("Ravi", "Block 1", "Girls Block 1")
        self.assertEqual(self.system.cycles["Block 1"], 29)
        self.assertEqual(self.system.cycles["Girls Block 1"], 31)
        self.assertEqual(record["fare"], 20)  # 1200 m

    def test_total_stays_330(self):
        # a ride never creates or destroys a cycle
        self.system.ride("A", "Block 1", "AB1")
        self.system.ride("B", "Girls Block 2", "Lab Complex")
        self.system.ride("C", "AB1", "Block 7")
        self.assertEqual(sum(self.system.cycles.values()), 330)

    def test_no_cycle_available(self):
        with self.assertRaises(ValueError):
            self.system.ride("Asha", "Lab Complex", "Block 1")
        # the failed ride must not change anything
        self.assertEqual(self.system.cycles["Block 1"], 30)

    def test_station_full(self):
        # force AB1 to be full and then try to ride into it
        self.system.cycles["AB1"] = 60
        with self.assertRaises(ValueError):
            self.system.ride("Asha", "Block 8A", "AB1")
        self.assertEqual(self.system.cycles["Block 8A"], 30)

    def test_earnings(self):
        self.system.ride("A", "Girls Block 1", "AB2")   # 500 m -> Rs.10
        self.system.ride("B", "Block 8A", "Block 8B")   # 100 m -> Rs.5
        self.assertEqual(self.system.total_earnings(), 15)

    def test_save_and_load(self):
        # save, then load into a new system and check the data survived
        path = os.path.join(tempfile.gettempdir(), "cycle_test.json")
        self.system.ride("A", "Block 1", "AB2")
        self.system.save(path)

        other = CycleSystem()
        self.assertTrue(other.load(path))
        self.assertEqual(other.cycles, self.system.cycles)
        self.assertEqual(len(other.history), 1)


if __name__ == "__main__":
    unittest.main()
