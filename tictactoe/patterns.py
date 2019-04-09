"""Patterns of winning spaces."""

# I think hard-coding board positions like this is good in some ways and bad in others.
# For the stated problem, this is much easier to read and understand than a more complicated
# search-based AI. It's also probably more CPU efficient, although that's not a big concern
# for this :)
#
# If we were building this as a maybe-slightly-overengineered Full Production System,
# hard-coding these things might bite us later if requirements change. For example,
# a new req comes in from the sales department that we have to support 4x4 tic tac toe.
#
# I'm *not* saying I would definitely change to something more general here. In fact, Maggie
# can attest that I'm often advising people to write code that deals with the specific data that
# they have in front of them, rather than building some more complicated general solution.
# But, that's the kind of tradeoff we want to think about when building business software: what's
# likely to change? What can we do in our code to be ready for that change when it comes? Not
# anticipate the specific change, but build things in a way that is flexible when change
# inevitably comes.
#
# I'm veering off into the weeds a bit, so we can pair up on some specific refactoring if you'd like!

winning_patterns = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]

corners = [0, 2, 6, 8]
middles = [1, 3, 5, 7]


def make_partial_patterns(winning_patterns):
    """Create a map of partial patterns to the spaces that complete the patterns.

    >>> partial_patterns[frozenset((0, 2))] == 1
    """
    partial_patterns = {}
    for s1, s2, s3 in winning_patterns:
        partial_patterns[frozenset((s1, s2))] = s3
        partial_patterns[frozenset((s1, s3))] = s2
        partial_patterns[frozenset((s2, s3))] = s1
    return partial_patterns


def make_outer_patterns(winning_patterns):
    """Create a list of outer patterns that don't include the center square."""
    return [pattern for pattern in winning_patterns if 4 not in pattern]


def make_diagonal_patterns(winning_patterns, corners):
    diagonal_patterns = []
    for s1, s2, s3 in winning_patterns:
        if s2 == 4 and all(s in corners for s in [s1, s3]):
            diagonal_patterns.append((s1, s2, s3))
    return diagonal_patterns


partial_patterns = make_partial_patterns(winning_patterns)
outer_patterns = make_outer_patterns(winning_patterns)
diagonal_patterns = make_diagonal_patterns(winning_patterns, corners)
