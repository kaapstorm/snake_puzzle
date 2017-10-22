#!/usr/bin/env python3
"""
Solves the snake puzzle by depth-wise search of a tree of possible
segments.
"""
from collections import namedtuple

SEGMENT_LENGTHS = (
    3, 3, 3, 3, 1, 3, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 3, 2, 2, 1, 3, 1,
    2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 3, 1, 3,
)


Coords = namedtuple('Coords', 'x y z')
DIRECTIONS = {
    # (operator, axes): English name
    # axes will determine which axis is being traversed
    # operator will increment or decrement a coordinate
    (int.__add__, Coords(True, False, False)): 'right',
    (int.__sub__, Coords(True, False, False)): 'left',
    (int.__add__, Coords(False, True, False)): 'up',
    (int.__sub__, Coords(False, True, False)): 'down',
    (int.__add__, Coords(False, False, True)): 'forwards',
    (int.__sub__, Coords(False, False, True)): 'backwards'
}


class Segment(namedtuple('Segment', 'coords direction length next_segment')):

    def __str__(self):
        if self.next_segment:
            return ' '.join((DIRECTIONS[self.direction], str(self.length), '>', str(self.next_segment)))
        return ' '.join((DIRECTIONS[self.direction], str(self.length)))


def get_end_coords(coords, direction, length):
    """
    Returns the coordinates of the point from `coords` in `direction`
    at `length`.
    """
    operator, axes = direction
    return Coords(
        operator(coords.x, length) if axes.x else coords.x,
        operator(coords.y, length) if axes.y else coords.y,
        operator(coords.z, length) if axes.z else coords.z,
    )


def are_coords_valid(coords, size):
    """
    Returns whether `coords` describe a point outside a cube of the
    given `size`.
    """
    return all(0 <= getattr(coords, axis) < size for axis in ('x', 'y', 'z'))


def crosses_occupied_block(coords, direction, length, cube):
    """
    Returns whether the segment described by `coords`, `direction` and
    `length` crosses a block in `cube` that is already occupied.

    >>> coords = Coords(0, 0, 0)
    >>> direction = next(k for k, v in DIRECTIONS.items() if v == 'right')
    >>> length = 1
    >>> cube = (((1, 1), (1, 1)), ((1, 1), (1, 1)))
    >>> bool(crosses_occupied_block(coords, direction, length, cube))
    True
    >>> cube = (((0, 0), (0, 0)), ((0, 0), (0, 0)))
    >>> bool(crosses_occupied_block(coords, direction, length, cube))
    False

    """
    operator, axes = direction
    return sum(
        cube[operator(coords.x, axes.x * i)]
            [operator(coords.y, axes.y * i)]
            [operator(coords.z, axes.z * i)]
        for i in range(length)
    )


def get_cube_state(coords, direction, length, initial_cube):
    """
    Returns the cube state after the segment described by `coords`,
    `direction` and `length` is added to `initial_cube`.

    >>> coords = Coords(0, 0, 0)
    >>> direction = next(k for k, v in DIRECTIONS.items() if v == 'right')
    >>> length = 2
    >>> initial_cube = (((0, 0), (0, 0)), ((0, 0), (0, 0)))
    >>> get_cube_state(coords, direction, length, initial_cube)
    (((1, 0), (0, 0)), ((1, 0), (0, 0)))

    """
    size = len(initial_cube)
    segment_cube = [[[0 for z in range(size)] for y in range(size)] for x in range(size)]
    operator, axes = direction
    for i in range(length):
        x = operator(coords.x, i) if axes.x else coords.x
        y = operator(coords.y, i) if axes.y else coords.y
        z = operator(coords.z, i) if axes.z else coords.z
        segment_cube[x][y][z] = 1

    return tuple(
        tuple(
            tuple(
                initial_cube[x][y][z] + segment_cube[x][y][z]
                for z in range(size)
            ) for y in range(size)
        ) for x in range(size)
    )


def next_directions(direction):
    """
    The next segment can't go in the same direction as the given
    direction, and it can't go in the opposite direction.

    >>> direction = next(k for k, v in DIRECTIONS.items() if v == 'right')
    >>> directions = [DIRECTIONS[d] for d in next_directions(direction)]
    >>> sorted(directions)
    ['backwards', 'down', 'forwards', 'up']

    """
    return (d for d in DIRECTIONS if direction[1] != d[1])


def get_valid_segment(coords, direction, length, initial_cube, segment_lengths):
    """
    Determine whether the given segment is a position by recursively
    checking the validity of possible next segments.
    """
    size = len(initial_cube)
    if not are_coords_valid(coords, size):
        return None
    end_coords = get_end_coords(coords, direction, length - 1)
    if not are_coords_valid(end_coords, size):
        return None
    if crosses_occupied_block(coords, direction, length, initial_cube):
        return None
    if not segment_lengths:
        return Segment(coords, direction, length, None)

    # Recurse
    cube = get_cube_state(coords, direction, length, initial_cube)
    next_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    for next_direction in next_directions(direction):
        next_coords = get_end_coords(end_coords, next_direction, 1)
        next_segment = get_valid_segment(next_coords, next_direction, next_length, cube, next_segment_lengths)
        if next_segment:
            return Segment(coords, direction, length, next_segment)
    return None


def solve(segment_lengths):
    """
    Iterate all points in the cube, and return the first valid path of
    segments found.

    >>> segment_lengths = (2, 1, 1, 1, 1, 1, 1)
    >>> bool(solve(segment_lengths))
    True
    >>> segment_lengths = (2, 2, 1, 1, 1, 1)
    >>> bool(solve(segment_lengths))
    False

    """
    size = int(round(sum(segment_lengths) ** (1.0 / 3)))  # Assumes a cube
    cube = (((0,) * size,) * size,) * size
    next_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    for x in range(size):
        for y in range(size):
            for z in range(size):
                coords = Coords(x, y, z)
                for direction in DIRECTIONS:
                    segment = get_valid_segment(coords, direction, next_length, cube, next_segment_lengths)
                    if segment:
                        return segment
    return None


if __name__ == '__main__':
    print(solve(SEGMENT_LENGTHS) or 'No solution')
