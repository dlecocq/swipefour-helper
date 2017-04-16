#! /usr/bin/env python

# Join together output
from string import join
# We need to count the frequency of each letter
from itertools import groupby

class swipefour(object):
	def __init__(self):
		self.board = None
		self.letters = ""
		# A list of unplayable letters
		self.unplayable = []
	
	def newRound(self, letters):
		self.letters = ''
		self.board = board()
		# Play the first letters provided
		self.board.move(1, 1, letters[0])
		self.board.move(2, 1, letters[1])
		self.board.move(1, 2, letters[2])
		self.board.move(2, 2, letters[3])
		self.display()
	
	def gotLetters(self, letters, auto=True):
		self.letters += letters
		if (len(self.letters) > 4):
			raise Exception("Too many letters!")
		if (len(self.letters) == 4 and auto):
			self.autoPlay()
	
	def autoPlay(self):
		mv = self.getMove()
		self.play(mv)
		self.display()
		print repr(mv)
	
	def play(self, mv):		
		self.board.move(mv['spot'][0], mv['spot'][1], mv['letter'])
		self.letters = self.letters.replace(mv['letter'], '', 1)
	
	def display(self):
		self.board.display()
	
	def getMoves(self, deep=False):
		# A list of the possible moves, a list of dictionaries,
		# {'spot':(x, y), 'letter':' ', 'words':[...]}
		possibilities = []
		# Look at all the squares that are open...
		for spot in self.board.openSquares():
			# Then for each of the letters that we have...
			for letter in list(set(self.letters)):
				# Then for each of the words you can make with it...
				words = self.board.words(spot[0], spot[1], letter, deep=deep)
				if (len(words)):
					possibilities.append({'letter':letter, 'deep':deep, 'words':words, 'spot':spot })
		# Get a list of unplayable letters 
		found = list(set([p['letter'] for p in possibilities]))
		self.unplayable = list(set(self.letters))
		for letter in found:
			self.unplayable.remove(letter)
		for letter in self.unplayable:
			print "%s is unplayable on this board..." % letter
		# If we couldn't find any moves, try using the deep dictionary
		if (len(possibilities) or deep):
			return possibilities
		else:
			return self.getMoves(deep=True)
	
	def score(self, mv):
		# Initialize the score to 0
		s = 0
		# The spot for the move
		sp = mv['spot']
		# Check to see if there are any letters that are currently
		# unplayable, but if we could play it after making this move
		for letter in self.unplayable:
			# Temporarily play that move...
			self.board.move(mv['spot'][0], mv['spot'][1], mv['letter'])
			# Look at all the squares that are open...
			for spot in self.board.openSquares():
				# Then for each of the words you can make with it...
				words = self.board.words(spot[0], spot[1], letter)
				if (len(words)):
					# Then we could play that letter... so add a bunch of points
					print "Move could make unplayable letter playable!"
					s += 10 / board.frequencies[letter]
			# Unplay the move...
			self.board.unmove(mv['spot'][0], mv['spot'][1])
		# If a move is to be made in the corner, it doesn't effect
		# where letters can be placed. Except if that is the only
		# place a very rare letter can be played.
		if (mv['letter'] in ['a', 'e', 'i', 'o', 'u']):
			for sq in self.board.adjacentSquares(sp[0], sp[1]):
				if not sq.filled():
					# It's good to have empty squares next to vowels
					s += 20
		else:
			# If it's not a vowel, the corner is a good place
			if (sp == (0, 0) or sp == (3, 0) or sp == (0, 3) or sp == (3, 3)):
				s += 50
		# board.frequencies has letter frequencies
		s += 1 / board.frequencies[mv['letter']]
		return s
	
	def getMove(self):
		return sorted(self.getMoves(), key=self.score, reverse=True)[0]

class square(object):
	def __init__(self):
		self.visited = False
		self.letter  = ''
	
	def open(self):
		return len(self.letter) == 0
	
	def filled(self):
		return len(self.letter) > 0

class board(object):
	frequencies = None
	validWords  = None
	deepWords   = None
	
	def __init__(self):
		self.squares = self.initializeSquares()
		self.initializeDictionary()
	
	def initializeDictionary(self):
		if (board.frequencies == None or board.validWords == None):
			print "Reading dictionary.txt"
			text = file("dictionary.txt").read().lower()
			letters = [l for l in text.replace('\n', '')]
			letters.sort()
			# Frequencies are normalized
			board.frequencies = dict([(k, len(list(g)) / float(len(letters))) for k, g in groupby(letters)])
			board.validWords = text.split('\n')
			print "Reading deep.txt"
			text = file("deep.txt").read().lower()
			board.deepWords = text.split('\n')
			print "Done"
	
	def initializeSquares(self):
		results = {}
		for i in range(4):
			for j in range(4):
				results[(i, j)] = square()
		return results
	
	def display(self):
		for j in range(4):
			row = []
			for i in range(4):
				square = self.squares[(i,j)]
				if (square.filled()):
					row.append(square.letter)
				else:
					row.append('_')
			print '|%s|' % join(row, '|')
	
	# Letter is the letter we'd be playing at x, y
	def words(self, x, y, stem, length = 3, deep=False):
		# This is the square at x, y:
		home = self.squares[(x, y)]
		home.visited = True
		# These are the results we will return
		results = []
		
		# If this is the first square visited... mark it as fil
		if length == 0:
			results = [self.squares[(x,y)].letter]
		else:
			# For all the squares we can validly reach from here (sideways and diagonally)...
			for spot in self.validSquares(x, y):
				# Square holds the square at spot
				square = self.squares[spot]
				# Append all the words we can make continuing from spot.
				for word in self.words(spot[0], spot[1], square.letter, length - 1, deep):
					results.append(stem + word)
				
				# If this is the base node, then we need to do some extra work
				if (length == 3):
					# Also check for this being the 2nd/3rd letter in a word
					# Start at the other square, then go to this one,
					square.visited = True
					for word in self.words(x, y, stem, 2, deep):
						results.append(square.letter + word)
					square.visited = False
		# If this is the base node, we need to also return all words in reverse
		if (length == 3):
			results += [word[::-1] for word in results]
			if (deep):
				print "Running DEEP!"
				results = [r for r in results if r in board.deepWords]
			else:
				results = [r for r in results if r in board.validWords]
		home.visited = False
		# Return the results we've gathered
		return list(set(results))
	
	def adjacentSpots(self, x, y):
		return [(i, j) for i in range(x-1, x+2) for j in range(y-1, y+2) if (i < 4 and i >= 0 and j < 4 and j >= 0)]
	
	def adjacentSquares(self, x, y):
		return [self.squares[s] for s in self.adjacentSpots(x, y)]
	
	def openSquares(self):
		return [(i, j) for i in range(4) for j in range(4) if self.squares[(i,j)].open()]
		
	def move(self, x, y, letter):
		square = self.squares[(x, y)]
		if (len(square.letter)):
			raise KeyError("Square at (%d, %d) already has letter %s" % (x, y, square.letter))
		else:
			square.letter = letter
	
	def unmove(self, x, y):
		square = self.squares[(x, y)]
		square.letter = ''
	
	def validSquares(self, x, y):
		return [s for s in self.adjacentSpots(x, y) if (not self.squares[s].visited) and self.squares[s].filled()]
	
	def visit(self, x, y):
		self.squares[(x,y)].visited = True
	
	# Undo the visiting of the square
	def unvisit(self, square):
		self.squares[(x,y)].visited = False
