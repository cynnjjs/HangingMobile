



def intlinprog(C, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, i):
	'''
	Solve the interget linear programming problem:
	min C^T * x
	subject to:
			A_ub * x <= b_ub
			A_lb * x >= b_lb
			A_eq * x == b_eq
			x[0:i] \in {0,1}
	'''
	pass;

