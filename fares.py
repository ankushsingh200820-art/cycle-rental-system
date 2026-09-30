# fares.py
# The fare rules of the cycle system, kept in their own file so that
# changing the price later does not touch any other code.

# Each slab is (up to this many metres, fare in rupees).
# The loop in calculate_fare goes through them in order and returns
# at the first slab that covers the distance.
FARE_SLABS = [
    (300, 5),
    (600, 10),
    (1000, 15),
]

# If the distance is more than the last slab (1000 m), this fare is used.
FARE_ABOVE_LAST_SLAB = 20


def calculate_fare(distance):
    """Return the fare in rupees for a distance in metres.

    0-300 m   -> Rs.5
    301-600 m -> Rs.10
    601-1000 m -> Rs.15
    above 1000 m -> Rs.20
    """
    for limit, fare in FARE_SLABS:
        if distance <= limit:
            return fare

    # The distance was bigger than every limit in the slabs.
    return FARE_ABOVE_LAST_SLAB
