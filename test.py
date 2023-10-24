import sys
import pickle
from maze import Cell
    

def countdown(start, end):
    yield start
    if start > end:
        yield from countdown(start - 1, end)

def wrapper(n):
    yield from countdown(n, 0)



if __name__ == "__main__":
    for num in wrapper(10):
        print(num)