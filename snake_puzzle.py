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
SIZE = round(sum(SEGMENT_LENGTHS) ** (1.0 / 3))  # Assumes a cube
Coords = namedtuple('Coords', 'x y z')
DIRECTIONS = {
    # (operator, axis): English name
    # axis will determine which axis is being traversed
    # operator will increment or decrement a coordinate
    (int.__add__, Coords(True, False, False)): 'right',
    (int.__sub__, Coords(True, False, False)): 'left',
    (int.__add__, Coords(False, True, False)): 'up',
    (int.__sub__, Coords(False, True, False)): 'down',
    (int.__add__, Coords(False, False, True)): 'forwards',
    (int.__sub__, Coords(False, False, True)): 'backwards'
}


class Segment(object):
    def __init__(self, coords, length, direction):
        self.coords = coords
        self.length = length
        self.direction = direction
        self.next_segment = None

    def __str__(self):
        if self.next_segment:
            return ' '.join((DIRECTIONS[self.direction], str(self.length), '>', str(self.next_segment)))
        return ' '.join((DIRECTIONS[self.direction], str(self.length)))


def get_coords(coords, direction, distance):
    """
    Returns the coordinates of the point from `coords` in `direction` at `distance`
    """
    operator, axis = direction
    return Coords(
        operator(coords.x, distance) if axis.x else coords.x,
        operator(coords.y, distance) if axis.y else coords.y,
        operator(coords.z, distance) if axis.z else coords.z,
    )


def are_coords_invalid(coords):
    """
    Returns whether coords is a point outside the cube
    """
    return any(getattr(coords, c) < 0 or getattr(coords, c) >= SIZE for c in ('x', 'y', 'z'))


def crosses_occupied_block(cube, segment):
    """
    Returns whether `segment` crosses a block in `cube` that is already occupied.
    """
    operator, axis = segment.direction
    return sum(
        cube[operator(segment.coords.x, axis.x * i)]
            [operator(segment.coords.y, axis.y * i)]
            [operator(segment.coords.z, axis.z * i)]
        for i in range(segment.length)
    )


def get_cube_state(initial_cube, segment):
    """
    Returns the cube state after `segment` is added to `initial_state`
    """
    segment_cube = [[[0 for z in range(SIZE)] for y in range(SIZE)] for x in range(SIZE)]
    operator, axis = segment.direction
    for i in range(segment.length):
        x = operator(segment.coords.x, i) if axis.x else segment.coords.x
        y = operator(segment.coords.y, i) if axis.y else segment.coords.y
        z = operator(segment.coords.z, i) if axis.z else segment.coords.z
        segment_cube[x][y][z] = 1

    return tuple(
        tuple(
            tuple(
                initial_cube[x][y][z] + segment_cube[x][y][z]
                for z in range(SIZE)
            ) for y in range(SIZE)
        ) for x in range(SIZE)
    )


def is_last_segment(segment_lengths):
    return not segment_lengths


def next_directions(segment):
    """
    The next segment can't go in the same direction as the given
    segment, and it can't go in the opposite direction.
    """
    return (d for d in DIRECTIONS if segment.direction[1] != d[1])


def is_valid(initial_cube, segment, segment_lengths):
    """
    Determine whether the given segment is a position by recursively
    checking the validity of possible next segments.
    """
    end_coords = get_coords(segment.coords, segment.direction, segment.length - 1)
    if are_coords_invalid(end_coords):
        return False
    if crosses_occupied_block(initial_cube, segment):
        return False
    if is_last_segment(segment_lengths):
        return True
    # Recurse
    segment_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    cube = get_cube_state(initial_cube, segment)
    for direction in next_directions(segment):
        start_coords = get_coords(end_coords, direction, 1)
        if are_coords_invalid(start_coords):
            continue
        segment.next_segment = Segment(start_coords, segment_length, direction)

        if is_valid(cube, segment.next_segment, next_segment_lengths):
            return True
    return False


def solve(segment_lengths):
    """
    Iterate all points in the cube, and return the first valid path of
    segments found.
    """
    cube = (((0,) * SIZE,) * SIZE,) * SIZE
    segment_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):
                coords = Coords(x, y, z)
                for direction in DIRECTIONS:
                    segment = Segment(coords, segment_length, direction)
                    if is_valid(cube, segment, next_segment_lengths):
                        return segment
    return 'No solution'


if __name__ == '__main__':
    print(solve(SEGMENT_LENGTHS))
