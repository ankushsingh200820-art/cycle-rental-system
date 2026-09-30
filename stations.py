# stations.py
# All the "map" information of the campus: station names, short codes
# and the distance between every pair of stations.
# The main program and system.py use the functions written here.

# Boys hostels are Block 1 to Block 7 and the two Block 8 buildings.
BOYS_HOSTELS = ["Block 1", "Block 2", "Block 3", "Block 4", "Block 5",
                "Block 6", "Block 7", "Block 8A", "Block 8B"]

# Girls hostels.
GIRLS_HOSTELS = ["Girls Block 1", "Girls Block 2"]

# All hostels together (list + list makes one big list).
HOSTELS = BOYS_HOSTELS + GIRLS_HOSTELS

# The three campus places where students also ride to.
LOCATIONS = ["AB1", "AB2", "Lab Complex"]

# Every station in one list.
ALL_STATIONS = HOSTELS + LOCATIONS

# Short codes so the user does not have to type the full name every time.
# Typing "B3" is the same as typing "Block 3".
STATION_CODES = {
    "B1": "Block 1",
    "B2": "Block 2",
    "B3": "Block 3",
    "B4": "Block 4",
    "B5": "Block 5",
    "B6": "Block 6",
    "B7": "Block 7",
    "B8A": "Block 8A",
    "B8B": "Block 8B",
    "G1": "Girls Block 1",
    "G2": "Girls Block 2",
    "AB1": "AB1",
    "AB2": "AB2",
    "LAB": "Lab Complex",
}

# Each hostel starts with this many cycles.
CYCLES_PER_HOSTEL = 30

# A station can never hold more than this many cycles.
MAX_CYCLES_PER_STATION = 60


# --------------------------------------------------------------------------
# Distances (all in metres)
#
# The boys hostel distances to AB1 and the girls hostel distances are the
# ones given in the problem. The boys distances to AB2 and Lab Complex
# are the same for every block, so they are just written directly.
#
# These are approximate values for simulation, not real measurements.
# --------------------------------------------------------------------------

# For every hostel, the distance to each campus location.
HOSTEL_TO_LOCATION = {
    "Block 1":       {"AB1": 1350, "AB2": 750, "Lab Complex": 1850},
    "Block 2":       {"AB1": 1400, "AB2": 750, "Lab Complex": 1850},
    "Block 3":       {"AB1": 1450, "AB2": 750, "Lab Complex": 1850},
    "Block 4":       {"AB1": 1500, "AB2": 750, "Lab Complex": 1850},
    "Block 5":       {"AB1": 1550, "AB2": 750, "Lab Complex": 1850},
    "Block 6":       {"AB1": 1600, "AB2": 750, "Lab Complex": 1850},
    "Block 7":       {"AB1": 1650, "AB2": 750, "Lab Complex": 1850},
    "Block 8A":      {"AB1": 1600, "AB2": 750, "Lab Complex": 1850},
    "Block 8B":      {"AB1": 1650, "AB2": 750, "Lab Complex": 1850},
    "Girls Block 1": {"AB1": 650,  "AB2": 500, "Lab Complex": 850},
    "Girls Block 2": {"AB1": 700,  "AB2": 500, "Lab Complex": 850},
}

# Distance between the three campus locations.
# AB1 to AB2 was given. The Lab Complex ones are assumed values.
LOCATION_DISTANCES = {
    ("AB1", "AB2"): 1100,
    ("AB1", "Lab Complex"): 900,
    ("AB2", "Lab Complex"): 700,
}

# Hostel to hostel distances are also assumed, using simple rules.
BOYS_TO_BOYS = 400        # any two boys hostels
GIRLS_TO_GIRLS = 200      # any two girls hostels
BOYS_TO_GIRLS = 1200      # a boys hostel and a girls hostel

# Exception: Block 8A and Block 8B are next to each other.
CLOSE_HOSTEL_PAIRS = {
    ("Block 8A", "Block 8B"): 100,
}


def find_station(text):
    """Take whatever the user typed and return the proper station name.

    Works with short codes (B8A, g1, lab), full names in any case
    (block 8a, Girls Block 1) and plain numbers ('3' means Block 3).
    Returns None if nothing matches, so the caller can print an error.
    """
    # Remove extra spaces and make it upper case so 'b8a' == 'B8A'.
    key = text.strip().upper().replace(" ", "")

    # First check: is it a short code like B3 or G1?
    if key in STATION_CODES:
        return STATION_CODES[key]

    # Second check: maybe the user typed the full name, like "Girls Block 1".
    for name in ALL_STATIONS:
        if name.upper().replace(" ", "") == key:
            return name

    # Third check: a plain number like "3" also means Block 3.
    if key.isdigit() and ("B" + key) in STATION_CODES:
        return STATION_CODES["B" + key]

    # Nothing matched.
    return None


def hostel_to_hostel_distance(first, second):
    """Distance between two hostels using the simple rules above."""
    # Check the special close pair in both orders.
    if (first, second) in CLOSE_HOSTEL_PAIRS:
        return CLOSE_HOSTEL_PAIRS[(first, second)]
    if (second, first) in CLOSE_HOSTEL_PAIRS:
        return CLOSE_HOSTEL_PAIRS[(second, first)]

    # Two girls hostels are close to each other.
    if first in GIRLS_HOSTELS and second in GIRLS_HOSTELS:
        return GIRLS_TO_GIRLS

    # Two boys hostels.
    if first in BOYS_HOSTELS and second in BOYS_HOSTELS:
        return BOYS_TO_BOYS

    # One boys and one girls hostel.
    return BOYS_TO_GIRLS


def get_distance(start, end):
    """Distance in metres between two stations.

    Raises an error if a station name is wrong or both are the same,
    because then a ride does not make sense.
    """
    if start not in ALL_STATIONS or end not in ALL_STATIONS:
        raise ValueError("Unknown station.")

    if start == end:
        raise ValueError("Start and destination cannot be the same.")

    # Case 1: both are hostels.
    if start in HOSTELS and end in HOSTELS:
        return hostel_to_hostel_distance(start, end)

    # Case 2: start is a hostel, end is a campus location.
    if start in HOSTELS:
        return HOSTEL_TO_LOCATION[start][end]

    # Case 3: end is a hostel, start is a campus location.
    # (same table, just used the other way round)
    if end in HOSTELS:
        return HOSTEL_TO_LOCATION[end][start]

    # Case 4: both are campus locations.
    # The table is written one way, so check both orders.
    if (start, end) in LOCATION_DISTANCES:
        return LOCATION_DISTANCES[(start, end)]
    return LOCATION_DISTANCES[(end, start)]
