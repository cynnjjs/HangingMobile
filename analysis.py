from lpsolver import intlinprog


class Structure:
	'''A hanging mobile structure which is a set of points and their masses'''
	def __init__(self, nodes, mass):
		self.nodes = nodes;
		self.mass = mass;     # The mass of the i-th node is self.mass[i]

	def internal_forces(self):
		'''get internal forces.
		A force is defined as a tuple: (a,b) meaning the force from a on b.
		@return a list of tuples;
		'''
		pass;

	def external_forces(self):
		'''get external forces'''
		pass;

	def inequality_constraints_ub(self):
		'''@return A_ub, b_ub'''
		pass;																	#

	def inequality_constraints_lb(self):
		'''@return A_lb, b_lb'''
		pass;

	def equality_constraints(self):
		'''@return A_eq, b_eq'''
		pass;

	def unknown(self):
		'''build X in this method.'''
		pass;

	def objective_function(self):
		'''@return C'''
		pass;

	def build_intlinprog(self):
		'''@return C, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, i'''
		pass;

	def solve(self):
		C, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, i = self.build_intlinprog();
		result = intlinprog(C, A_ub, b_ub, A_lb, b_lb, A_eq, b_eq, i);
		return result;


