import random
from typing import List
from enum import Enum
from time import sleep
from threading import Thread
import keyboard
import os

score = 0

class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 3
    RIGHT = 6

class Food():
    def __init__(self, position: tuple[int]):
        self.position = position

class Snake():
    def __init__(self, startPosition: tuple[int]):
        self.body: List[tuple[int]] = []
        self.body.append(startPosition)
        self.direction = Direction.RIGHT
        self.score = 0
    
    def grow(self) -> None:
        pass

    def getNextPosition(self) -> tuple[int]:
        self.directions

    def move(self) -> None:
        #check if the snake moved into the direction it is a valid position
        global facing

        if facing == self.direction:
            return
        elif facing == Direction.UP and self.direction == Direction.DOWN:
            #check if the snake moved into the direction it is a valid position

            #find dound what position the snake would move to 
            return
        elif facing == Direction.DOWN and self.direction == Direction.UP:
            #check if the snake moved into the direction it is a valid position
            return
        elif facing == Direction.LEFT and self.direction == Direction.RIGHT:
            #check if the snake moved into the direction it is a valid position
            return
        elif facing == Direction.RIGHT and self.direction == Direction.LEFT:
            #check if the snake moved into the direction it is a valid position
            return
        else:
            self.direction = facing

    
        
class Grid():
    def __init__(self, x, y):
        if x < 10 or y < 10:
            raise ValueError('The grid must be at least 10x10')
        
        self.x = x
        self.y = y

        snakePosition = (round(x // 2), round(y // 2))
        foodPosition = self.getRandmonPoisition()
        
        while snakePosition == foodPosition:
            foodPosition = self.getRandmonPoisition()

        self.snake = Snake(snakePosition)
        self.food = Food(foodPosition)

    def getRandmonPoisition(self):
        x = random.randint(0, self.x)
        y = random.randint(0, self.y)

        return x, y
    
    def draw(self):
        #clear the screen  and draw the grid
        os.system('cls')
        for y in range(self.y):
            for x in range(self.x):
                if (x, y) in self.snake.body:
                    print('O', end='')
                elif (x, y) == self.food.position:
                    print('X', end='')
                else:
                    print('.', end='')

facing = Direction.RIGHT
running = False

def getUserDirection():
    global facing
    global running
    while True:
        if keyboard.is_pressed('w'):
            facing = Direction.UP
            print('up')
        elif keyboard.is_pressed('s'):
            facing = Direction.DOWN
            print('down')
        elif keyboard.is_pressed('a'):
            facing = Direction.LEFT
            print('left')
        elif keyboard.is_pressed('d'):
            facing = Direction.RIGHT
            print('right')
        else:
            facing = facing

        if running:
            sleep(0.001)
        else:
            break

def main():
    global running

    #creeate a grid
    grid = Grid(40, 20)

    tickRate = 1

    #start input hanlder loop to hanlde user control of the snake
    inputThread = Thread(target=getUserDirection)
    inputThread.start()
    
    while True:
        try:
            grid.snake.move()
            grid.draw()
        except:
            running = False
            print('You died')
            print('Your score was: ', grid.snake.score)
            sleep(tickRate)
            break

# main()

# getDirection()
