"""Patterns of winning spaces."""
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
