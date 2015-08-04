from analysis import *
from lpsolver import *


'''This is a 2D 4-node test case
	

	*		*
	

	*		*
'''

def main():
	nodes = [ (0,0,0), (0,0,1), (0,1,1), (0,1,0) ]
	mass  = [1,1,1,1]

	struct = Structure(nodes, mass)
	struct.solve()

	return;







if __name__ == '__main__':
	main()