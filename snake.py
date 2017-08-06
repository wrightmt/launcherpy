class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
#############################################################################
#^^^^^^^^NOT MY CODE CREDIT TO http://bit.ly/TLpDmo ^^^^^^^^
#vvvvvvvvMY CODE vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
def Draw(board,score):
	print '\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\t',board[1],'|', board[2],'|',board[3],'\n','\t---------\n','\t',board[4],'|', board[5],'|',board[6],'\n\t---------','\n','\t',board[7],'|', board[8],'|',board[9],'\nScore: ',score  
pos=5
board=['BUFFERXDXD',' ',' ',' ',' ',' ',' ',' ',' ',' ']
score=0
import random
spawnrate=int(raw_input('What do you want the spawn rate to be? Bigger=less coins (Must be int)\n'))
while (True):
	if(random.randint(1,spawnrate)==1):
		enemyspawn=random.randint(1,9)		
		if (board[enemyspawn]!='X'):		
			board[enemyspawn]='O'	
	x=getch()	
	if(x=='w' or x=='a' or x=='s' or x=='d'):
		board[pos]=' '
		if(x=='w' and pos!=1 and pos!=2 and pos!=3):
			if(board[pos-3]=='O'):
				score+=1			
			pos-=3
		if(x=='a' and pos!=1 and pos!=4 and pos!=7):
			if(board[pos-1]=='O'):
				score+=1			
			pos-=1
		if(x=='s' and pos!=7 and pos!=8 and pos!=9):
			if(board[pos+3]=='O'):
				score+=1			
			pos+=3
		if(x=='d' and pos!=3 and pos!=6 and pos!=9):
			if(board[pos+1]=='O'):
				score+=1			
			pos+=1
	board[pos]='X'
	Draw(board,score)
	if(x=='~'):
		break
	if (score>=20):
		print '\n\n\n\nYOU WIN!!!!!!'
		break
#This file is part of Python-mini-Game.

#    Python-mini-Game is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Python-mini-Game is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Python-mini-Game.  If not, see <http://www.gnu.org/licenses/>.