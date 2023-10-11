# -*- coding: utf-8 -*-
"""
Created on Sat Oct  7 14:30:48 2023

@author: 15440
"""
import sys

COLOR_RED = '\033[91m' #GFD
COLOR_ORANGE = '\033[33m' #LFD
COLOR_BLUE = '\033[94m' #CLIENT
COLOR_MAGENTA = '\033[95m' #SERVER

COLOR_RESET = '\033[0m'

def print_color(text, color):
    sys.stdout.write(color + text + COLOR_RESET + '\n')

# print_color('Hello, world!', COLOR_RED)
# print_color('Hello, world!', COLOR_GREEN)
# print_color('Hello, world!', COLOR_YELLOW)
# print_color('Hello, world!', COLOR_BLUE)
# print_color('Hello, world!', COLOR_MAGENTA)
# print_color('Hello, world!', COLOR_CYAN)
# print_color('Hello, world!', COLOR_RESET)