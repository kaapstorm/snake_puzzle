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
DIRECTIONS = {
    '+x': 'right',
    '-x': 'left',
    '+y': 'up',
    '-y': 'down',
    '+z': 'forwards',
    '-z': 'backwards'
}
Coords = namedtuple('Coords', 'x y z')


def get_coords(coords, direction, distance):
    """
    Returns the coordinates of the point from `coords` in `direction` at `distance`
    """
    if direction == '+x':
        return Coords(coords.x + distance, coords.y, coords.z)
    if direction == '-x':
        return Coords(coords.x - distance, coords.y, coords.z)
    if direction == '+y':
        return Coords(coords.x, coords.y + distance, coords.z)
    if direction == '-y':
        return Coords(coords.x, coords.y - distance, coords.z)
    if direction == '+z':
        return Coords(coords.x, coords.y, coords.z + distance)
    if direction == '-z':
        return Coords(coords.x, coords.y, coords.z - distance)


def are_coords_invalid(coords):
    """
    Returns whether coords is a point outside the cube
    """
    return any(getattr(coords, c) < 0 or getattr(coords, c) >= SIZE for c in ('x', 'y', 'z'))


def crosses_occupied_block(cube, segment):
    """
    Returns whether `segment` crosses a block in `cube` that is already occupied.
    """
    if segment.direction == '+x':
        return sum(cube[segment.coords.x + i][segment.coords.y][segment.coords.z]
                   for i in range(segment.length))
    if segment.direction == '-x':
        return sum(cube[segment.coords.x - i][segment.coords.y][segment.coords.z]
                   for i in range(segment.length))
    if segment.direction == '+y':
        return sum(cube[segment.coords.x][segment.coords.y + i][segment.coords.z]
                   for i in range(segment.length))
    if segment.direction == '-y':
        return sum(cube[segment.coords.x][segment.coords.y - i][segment.coords.z]
                   for i in range(segment.length))
    if segment.direction == '+z':
        return sum(cube[segment.coords.x][segment.coords.y][segment.coords.z + i]
                   for i in range(segment.length))
    if segment.direction == '-z':
        return sum(cube[segment.coords.x][segment.coords.y][segment.coords.z - i]
                   for i in range(segment.length))


def get_cube_state(initial_cube, segment):
    """
    Returns the cube state after `segment` is added to `initial_state`
    """
    segment_cube = [[[0 for z in range(SIZE)] for y in range(SIZE)] for x in range(SIZE)]
    for i in range(segment.length):
        if segment.direction == '+x':
            segment_cube[segment.coords.x + i][segment.coords.y][segment.coords.z] = 1
        if segment.direction == '-x':
            segment_cube[segment.coords.x - i][segment.coords.y][segment.coords.z] = 1
        if segment.direction == '+y':
            segment_cube[segment.coords.x][segment.coords.y + i][segment.coords.z] = 1
        if segment.direction == '-y':
            segment_cube[segment.coords.x][segment.coords.y - i][segment.coords.z] = 1
        if segment.direction == '+z':
            segment_cube[segment.coords.x][segment.coords.y][segment.coords.z + i] = 1
        if segment.direction == '-z':
            segment_cube[segment.coords.x][segment.coords.y][segment.coords.z - i] = 1

    return tuple(
        tuple(
            tuple(
                initial_cube[x][y][z] + segment_cube[x][y][z]
                for z in range(SIZE)
            ) for y in range(SIZE)
        ) for x in range(SIZE)
    )


class Segment(object):
    def __init__(self, coords, length, direction, initial_cube, segment_lengths):
        self.coords = coords
        self.length = length
        self.direction = direction
        self.initial_cube = initial_cube
        self.segment_lengths = segment_lengths
        self.next_segment = None

    def _is_last_segment(self):
        return not self.segment_lengths

    def _possible_directions_gen(self):
        """
        The next segment can't go in the same direction as this 
        segment, and it can't go in the opposite direction.
        """
        return (d for d in DIRECTIONS if self.direction[1] not in d)

    def is_valid(self):
        """
        Determine whether this a valid segment position by recursively
        checking the validity of possible next segments.
        """
        end_coords = get_coords(self.coords, self.direction, self.length - 1)
        if are_coords_invalid(end_coords):
            return False
        if crosses_occupied_block(self.initial_cube, self):
            return False
        if self._is_last_segment():
            return True
        # Recurse
        segment_length = self.segment_lengths[0]
        next_segment_lengths = self.segment_lengths[1:]
        cube = get_cube_state(self.initial_cube, self)
        for direction in self._possible_directions_gen():
            start_coords = get_coords(end_coords, direction, 1)
            if are_coords_invalid(start_coords):
                continue
            self.next_segment = Segment(start_coords, segment_length, direction, cube, next_segment_lengths)

            if self.next_segment.is_valid():
                return True
        return False

    def __str__(self):
        if self.next_segment:
            return ' '.join((DIRECTIONS[self.direction], str(self.length), '>', str(self.next_segment)))
        return ' '.join((DIRECTIONS[self.direction], str(self.length)))


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
                    segment = Segment(coords, segment_length, direction, cube, next_segment_lengths)
                    if segment.is_valid():
                        return segment
    return 'No solution'


if __name__ == '__main__':
    print(solve(SEGMENT_LENGTHS))
