# Project Statement: VIT Bhopal Cycle Sharing System

## Problem statement

Hostels at VIT Bhopal are far from the academic blocks and the Lab Complex. Boys' hostels are roughly 1.3 to 1.9 km away, and walking takes a long time between classes. A shared-cycle service can help, but it only works if someone keeps track of how many cycles are at each place and how much each trip should cost. Doing this by hand leads to mistakes: cycles pile up at the academic blocks, hostels run out, and fares are inconsistent.

This project is a command-line program that keeps count of cycles at every hostel and campus location, moves a cycle from one place to another when a student takes a ride, and charges a fare based on the distance travelled.

## Objectives

1. Keep an accurate count of cycles at all 14 stations, with the total always 330, because a ride only moves a cycle.
2. Book rides between any two stations with a fare calculated from the distance using the four slabs (Rs.5, Rs.10, Rs.15, Rs.20).
3. Enforce the ride rules: no ride from an empty station, no ride to a full station (60 cycles).
4. Keep a ride history and give earnings and station reports, so the service can be managed and cycles rebalanced.
5. Save the data after every ride and load it on the next start, with validation and clear error messages instead of crashes.
6. Use only the Python standard library and cover the core logic with unit tests.

## Scope of the project

**Included**

- 11 hostels (9 boys' blocks: Block 1-7, 8A, 8B; 2 girls' blocks) and 3 campus locations (AB1, AB2, Lab Complex).
- 30 cycles at every hostel at the start (330 in total); the three locations start with none.
- Rides between any two hostels, between a hostel and a location, and between locations.
- Distance-based fare slabs of Rs.5, Rs.10, Rs.15 and Rs.20.
- Ride history, earnings summary, and a report of stations that are running low or crowded.
- Saving and loading data between runs, with input validation and clear error messages.

**Not included**

- Live GPS tracking or a mobile/web app; the program runs in the terminal only.
- Real payment processing.
- Tracking individual cycles by number or their condition.
- Real surveyed distances; the distances used are approximate simulation values.

## Target users

- **Students**, who choose where to pick up and drop a cycle and see the fare before confirming.
- **The cycle service manager or hostel administration**, who can check how many cycles are at each station, see total earnings and ride history, and spot stations that need cycles moved.

## High-level features

1. Cycle count for every station, always adding up to the total of 330.
2. Ride booking with fare preview and confirmation.
3. Distance-based fare calculation using four fare slabs.
4. Rules that reject a ride when no cycle is available or the destination is full.
5. Ride history and earnings summary.
6. Report of low and crowded stations to help move cycles where they are needed.
7. Automatic saving and loading of data, with recovery if the saved file is damaged.
8. Unit tests for fares, distances, station names and ride rules.
