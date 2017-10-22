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


class Segment(namedtuple('Segment', 'coords direction length next_segment')):

    def __str__(self):
        if self.next_segment:
            return ' '.join((DIRECTIONS[self.direction], str(self.length), '>', str(self.next_segment)))
        return ' '.join((DIRECTIONS[self.direction], str(self.length)))


def get_end_coords(coords, direction, length):
    """
    Returns the coordinates of the point from `coords` in `direction` at `length`
    """
    operator, axis = direction
    return Coords(
        operator(coords.x, length) if axis.x else coords.x,
        operator(coords.y, length) if axis.y else coords.y,
        operator(coords.z, length) if axis.z else coords.z,
    )


def are_coords_invalid(coords):
    """
    Returns whether coords is a point outside the cube
    """
    return any(getattr(coords, c) < 0 or getattr(coords, c) >= SIZE for c in ('x', 'y', 'z'))


def crosses_occupied_block(coords, direction, length, cube):
    """
    Returns whether `segment` crosses a block in `cube` that is already occupied.
    """
    operator, axis = direction
    return sum(
        cube[operator(coords.x, axis.x * i)]
            [operator(coords.y, axis.y * i)]
            [operator(coords.z, axis.z * i)]
        for i in range(length)
    )


def get_cube_state(coords, direction, length, initial_cube):
    """
    Returns the cube state after `segment` is added to `initial_state`
    """
    segment_cube = [[[0 for z in range(SIZE)] for y in range(SIZE)] for x in range(SIZE)]
    operator, axis = direction
    for i in range(length):
        x = operator(coords.x, i) if axis.x else coords.x
        y = operator(coords.y, i) if axis.y else coords.y
        z = operator(coords.z, i) if axis.z else coords.z
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


def next_directions(direction):
    """
    The next segment can't go in the same direction as the given
    segment, and it can't go in the opposite direction.
    """
    return (d for d in DIRECTIONS if direction[1] != d[1])


def get_valid_segment(coords, direction, length, initial_cube, segment_lengths):
    """
    Determine whether the given segment is a position by recursively
    checking the validity of possible next segments.
    """
    end_coords = get_end_coords(coords, direction, length - 1)
    if are_coords_invalid(end_coords):
        return None
    if crosses_occupied_block(coords, direction, length, initial_cube):
        return None
    if is_last_segment(segment_lengths):
        return Segment(coords, direction, length, None)

    # Recurse
    cube = get_cube_state(coords, direction, length, initial_cube)
    next_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    for next_direction in next_directions(direction):
        next_coords = get_end_coords(end_coords, next_direction, 1)
        if are_coords_invalid(next_coords):
            continue
        next_segment = get_valid_segment(next_coords, next_direction, next_length, cube, next_segment_lengths)
        if next_segment:
            return Segment(coords, direction, length, next_segment)
    return None


def solve(segment_lengths):
    """
    Iterate all points in the cube, and return the first valid path of
    segments found.
    """
    cube = (((0,) * SIZE,) * SIZE,) * SIZE
    next_length = segment_lengths[0]
    next_segment_lengths = segment_lengths[1:]
    for x in range(SIZE):
        for y in range(SIZE):
            for z in range(SIZE):
                coords = Coords(x, y, z)
                for direction in DIRECTIONS:
                    segment = get_valid_segment(coords, direction, next_length, cube, next_segment_lengths)
                    if segment:
                        return segment
    return 'No solution'


if __name__ == '__main__':
    print(solve(SEGMENT_LENGTHS))
