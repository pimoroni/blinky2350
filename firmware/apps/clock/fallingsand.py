import random


class FallingSand:
    # A class that contains all the necessaries to do a simple cellular automata-style
    # falling sand simulation. It is tailored to this application but could be made more generic.

    def __init__(self):
        self.sand_grid = self.make_2d_array(12, 39)

        # The following values are tweakable to customise how
        # fast the sand fills up, empties etc.

        # How many grains to drop on each drop.
        self.hour_grains = 3
        self.min_grains = 3
        self.sec_grains = 2

        # Drop every X intervals. In seconds, seconds and minutes respectively.
        self.sec_drop_every = 1
        self.min_drop_every = 15
        self.hour_drop_every = 15

        # Drain every X intervals. In minutes, minutes and hours respectively.
        self.sec_drain_every = 1
        self.min_drain_every = 15
        self.hour_drain_every = 6

        self.hour_to_drop = 0
        self.min_to_drop = 0
        self.sec_to_drop = 0

        self.hour_hatch = False
        self.min_hatch = False
        self.sec_hatch = False

    def make_2d_array(self, rows, cols):
        # Simple 2D array, used above to make a grid for our cellular automaton.

        grid = []
        for i in range(cols):
            row = []
            for j in range(rows):
                row.append(0)
            grid.append(row)
        return grid

    def assess_drop(self, currenttime):
        # This method takes in a time and decides which of the three drop zones
        # to drop from.

        hour = currenttime[3]
        minute = currenttime[4]
        second = currenttime[5]

        # Some of these checks are redundant, but are included
        # here for consistency and clarity.

        # First we decide whether to drop.
        # If it's time, we fill the "to_drop"
        # variables with the number of grains set.
        if second % self.sec_drop_every == 0:
            self.sec_to_drop = self.sec_grains
        if second % self.min_drop_every == 0:
            self.min_to_drop = self.min_grains
        if minute % self.hour_drop_every == 0 and second == 0:
            self.hour_to_drop = self.hour_grains

        # Then we decide to drain in the same way. The
        # "second == 0" ensures that it's only done once per minute.
        # If it's time to drain we open the hatch.
        if minute % self.sec_drain_every == 0 and second == 0:
            self.sec_hatch = True
        if minute % self.min_drain_every == 0 and second == 0:
            self.min_hatch = True
        if hour % self.hour_drain_every == 0 and second == 0:
            self.hour_hatch = True

        # Any hatch will always open at the start of a minute, so
        # after six seconds we close all hatches.
        if second == 6:
            self.sec_hatch = False
            self.min_hatch = False
            self.hour_hatch = False

    def drop_grains(self):
        # Simply checks if there are any grains left to drop, and
        # if so drops one around the specified x coordinate and removes
        # one from the list.
        # This means each grain drops on consecutive update cycles and not all together.

        if self.hour_to_drop > 0:
            self.drop_grain(8)
            self.hour_to_drop -= 1

        if self.min_to_drop > 0:
            self.drop_grain(19)
            self.min_to_drop -= 1

        if self.sec_to_drop > 0:
            self.drop_grain(30)
            self.sec_to_drop -= 1

    def drop_grain(self, centre):
        # Actually dropping the grain.
        # This will place a value in the top row of the grid
        # in a random spot between x-2 and x+2. Its value
        # will be between 90 and 218 depending on how far right
        # it's dropping, which gives us the shading.

        left = centre - 2
        offset = random.randint(0, 4)
        colour_offset = offset * 32
        colour = random.randint(90, 90 + colour_offset)
        self.sand_grid[left + offset][0] = colour

    def draw_sand(self, screen):
        # Draw the sand. Iterate through the whole grid and if the
        # value in the cell is above zero, take the value and use it
        # as a brightness to fill in the pixel at those grid coordinates.
        for i in range(len(self.sand_grid)):
            for j in range(len(self.sand_grid[0])):
                grain = self.sand_grid[i][j]
                if grain > 0:
                    screen.pen = color.rgb(grain, grain, grain)
                else:
                    screen.pen = color.rgb(0, 0, 0)
                screen.shape(shape.rectangle(i, j, 1, 1))

    def check_neighbours(self, x, y):
        # Method to check what's below, below left, and below right
        # respective to a given grid cell. Any value above zero counts as filled.

        # If it's on the bottom , all three are filled by default.
        if y >= 11:
            return 1, 1, 1

        # Otherwise check the grid in those three squares and return the result.
        # If it's at the left and right edges of the grid they always return filled.
        left, middle, right = 0, 0, 0

        if x == 0:
            left = 1
        elif self.sand_grid[x - 1][y + 1]:
            left = 1

        if x >= 38:
            right = 1
        elif self.sand_grid[x + 1][y + 1]:
            right = 1

        if self.sand_grid[x][y + 1]:
            middle = 1

        return left, middle, right

    def simulate_sand(self):
        # Actually performing the simulation.

        # We can't alter the grid we're reading it while we're trying to read from it,
        # so we make a new one for the next step of the sim and fill in cells as we go.
        # We'll swap it out for the old grid at the end.
        newgrid = self.make_2d_array(12, 39)

        # Iterate through the cells in the old grid.
        for i in range(len(self.sand_grid)):
            for j in range(len(self.sand_grid[0])):
                current = self.sand_grid[i][j]
                # If it's not got sand in we can ignore it. If it has:
                if current > 0:
                    # Check what's beliow it.
                    left, middle, right = self.check_neighbours(i, j)

                    # If it's directly above one of the hatches (in the same position as the drop zones above),
                    # check if the hatch is open. If so, make that cell in the new grid empty
                    # as it's dropped out of the bottom of the grid.
                    if j >= 11 and i <= 10 and i >= 6 and self.hour_hatch:
                        newgrid[i][j] = 0
                    elif j >= 11 and i <= 21 and i >= 17 and self.min_hatch:
                        newgrid[i][j] = 0
                    elif j >= 11 and i <= 32 and i >= 28 and self.sec_hatch:
                        newgrid[i][j] = 0

                    # Otherwise we're just going through all the possible combinations
                    # of filled left, middle and right squares below the current cell and
                    # filling in the cell's value in it's new position on the new grid.
                    # Possible choices - stay where it is, fall straight down, fall down and left or fall down and right.
                    elif not left and not middle and not right:
                        newgrid[i][j + 1] = current
                    elif not left and not middle and right:
                        newgrid[i][j + 1] = current
                    elif not left and middle and not right:
                        # This one's a special one. If the cell directly below is full
                        # but both side ones are empty, then pick a side to fall to at random.
                        choice = random.randint(0, 1)
                        if choice:
                            newgrid[i + 1][j + 1] = current
                        else:
                            newgrid[i - 1][j + 1] = current
                    elif not left and middle and right:
                        newgrid[i - 1][j + 1] = current
                    elif left and not middle and not right:
                        newgrid[i][j + 1] = current
                    elif left and not middle and right:
                        newgrid[i][j + 1] = current
                    elif left and middle and not right:
                        newgrid[i + 1][j + 1] = current
                    elif left and middle and right:
                        newgrid[i][j] = current

        # Finally, swap out the old grid for the new one to advance the simulation one step.
        self.sand_grid = newgrid
