#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: revision2.py
# Author: Yining Chen
# Modified from IBM's cplex mixed integer programming example mipex1.py
# ---------------------------------------------------------------------------
# Vector x: 2*n*n+7*n total
# 0 to (n*n-1): x(i->j);                                            n*n entries
# (n*n) to (2*n*n-1): f(i->j);                                      n*n entries
# (2*n*n) to (2*n*n-1+n): x extern                                    n entries
# (2*n*n+n) to (2*n*n-1+7*n): f extern (+x, -x, +y, -y, +z, -z)     6*n entries
# ---------------------------------------------------------------------------
# Equations: 2*n*n+3*n total
# x, y, z directions equilibrium * n balls      3*n entries
# f(i)-x(i) if-else clause                      n*n+n entries
# f(a->b) = f(b->a)                             n*(n-1)/2 entries
# x(a->b) = x(b->a)                             n*(n-1)/2 entries

from __future__ import print_function

import sys

import cplex
import math
from cplex.exceptions import CplexError

# constants
m1 = 9999
m2 = 8888
verysmall = 0.0

# inputs
n = 4
my_balls_x = [0.0, 0.0, 0.0, 0.0]
my_balls_y = [0.0, 1.0, 0.0, 1.0]
my_balls_z = [1.0, 1,0, 0.0, 0.0]
my_balls_g = [1.0, 1.0, 1.0, 1.0]



# fill in my_obj
len_sum = 0.0;
my_obj=[0.0 for x in range(2*n*n+7*n)]
my_colnames=["" for x in range(2*n*n+7*n)]

for i in range(0,n):
    for j in range(0,n):
        # my_obj for each edge (i->j) is -edge_length
        my_obj[i*n+j] = -math.sqrt((my_balls_x[i]-my_balls_x[j])*(my_balls_x[i]-my_balls_x[j])+(my_balls_y[i]-my_balls_y[j])*(my_balls_y[i]-my_balls_y[j])+(my_balls_z[i]-my_balls_z[j])*(my_balls_z[i]-my_balls_z[j]))
        # summing up all edge_lengths
        len_sum = len_sum - my_obj[i*n+j]
        my_colnames[i*n+j]="x("+str(i)+","+str(j)+")"

m = n*n -1

for i in range(n):
    for j in range(0,n):
        m+=1
        my_colnames[m]="f("+str(i)+","+str(j)+")"

for i in range(n):
    m = m+1
    # my_obj for each external edge is -len_sum-1.0
    my_obj[m]= -len_sum-1.0
    my_colnames[m]="xex("+str(i)+")"

for i in range(n*6):
    m = m+1
    my_colnames[m]="fex("+str(i/6)+","+str(i%6+1)+")"

# fill in my_ub, my_lb, my_ctype
my_ctype = ""
my_ub=[0.0 for x in range(2*n*n+7*n)]
my_lb=[0.0 for x in range(2*n*n+7*n)]

for i in range(0,n):
    for j in range(0,n):
        # x(i->j) is either 0 or 1 when i!=j
        # x(i->i) has to be 0
        if i!=j:
            my_ub[i*n+j] = 1.1
        else:
            my_ub[i*n+j] = 0.1
        my_lb[i*n+j] = -0.1
        my_ctype = my_ctype + "I"

m = n*n -1

for i in range(0, n*n):
    m = m+1
    # each f is non-negative and has no upper bound
    my_ub[m] = cplex.infinity
    my_lb[m] = 0.0
    my_ctype = my_ctype + "C"

for i in range(0, n):
    m = m+1
    # x_external(i) is either 0 or 1
    my_ub[m] = 1.1
    my_lb[m] = -0.1
    my_ctype = my_ctype + "I"

for i in range(0, n*6):
    m = m+1
    # each f_external is non-negative and has no upper bound
    my_ub[m] = cplex.infinity
    my_lb[m] = 0.0
    my_ctype = my_ctype + "C"



# fill in my_rhs, my_sense, my_rownames
my_sense = ""
my_rhs = [0.0 for x in range(2*n*n+3*n)]
my_rownames = ["r" for x in range(2*n*n+3*n)]

for i in range(2*n*n+3*n):
    my_rownames[i]="r("+str(i)+")"

for i in range(n):
    # equilibrium in x, y, z directions
    my_rhs[i*3] = 0.0
    my_rhs[i*3+1] = 0.0
    my_rhs[i*3+2] = my_balls_g[i]
    my_sense = my_sense + "EEE"

m = n*3-1
for i in range(n*n+n):
    # when x(i) is 0, f(i) has to be 0
    m = m+1
    my_rhs[m] = verysmall
    my_sense = my_sense + "L"

for i in range(n*(n-1)):
    # Newton's third law
    m = m+1
    my_rhs[m] = 0.0
    my_sense = my_sense + "E"


def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    
    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)
    
    # fill in rows
    rows=[[[] for x in range(2)] for x in range(2*n*n+3*n)]
    
    # 3*n equilibrium
    for i in range(0,n):
        # rows[i*3]: [[(n + 2) entries],[(n + 2) entries]], equilibrium in x direction
        # rows[i*3+1]: [[(n + 2) entries],[(n + 2) entries]], equilibrium in y direction
        # rows[i*3+2]: [[(n + 2) entries],[(n + 2) entries]], equilibrium in z direction
        rows[i*3][0]=[]
        rows[i*3][1]=[]
        rows[i*3+1][0]=[]
        rows[i*3+1][1]=[]
        rows[i*3+2][0]=[]
        rows[i*3+2][1]=[]
        for j in range(0,n):
            if i!=j :
                rows[i*3][0]+=[my_colnames[n*n + j*n+i]]
                rows[i*3][1]+=[-(my_balls_x[j]-my_balls_x[i])/my_obj[j*n+i]]
                rows[i*3+1][0]+=[my_colnames[n*n + j*n+i]]
                rows[i*3+1][1]+=[-(my_balls_y[j]-my_balls_y[i])/my_obj[j*n+i]]
                rows[i*3+2][0]+=[my_colnames[n*n + j*n+i]]
                rows[i*3+2][1]+=[-(my_balls_z[j]-my_balls_z[i])/my_obj[j*n+i]]
    
        # add +x, -x
        rows[i*3][0]+=[my_colnames[2*n*n+n+i*6],my_colnames[2*n*n+n+i*6+1]]
        rows[i*3][1]+=[1.0, -1.0]
        # add +y, -y
        rows[i*3+1][0]+=[my_colnames[2*n*n+n+i*6+2],my_colnames[2*n*n+n+i*6+3]]
        rows[i*3+1][1]+=[1.0, -1.0]
        # add +z, -z
        rows[i*3+2][0]+=[my_colnames[2*n*n+n+i*6+4],my_colnames[2*n*n+n+i*6+5]]
        rows[i*3+2][1]+=[1.0, -1.0]

    # when x(i) is 0, f(i) has to be 0 for internal fs
    m = n*3-1
    for i in range(0,n):
        for j in range(0,n):
            m+=1
            rows[m][0]=[my_colnames[n*n + i*n+j], my_colnames[i*n+j]]
            rows[m][1]=[1.0,-m2]

    # when x(i) is 0, f(i) has to be 0 for external fs
    for i in range(n):
        m+=1
        rows[m][0]=[my_colnames[2*n*n+n+i*6], my_colnames[2*n*n+n+i*6+1],my_colnames[2*n*n+n+i*6+2],my_colnames[2*n*n+n+i*6+3],my_colnames[2*n*n+n+i*6+4],my_colnames[2*n*n+n+i*6+5],my_colnames[2*n*n+i]]
        rows[m][1]=[1.0,1.0,1.0,1.0,1.0,1.0,-m2]

    # f(a,b)=f(b,a)
    for i in range(0,n-1):
        for j in range(i+1,n):
            m+=1
            rows[m][0]=[my_colnames[n*n + j*n+i], my_colnames[n*n + i*n+j]]
            rows[m][1]=[1.0,-1.0]

    # x(a,b)=x(b,a)
    for i in range(0,n-1):
        for j in range(i+1,n):
            m+=1
            rows[m][0]=[my_colnames[j*n+i], my_colnames[i*n+j]]
            rows[m][1]=[1.0,-1.0]

    print("Constraints Printout:")
    for i in range(2*n*n+7*n):
        print("Column ",i,my_lb[i],"<=",my_colnames[i],"<=",my_ub[i],"weight =",my_obj[i],"type =",my_ctype[i])
    print()

    print("Equations Printout:")
    for i in range(2*n*n+3*n):
        print(i,rows[i],my_sense[i],my_rhs[i])
    print()

    prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)


def main():

    try:
        my_prob = cplex.Cplex()

        handle = populatebyrow(my_prob)

        my_prob.solve()
    
    except CplexError as exc:
            print(exc)
            return

    print()
    # solution.get_status() returns an integer code
    print("Solution status = ", my_prob.solution.get_status(), ":", end=' ')
    # the following line prints the corresponding string
    print(my_prob.solution.status[my_prob.solution.get_status()])
    print("Solution value  = ", my_prob.solution.get_objective_value())

    numcols = my_prob.variables.get_num()
    numrows = my_prob.linear_constraints.get_num()

    slack = my_prob.solution.get_linear_slacks()
    x = my_prob.solution.get_values()

    for j in range(numrows):
        print("Row %d:  Slack = %10f" % (j, slack[j]))
    for j in range(numcols):
        print("Column %d %s:  Value = %10f" % (j, my_colnames[j],x[j]))


if __name__ == "__main__":
    main()
