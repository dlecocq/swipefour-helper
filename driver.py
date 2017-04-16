#! /usr/bin/env python

import swipefour

s = swipefour.swipefour()
method = s.newRound

while True:
    try:
        letters = raw_input('What letters have you gotten? ')
        method(letters)
        method = s.gotLetters
        s.display()
    except KeyboardInterrupt:
        print('Starting a new game')
        method = s.newRound
