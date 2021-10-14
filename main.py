"""
Example Tetris project by Bennett Kaufmann
Example project using pygame, but including some more advanced concepts.
Requires numpy to run.

TODO
  Change input handling to prevent repeat rotations.
  Change input handling to move pieces on hold, even after pressing another key.
  Make blocks rotate correctly.
  Handle losing.
  Display next and hold pieces.
  Add counter-clockwise rotation and flips.
  Add leeway to move block before placing.
  Change piece generation to not be completely random.
  Clean up piece handling.
"""

import random
import sys

import pygame
import numpy as np

# Initialize pygame
clock = pygame.time.Clock()
pygame.display.init()

dispInfo = pygame.display.Info()
sizex, sizey = dispInfo.current_w, dispInfo.current_h

display = pygame.display.set_mode((sizex, sizey), pygame.FULLSCREEN)

# Input settings
pygame.key.set_repeat(100, 40)

# Define shape colors and shapes
colors = {
    1: (0, 255, 255),
    2: (255, 0, 0),
    3: (200, 0, 255),
    4: (255, 255, 0),
    5: (255, 128, 0),
    6: (0, 255, 0),
    7: (0, 0, 255), 255: (100, 100, 100)
}

shapes = {
    1: [np.array((-1, 0)), np.array((0, 0)), np.array((1, 0)), np.array((2, 0))],
    2: [np.array((-1, 0)), np.array((0, 0)), np.array((0, 1)), np.array((1, 1))],
    3: [np.array((-1, 0)), np.array((0, 0)), np.array((0, 1)), np.array((1, 0))],
    4: [np.array((0, 0)), np.array((1, 0)), np.array((0, 1)), np.array((1, 1))],
    5: [np.array((0, 1)), np.array((0, 0)), np.array((1, 0)),np.array((2, 0))],
    6: [np.array((-1, 1)), np.array((0, 1)),np.array((0, 0)),np.array((1, 0))],
    7: [np.array((-1, 0)), np.array((0, 0)),np.array((1, 0)),np.array((1, 1))]
}

background = pygame.image.load('Tetback.png')

# Set size based off of screen size
SIZE = 40 // (1920/sizex)

class Board:
    """
    Basic board class holding current state of blocks and drawing blocks to screen.
    """
    def __init__(self):
        self.piece = None
        self.grid = np.zeros((10, 20), np.uint8)
        self.held = None

    def render(self):
        """
        Method that renders the current board state to the display, with all placed pieces.
        """
        for x in range(10):
            for y in range(20):
                col = self.grid[x, y]

                if col:
                    # Draw square at potion based off of screen size
                    pos = pygame.Rect((250 // (1920/sizex)) + SIZE * x, (100 // (1080/sizey)) + SIZE * y, SIZE, SIZE)
                    pygame.draw.rect(display, colors[col], pos)

class Piece:
    """
    Piece class containing methods to handle unplaced piece interaction.
    """
    def __init__(self, shape=None):
        if shape:
            self.shape = shape

        else:
            self.shape = random.randint(1, len(shapes))

        self.pos = [5, 3]
        self.rot = 0

    def move(self):
        """
        Method that moves a piece down.
        """
        self.pos[1] += 1

    def rotate(self):
        """
        Method that rotates a piece clockwise once.
        """
        self.rot = (self.rot + 1) % 4

    def collide(self, grid, exp):
        """
        Method that detects collision with the board from a certain offset.
        """
        for off in shapes[self.shape]:
            if (self.rot % 2):
                off = np.flip(off) * (-1, 1)

            if self.rot > 1:
                off = np.negative(off)

            if (self.pos[1] + off[1] + exp[1] >= 20
               or self.pos[0] + off[0] + exp[0] not in range(10)
               or grid[self.pos[0] + off[0] + exp[0], self.pos[1] + off[1] + exp[1]] not in {0, 255}
               ):
                return True

# Create board
b = Board()

i = 0
placed = 1

# Game loop
while True:
    if not(b.piece):
        # Clear lines that are full
        for row in range(b.grid.shape[1]):
            if np.all(b.grid[:,row]):
                b.grid[:,1:row + 1] = b.grid[:,:row]

        # Create new piece
        b.piece = Piece()

        # Collided on piece spawn (dead)
        if b.piece.collide(b.grid, (0, 0)):
            print('Died')
            break

##    else:
##        if b.piece.collide(b.grid, (0, 1)):
##            b.piece = piece()

    hold = False
    i += 1
    placed -= 1

    display.blit(background, [0, 0])

##    for off in shapes[b.piece.shape]:
##        b.grid[tuple(np.array(b.piece.pos) + off)] = 0

    # Gravity (every 20 frames)
    if not(i % 20) and b.piece:
        b.piece.move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)

        # Handle input
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and b.piece.pos[0] > 0:
                if not(b.piece.collide(b.grid, (-1, 0))):
                    b.piece.pos[0] -= 1

            elif event.key == pygame.K_RIGHT and b.piece.pos[0] < 9:
                if not(b.piece.collide(b.grid, (1, 0))):
                    b.piece.pos[0] += 1

            elif event.key == pygame.K_DOWN:
                if not(b.piece.collide(b.grid, (0, 1))):
                    b.piece.move()

            elif event.key == pygame.K_UP:
                b.piece.rotate()

                # Unrotate if rotation makes piece collide
                if b.piece.collide(b.grid, (0, 0)):
                    for x in range(3):
                        b.piece.rotate()

            # Place piece if long enough since last placement
            elif event.key == pygame.K_SPACE and placed < 0:
                while not(b.piece.collide(b.grid, (0, 1))):
                    b.piece.move()

            elif event.key == pygame.K_c:
                hold = True

    # Set current piece on board (FIXME: Don't place, and instead render separately to simplify collision)
    for off in shapes[b.piece.shape]:
        if b.piece.rot % 2:
            off = np.flip(off) * (-1, 1)

        if b.piece.rot > 1:
            off = np.negative(off)

        b.grid[tuple(np.array(b.piece.pos) + off)] = b.piece.shape

    # Render board
    b.render()

    b.grid = np.where(b.grid == 255, 0, b.grid)

    # Remove current piece from board
    for off in shapes[b.piece.shape]:
        if b.piece.rot % 2:
            off = np.flip(off) * (-1, 1)

        if b.piece.rot > 1:
            off = np.negative(off)

        b.grid[tuple(np.array(b.piece.pos) + off)] = 0

    # Find how far piece can currently fall (for ghost block)
    blocks = 0

    while not(b.piece.collide(b.grid, (0, blocks))):
        blocks += 1

    # Put ghost piece on board (shouldn't need to)
    for off in shapes[b.piece.shape]:
        if b.piece.rot % 2:
            off = np.flip(off) * (-1, 1)

        if b.piece.rot > 1:
            off = np.negative(off)

        if b.grid[tuple(np.array(b.piece.pos) + off + (0, blocks - 1))] == 0:
            b.grid[tuple(np.array(b.piece.pos) + off + (0, blocks - 1))] = 255

##    for off in shapes[b.piece.shape]:
##        if b.piece.rot % 2:
##            off = np.flip(off) * (-1, 1)
##
##        if b.piece.rot > 1:
##            off = np.negative(off)

    # Place piece if about to hit groud
    if b.piece.collide(b.grid, (0, 1)):
        for off in shapes[b.piece.shape]:
            if b.piece.rot % 2:
                off = np.flip(off) * (-1, 1)

            if b.piece.rot > 1:
                off = np.negative(off)

            b.grid[tuple(np.array(b.piece.pos) + off)] = b.piece.shape

        b.piece = None

        placed = 5
##        break

    # Remove current piece from board
    if b.piece:
        for off in shapes[b.piece.shape]:
            if b.piece.rot % 2:
                off = np.flip(off) * (-1, 1)

            if b.piece.rot > 1:
                off = np.negative(off)

            b.grid[tuple(np.array(b.piece.pos) + off)] = 0

    # Replace piece if hold is input
    if hold:
        if b.held:
            n = b.piece.shape
            b.piece = Piece(b.held)
            b.held = n

        else:
            b.held = b.piece.shape
            b.piece = Piece()

    # Refresh display
    pygame.display.update()
    clock.tick(60)
