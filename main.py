"""
Example Tetris project by Bennett Kaufmann
Example project using pygame, but including some more advanced concepts.
Requires numpy to run.

TODO
  Change input handling to not allow multiple directions at once.
  Possibly change input handling to repeat by milliseconds instead of frames.
  Handle losing.
  Label next and hold pieces.
"""

import random
import sys

import pygame
import numpy as np

# Initialize pygame
clock = pygame.time.Clock()
pygame.display.init()

# Set display size from screen size
dispInfo = pygame.display.Info()
sizex, sizey = dispInfo.current_w, dispInfo.current_h

display = pygame.display.set_mode((sizex, sizey))

# Input settings
delays = [8, 3]
holdNums = [delays[0]] * 3

# Define shape colors and shapes
colors = {
    1: (0, 255, 255),
    2: (255, 0, 0),
    3: (200, 0, 255),
    4: (255, 255, 0),
    5: (255, 128, 0),
    6: (0, 255, 0),
    7: (0, 0, 255)
}

shapes = {
    1: np.transpose(np.array([
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])),
    2: np.transpose(np.array([
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0]
    ])),
    3: np.transpose(np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0]
    ])),
    4: np.transpose(np.array([
        [0, 1, 1, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 0]
    ])),
    5: np.transpose(np.array([
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0]
    ])),
    6: np.transpose(np.array([
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0]
    ])),
    7: np.transpose(np.array([
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0]
    ])),
}

kickTable = {
    (0, 1): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (1, 0): [(1, 0), (1, 1), (0, -2), (1, -2)],
    (1, 2): [(1, 0), (1, 1), (0, -2), (1, -2)],
    (2, 1): [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
    (2, 3): [(1, 0), (1, -1), (0, 2), (1, 2)],
    (3, 2): [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
    (3, 0): [(-1, 0), (-1, -1), (0, 2), (-1, -2)],
    (0, 3): [(1, 0), (1, -1), (0, 2), (1, 2)]
}
lkickTable = {
    (0, 1): [(-2, 0), (1, 0), (-2, 1), (1, -2)],
    (1, 0): [(2, 0), (-1, 0), (2, -1), (-1, 2)],
    (1, 2): [(-1, 0), (2, 0), (-1, -2), (2, 1)],
    (2, 1): [(1, 0), (-2, 0), (1, 2), (-2, -1)],
    (2, 3): [(2, 0), (-1, 0), (2, -1), (-1, 2)],
    (3, 2): [(-2, 0), (1, 0), (-2, 1), (1, -2)],
    (3, 0): [(1, 0), (-2, 0), (1, 2), (-2, -1)],
    (0, 3): [(-1, 0), (2, 0), (-1, -2), (2, 1)]
}

background = pygame.image.load('Tetback.png')

# Set size based off of screen size
SIZE = 40 // (1920/sizex)
background = pygame.transform.scale(background, (SIZE * 48, SIZE * 27))

class Board:
    """
    Basic board class holding current state of blocks and drawing blocks to screen.
    """
    def __init__(self):
        self.piece = None
        self.grid = np.zeros((10, 20), np.uint8)
        self.held = None

        self.bag = list(shapes.keys())
        random.shuffle(self.bag)

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

        for i in range(4):
            shape = zip(*np.where(shapes[self.bag[i]]))

            for off in shape:
                pos = pygame.Rect(900 // (1920/sizex) + SIZE * off[0], (300 + 120 * i) // (1080/sizey) + SIZE * off[1], SIZE, SIZE)
                pygame.draw.rect(display, colors[self.bag[i]], pos)

        if self.held:
            for off in zip(*np.where(shapes[self.held])):
                pos = pygame.Rect(84 // (1920/sizex) + SIZE * off[0], (200) // (1080/sizey) + SIZE * off[1], SIZE, SIZE)
                pygame.draw.rect(display, colors[self.held], pos)

    def getPiece(self):
        """
        Method that returns the next piece from the random bag.
        """
        if len(self.bag) < 7:
            add = list(shapes.keys())
            random.shuffle(add)
            self.bag += add

        return self.bag.pop(0)

class Piece:
    """
    Piece class containing methods to handle unplaced piece interaction.
    """
    def __init__(self, board, shape=None):
        self.board = board

        if shape:
            self.col = shape

        else:
            self.col = b.getPiece()

        self.offs = tuple(zip(*np.where(shapes[self.col])))
        self.rot = 0

        self.pos = [4, 3]

    def move(self):
        """
        Method that moves a piece down.
        """
        self.pos[1] += 1

    def rotate(self, num=1):
        """
        Method that rotates a piece clockwise once.
        """
        # Do two rotations for 180 flips (so kicks work)
        if num == 2:
            self.rotate(1)
            num -= 1

        srot = self.rot
        self.rot = (self.rot + num) % 4

        if self.col != 4:
            self.offs = tuple(zip(*np.where(np.rot90(shapes[self.col], self.rot))))

            if self.col == 1:
                kicks = [(0, 0), *lkickTable[srot, self.rot]]

            else:
                kicks = [(0, 0), *kickTable[srot, self.rot]]

            for kick in kicks:
                if self.collide(self.board.grid, kick):
                    continue

                self.pos[0] += kick[0]
                self.pos[1] += kick[1]
                return

            self.rot = (self.rot - num) % 4
            self.offs = tuple(zip(*np.where(np.rot90(shapes[self.col], self.rot))))

    def collide(self, grid, exp):
        """
        Method that detects collision with the board from a certain offset.
        """
        for off in self.offs:
            if (self.pos[1] + off[1] + exp[1] >= 20
               or self.pos[0] + off[0] + exp[0] not in range(10)
               or grid[self.pos[0] + off[0] + exp[0], self.pos[1] + off[1] + exp[1]] != 0
               ):
                return True

        return False

    def render(self):
        """
        Method that renders the current piece to the display.
        """
        for off in self.offs:
            pos = pygame.Rect((250 // (1920/sizex)) + SIZE * (self.pos[0] + off[0]), (100 // (1080/sizey)) + SIZE * (self.pos[1] + off[1]), SIZE, SIZE)
            pygame.draw.rect(display, colors[self.col], pos)

    def ghostrender(self):
        """
        Render the ghost block where the current block will collide at.
        """
        # Find how far piece can currently fall (for ghost block)
        blocks = 0

        while not(b.piece.collide(b.grid, (0, blocks + 1))):
            blocks += 1

        # Display ghost piece
        for off in self.offs:
            pos = pygame.Rect((250 // (1920/sizex)) + SIZE * (self.pos[0] + off[0]), (100 // (1080/sizey)) + SIZE * (self.pos[1] + off[1] + blocks), SIZE, SIZE)
            pygame.draw.rect(display, (100, 100, 100), pos)

# Create board
b = Board()

i = 0
placed = 1
lock = 0
totlock = 0
locks = [20, 120]
lines = 0
lasthold = False

# Game loop
while True:
    if not(b.piece):
        # Clear lines that are full
        for row in range(b.grid.shape[1]):
            if np.all(b.grid[:,row]):
                b.grid[:,1:row + 1] = b.grid[:,:row]
                lines += 1

        # Create new piece
        b.piece = Piece(b)

        # Collided on piece spawn (dead)
        if b.piece.collide(b.grid, (0, 0)):
            print('Died')
            break

    # Initialize frame state
    hold = False
    i += 1
    placed -= 1

    display.blit(background, [2, 1])

    # Gravity
    if not(i % (16 - min(15, lines // 4))) and b.piece and not(b.piece.collide(b.grid, (0, 1))):
        b.piece.move()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(1)

        # Handle single inputs
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                b.piece.rotate(1)
                lock = 0

            elif event.key == pygame.K_a:
                b.piece.rotate(2)
                lock = 0

            elif event.key == pygame.K_z:
                b.piece.rotate(-1)
                lock = 0

            # Place piece if pressed and long enough since last placement
            elif event.key == pygame.K_SPACE and placed < 0:
                while not(b.piece.collide(b.grid, (0, 1))):
                    b.piece.move()

                totlock = locks[1]

            elif event.key == pygame.K_c:
                hold = True

    # Handle repeated inputs
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        if not(b.piece.collide(b.grid, (-1, 0))) and holdNums[0] in {0, delays[0]}:
            b.piece.pos[0] -= 1

            if not(holdNums[0]):
                holdNums[0] = delays[1]

        holdNums[0] = max(holdNums[0] - 1, 0)
        lock = 0

    else:
        holdNums[0] = delays[0]

    if keys[pygame.K_RIGHT]:
        if not(b.piece.collide(b.grid, (1, 0))) and holdNums[1] in {0, delays[0]}:
            b.piece.pos[0] += 1

            if not(holdNums[1]):
                holdNums[1] = delays[1]

        holdNums[1] = max(holdNums[1] - 1, 0)
        lock = 0

    else:
        holdNums[1] = delays[0]

    if keys[pygame.K_DOWN]:
        if not(b.piece.collide(b.grid, (0, 1))) and holdNums[2] in {0, delays[0] - 1}:
            b.piece.move()

            if not(holdNums[2]):
                holdNums[2] = delays[1] - 4

        holdNums[2] = max(holdNums[2] - 1, 0)

    else:
        holdNums[2] = delays[0]

    # Render board and pieces
    b.render()

    if b.piece:
        b.piece.ghostrender()

    b.piece.render()

    # Place piece if about to hit groud
    if b.piece.collide(b.grid, (0, 1)):
        if lock >= locks[0] or totlock >= locks[1]:
            for off in b.piece.offs:
                b.grid[tuple(np.array(b.piece.pos) + off)] = b.piece.col

            b.piece = None

            placed = 5
            lock = 0
            totlock = 0

            lasthold = False

        else:
            lock += 1
            totlock += 1

    # Replace piece if hold is input
    if hold and not(lasthold) and b.piece:
        if b.held:
            n = b.piece.col
            b.piece = Piece(b, b.held)
            b.held = n

        else:
            b.held = b.piece.col
            b.piece = Piece(b)

            lock = 0
            totlock = 0

        lasthold = True

    # Refresh display
    pygame.display.update()
    clock.tick(60)
