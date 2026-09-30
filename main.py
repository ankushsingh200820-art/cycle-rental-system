# main.py
# The menu program. This is the file the user runs.
#
#   python main.py          -> normal menu
#   python main.py --demo   -> runs a few sample rides without any typing

import sys

from stations import ALL_STATIONS, HOSTELS, LOCATIONS, find_station, get_distance
from fares import FARE_SLABS, FARE_ABOVE_LAST_SLAB, calculate_fare
from system import CycleSystem

# All rides are saved here, so nothing is lost when the program closes.
DATA_FILE = "data/cycle_data.json"

MENU = """
===== VIT Bhopal Cycle Sharing =====
1. Show cycles at every station
2. Take a ride
3. Fare chart
4. Ride history
5. Earnings summary
6. Stations that need attention
7. Reset system
0. Exit
"""

STATION_HELP = ("Station codes: B1-B7, B8A, B8B (boys hostels), G1, G2 (girls hostels),\n"
                "                AB1, AB2, LAB (Lab Complex)")


# ----- option 1: show the cycles at every station -------------------------

def show_availability(system):
    print("\nStation         Cycles")
    print("-" * 22)
    for name in ALL_STATIONS:
        # :<15 makes the names line up in a column.
        print(f"{name:<15} {system.cycles[name]}")
    print("-" * 22)
    print(f"{'Total':<15} {sum(system.cycles.values())}")


# ----- option 2: take a ride ---------------------------------------------

def take_ride(system):
    # Ask for the name first.
    student = input("Your name: ").strip()
    if student == "":
        print("Name cannot be empty.")
        return

    # Ask where to pick up and drop the cycle.
    print(STATION_HELP)
    start = find_station(input("Pick up from: "))
    end = find_station(input("Drop at: "))

    # find_station returns None when the user typed something unknown.
    if start is None or end is None:
        print("Unknown station. Please use one of the station codes shown above.")
        return

    # Check the distance (this also rejects start == end).
    try:
        distance = get_distance(start, end)
    except ValueError as error:
        print("Sorry:", error)
        return

    # Show the fare and ask before actually booking the ride.
    fare = calculate_fare(distance)
    print(f"{start} -> {end}: {distance} m, fare Rs.{fare}")

    answer = input("Confirm ride? (y/n): ").strip().lower()
    if answer != "y":
        print("Ride cancelled.")
        return

    # Book the ride. system.ride checks the cycle rules and
    # raises an error if the pickup is empty or the drop is full.
    try:
        record = system.ride(student, start, end)
    except ValueError as error:
        print("Sorry:", error)
        return

    print(f"\nRide #{record['ride_no']} done. Enjoy, {student}!")
    print(f"{start} now has {system.cycles[start]} cycles, "
          f"{end} now has {system.cycles[end]}.")
    print(f"Please pay Rs.{record['fare']}.")

    # Save after every ride so nothing is lost if the program closes.
    system.save(DATA_FILE)


# ----- option 3: fare chart ----------------------------------------------

def show_fare_chart():
    # First the simple slab table.
    print("\nFare slabs:")
    lower = 0
    for limit, fare in FARE_SLABS:
        print(f"  {lower + 1} - {limit} m : Rs.{fare}")
        lower = limit
    print(f"  above {lower} m : Rs.{FARE_ABOVE_LAST_SLAB}")

    # Then every hostel's distance and fare to each location.
    print("\nHostel to locations (distance, fare):")
    print(f"{'Hostel':<15} " + "".join(f"{place:<17}" for place in LOCATIONS))
    for hostel in HOSTELS:
        row = f"{hostel:<15} "
        for place in LOCATIONS:
            d = get_distance(hostel, place)
            row = row + f"{d} m Rs.{calculate_fare(d)}".ljust(17)
        print(row)

    # Distances between the three locations.
    print("\nBetween locations:")
    pairs = [("AB1", "AB2"), ("AB1", "Lab Complex"), ("AB2", "Lab Complex")]
    for first, second in pairs:
        d = get_distance(first, second)
        print(f"  {first} <-> {second}: {d} m, Rs.{calculate_fare(d)}")

    # A few hostel-to-hostel examples.
    print("\nBetween hostels:")
    examples = [
        ("boys hostel <-> boys hostel", "Block 1", "Block 2"),
        ("Block 8A <-> Block 8B", "Block 8A", "Block 8B"),
        ("girls hostel <-> girls hostel", "Girls Block 1", "Girls Block 2"),
        ("boys hostel <-> girls hostel", "Block 1", "Girls Block 1"),
    ]
    for label, first, second in examples:
        d = get_distance(first, second)
        print(f"  {label}: {d} m, Rs.{calculate_fare(d)}")


# ----- option 4: ride history --------------------------------------------

def show_history(system):
    if len(system.history) == 0:
        print("No rides yet.")
        return

    print("\nNo  Name        From           To             Fare   Time")
    for r in system.history:
        print(f"{r['ride_no']:<3} {r['student']:<11} {r['from']:<14} {r['to']:<14} "
              f"Rs.{r['fare']:<4} {r['time']}")


# ----- option 5: earnings summary ----------------------------------------

def show_earnings(system):
    print("Total rides   :", len(system.history))
    print("Total earnings: Rs." + str(system.total_earnings()))


# ----- option 6: stations that need attention ----------------------------

def show_attention(system):
    low = system.low_stations()
    crowded = system.crowded_stations()

    if len(low) == 0 and len(crowded) == 0:
        print("All stations look balanced.")
        return

    for name in low:
        print(f"LOW     {name} has only {system.cycles[name]} cycles.")
    for name in crowded:
        print(f"CROWDED {name} has {system.cycles[name]} cycles, move some out.")


# ----- the menu loop ------------------------------------------------------

def run_menu(system):
    # Show the menu again and again until the user presses 0.
    while True:
        print(MENU)
        choice = input("Choose: ").strip()

        if choice == "1":
            show_availability(system)
        elif choice == "2":
            take_ride(system)
        elif choice == "3":
            show_fare_chart()
        elif choice == "4":
            show_history(system)
        elif choice == "5":
            show_earnings(system)
        elif choice == "6":
            show_attention(system)
        elif choice == "7":
            # Reset is destructive, so ask first.
            sure = input("This erases all rides. Sure? (y/n): ").strip().lower()
            if sure == "y":
                system.reset()
                system.save(DATA_FILE)
                print("System reset.")
        elif choice == "0":
            system.save(DATA_FILE)
            print("Goodbye!")
            break
        else:
            print("Please choose a number from the menu.")


# ----- demo mode ----------------------------------------------------------

def run_demo():
    """Run a few rides automatically, so the program can be tried
    without typing anything. The last ride is meant to fail,
    to show what an error looks like."""
    system = CycleSystem()

    rides = [
        ("Asha", "Block 8A", "AB1"),
        ("Ravi", "Block 1", "AB2"),
        ("Meena", "AB1", "Block 8A"),
        ("Karan", "Girls Block 1", "Lab Complex"),
        ("Zoya", "Block 2", "Block 3"),
        ("Dev", "Lab Complex", "Block 1"),
        ("Neha", "Lab Complex", "Girls Block 2"),
    ]

    for student, start, end in rides:
        try:
            r = system.ride(student, start, end)
            print(f"{student}: {start} -> {end}, {r['distance']} m, Rs.{r['fare']}")
        except ValueError as error:
            print(f"{student}: {start} -> {end} failed: {error}")

    show_availability(system)
    show_earnings(system)


# ----- program start ------------------------------------------------------

def main():
    # Demo mode: run the sample rides and stop.
    if "--demo" in sys.argv:
        run_demo()
        return

    # Normal mode: load any saved data, then show the menu.
    system = CycleSystem()
    if system.load(DATA_FILE):
        print("Loaded saved data.")

    try:
        run_menu(system)
    except (EOFError, KeyboardInterrupt):
        # Ctrl+C or end of input should not lose the data.
        system.save(DATA_FILE)
        print("\nGoodbye!")


if __name__ == "__main__":
    main()
