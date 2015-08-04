#!/usr/bin/python
# ---------------------------------------------------------------------------
# File: mipex1.py
# Version 12.6.2
# ---------------------------------------------------------------------------
# Licensed Materials - Property of IBM
# 5725-A06 5725-A29 5724-Y48 5724-Y49 5724-Y54 5724-Y55 5655-Y21
# Copyright IBM Corporation 2009, 2015. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with
# IBM Corp.
# ---------------------------------------------------------------------------
#
# mipex1.py - Entering and optimizing a mixed integer programming problem
#             Demonstrates different methods for creating a problem.
#
# The user has to choose the method on the command line:
#
#    python mipex1.py -r     generates the problem by adding rows
#    python mipex1.py -c     generates the problem by adding columns
#    python mipex1.py -n     generates the problem by adding a
#                            list of coefficients
#
# The MIP problem solved in this example is:
#
#   Maximize  x1 + 2 x2 + 3 x3 + x4
#   Subject to
#      - x1 +   x2 + x3 + 10 x4 <= 20
#        x1 - 3 x2 + x3         <= 30
#               x2      - 3.5x4  = 0
#   Bounds
#        0 <= x1 <= 40
#        0 <= x2
#        0 <= x3
#        2 <= x4 <= 3
#   Integers
#       x4

from __future__ import print_function

import sys

import cplex
import math
from cplex.exceptions import CplexError

# data common to all populateby functions
#my_obj = [1.0, 2.0, 3.0, 1.0]
#my_ub = [40.0, cplex.infinity, cplex.infinity, 3.0]
#my_lb = [0.0, 0.0, 0.0, 2.0]
#my_ctype = "CCCI"
#my_colnames = ["x1", "x2", "x3", "x4"]
#my_rhs = [20.0, 30.0, 0.0]
#my_rownames = ["r1", "r2", "r3"]
#my_sense = "LLE"

# constants
g = 1.0
m1 = 9999999.9
m2 = 8888888.9
verysmall = 1e-7

# inputs
my_balls_n = 4
my_balls_x = [0.0, 0.0, 0.0, 0.0]
my_balls_y = [0.0, 1.0, 0.0, 1.0]
my_balls_z = [1.0, 1.0, 0.0, 0.0]

# Vector x:
# 0 to (n*n-1): x(i->j);                                            n*n entries
# (n*n) to (2*n*n-1): f(i->j);                                      n*n entries
# (2*n*n) to (2*n*n-1+6*n): x extern (+x, -x, +y, -y, +z, -z)       6*n entries
# (2*n*n+6*n) to (2*n*n-1+12*n): f extern (+x, -x, +y, -y, +z, -z)  6*n entries

# fill in my_obj
len_sum = 0.0;
my_obj=[0.0 for x in range(2*my_balls_n*my_balls_n+12*my_balls_n)]
my_colnames=["" for x in range(2*my_balls_n*my_balls_n+12*my_balls_n)]
for i in range(0,my_balls_n):
    for j in range(0,my_balls_n):
        my_obj[i*my_balls_n+j] = -math.sqrt((my_balls_x[i]-my_balls_x[j])*(my_balls_x[i]-my_balls_x[j])+(my_balls_y[i]-my_balls_y[j])*(my_balls_y[i]-my_balls_y[j])+(my_balls_z[i]-my_balls_z[j])*(my_balls_z[i]-my_balls_z[j]))
        len_sum = len_sum - my_obj[i*my_balls_n+j]
        my_colnames[i*my_balls_n+j]="x("+str(i)+","+str(j)+")"

m = my_balls_n*my_balls_n -1

for i in range(0,my_balls_n):
    for j in range(0,my_balls_n):
        m+=1
        my_colnames[m]="f("+str(i)+","+str(j)+")"

for i in range(0, my_balls_n*6):
    m = m+1
    my_obj[m]= -len_sum-1.0
    my_colnames[m]="xex("+str(i/6)+","+str(i%6+1)+")"

for i in range(0, my_balls_n*6):
    m = m+1
    my_colnames[m]="fex("+str(i/6)+","+str(i%6+1)+")"

# fill in my_ub, my_lb, my_ctype
my_ctype = ""
my_ub=[0.0 for x in range(2*my_balls_n*my_balls_n+12*my_balls_n)]
my_lb=[0.0 for x in range(2*my_balls_n*my_balls_n+12*my_balls_n)]
for i in range(0,my_balls_n):
    for j in range(0,my_balls_n):
        if i!=j:
            my_ub[i*my_balls_n+j] = 1
        else:
            my_ub[i*my_balls_n+j] = 0
        my_lb[i*my_balls_n+j] = 0
        my_ctype = my_ctype + "I"

m = my_balls_n*my_balls_n -1
for i in range(0, my_balls_n*my_balls_n):
    m = m+1
    my_ub[m] = cplex.infinity
    my_lb[m] = 0.0
    my_ctype = my_ctype + "C"

for i in range(0, my_balls_n*6):
    m = m+1
    my_ub[m] = 1
    my_lb[m] = 0
    my_ctype = my_ctype + "I"

for i in range(0, my_balls_n*6):
    m = m+1
    my_ub[m] = cplex.infinity
    my_lb[m] = 0.0
    my_ctype = my_ctype + "C"

# Equations: 4*my_balls_n*my_balls_n+16*my_balls_n total
# x, y, z directions equilibrium * n balls      3*n entries
# f(i)-x(i) if-else clause                      2*(n*n+6*n) entries
# f(a->b) = f(b->a)                             n*(n-1)/2 entries
# x(a->b) = x(b->a)                             n*(n-1)/2 entries

# fill in my_rhs, my_sense
my_sense = ""
my_rhs = [0.0 for x in range(3*my_balls_n*my_balls_n+14*my_balls_n)]

my_rownames = ["r" for x in range(3*my_balls_n*my_balls_n+14*my_balls_n)]

for i in range(3*my_balls_n*my_balls_n+14*my_balls_n):
    my_rownames[i]="r("+str(i)+")"

for i in range(0,my_balls_n):
    my_rhs[i*3] = 0.0
    my_rhs[i*3+1] = 0.0
    my_rhs[i*3+2] = g
    my_sense = my_sense + "EEE"

m = my_balls_n*3-1
for i in range(0,my_balls_n*my_balls_n+6*my_balls_n):
    m = m+1
    my_rhs[m] =verysmall-m1
    m = m+1
    my_rhs[m] = 0.0
    my_sense = my_sense + "GG"

for i in range(my_balls_n*(my_balls_n-1)):
    m = m+1
    my_rhs[m] = 0.0
    my_sense = my_sense + "E"

#cosa = 2.0/math.sqrt(5.0)
#sina = cosa/2
#c2 = 1.0/math.sqrt(2.0)

#my_obj = [3.0, math.sqrt(5.0), math.sqrt(5.0), 1.0, math.sqrt(2.0), math.sqrt(2.0),0,0,0,0,0,0,0,0,0,0,0,0]
#my_ub = [1.1, 1.1, 1.1, 1.1, 1.1, 1.1, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity]
#my_lb = [-0.1, -0.1, -0.1, -0.1, -0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#my_ctype = "IIIIIICCCCCCCCCCCC"
#my_colnames = ["x1", "x2", "x3", "x4","x5", "x6","f1", "f2", "f3", "f4","f5", "f6","f7", "f8", "f9", "f10","f11", "f12"]
#my_rhs = [0.0, g, 0.0, g, 0.0, g, 0.0, g, verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0]
#my_rownames = ["r1", "r2", "r3","r4", "r5", "r6","r7", "r8", "r9","r10", "r11", "r12","r13","r14", "r15", "r16","r17","r18", "r19", "r20"]
#my_sense = "EEEEEEEEGGGGGGGGGGGG"

#my_obj = [-1.0, -math.sqrt(2.0), -math.sqrt(2.0), -1.0, -1.0, -1.0,0,0,0,0,0,0,0,0,0,0,0,0]
#my_ub = [1.1, 1.1, 1.1, 1.1, 1.1, 1.1, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity, cplex.infinity]
#my_lb = [-0.1, -0.1, -0.1, -0.1, -0.1, -0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#my_ctype = "IIIIIICCCCCCCCCCCC"
#my_colnames = ["x1", "x2", "x3", "x4","x5", "x6","f1", "f2", "f3", "f4","f5", "f6","f7", "f8", "f9", "f10","f11", "f12"]
#my_rhs = [0.0, g, 0.0, g, 0.0, g, 0.0, g, verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0,verysmall-m1, 0.0]
#my_rownames = ["r1", "r2", "r3","r4", "r5", "r6","r7", "r8", "r9","r10", "r11", "r12","r13","r14", "r15", "r16","r17","r18", "r19", "r20"]
#my_sense = "EEEEEEEEGGGGGGGGGGGG"

def populatebyrow(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    print(my_obj)
    print(my_ub)
    print(my_lb)
    print(my_ctype)
    print(my_colnames)
    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)
    
    # fill in rows
    rows=[[[] for x in range(2)] for x in range(3*my_balls_n*my_balls_n+14*my_balls_n)]
    # 3*n equilibrium
    for i in range(0,my_balls_n):
        # rows[i*3]: x, [[(my_balls_n + 2) entries],[(my_balls_n + 2) entries]]
        # rows[i*3+1]: y
        # rows[i*3+2]: z
        rows[i*3][0]=[]
        rows[i*3][1]=[]
        rows[i*3+1][0]=[]
        rows[i*3+1][1]=[]
        rows[i*3+2][0]=[]
        rows[i*3+2][1]=[]
        for j in range(0,my_balls_n):
            if i!=j :
                rows[i*3][0]+=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i]]
                rows[i*3][1]+=[-(my_balls_x[j]-my_balls_x[i])/my_obj[j*my_balls_n+i]]
                rows[i*3+1][0]+=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i]]
                rows[i*3+1][1]+=[-(my_balls_y[j]-my_balls_y[i])/my_obj[j*my_balls_n+i]]
                rows[i*3+2][0]+=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i]]
                rows[i*3+2][1]+=[-(my_balls_z[j]-my_balls_z[i])/my_obj[j*my_balls_n+i]]
        # add +x, -x
        rows[i*3][0]+=[my_colnames[2*my_balls_n*my_balls_n+i*6],my_colnames[2*my_balls_n*my_balls_n+i*6+1]]
        rows[i*3][1]+=[1.0, -1.0]
        rows[i*3+1][0]+=[my_colnames[2*my_balls_n*my_balls_n+i*6+2],my_colnames[2*my_balls_n*my_balls_n+i*6+3]]
        rows[i*3+1][1]+=[1.0, -1.0]
        rows[i*3+2][0]+=[my_colnames[2*my_balls_n*my_balls_n+i*6+4],my_colnames[2*my_balls_n*my_balls_n+i*6+5]]
        rows[i*3+2][1]+=[1.0, -1.0]

    # if - else
    m = my_balls_n*3-1
    for i in range(0,my_balls_n):
        for j in range(0,my_balls_n):
            m+=1
            rows[m][0]=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i], my_colnames[j*my_balls_n+i]]
            rows[m][1]=[1.0,-m1]
            m+=1
            rows[m][0]=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i], my_colnames[j*my_balls_n+i]]
            rows[m][1]=[-1.0,m2]

    for i in range(2*my_balls_n*my_balls_n, 2*my_balls_n*my_balls_n+6*my_balls_n):
        m+=1
        rows[m][0]=[my_colnames[i+6*my_balls_n], my_colnames[i]]
        rows[m][1]=[1.0,-m1]
        m+=1
        rows[m][0]=[my_colnames[i+6*my_balls_n], my_colnames[i]]
        rows[m][1]=[-1.0,m2]

    # f(a,b)=f(b,a)
    for i in range(0,my_balls_n-1):
        for j in range(i+1,my_balls_n):
            m+=1
            rows[m][0]=[my_colnames[my_balls_n*my_balls_n + j*my_balls_n+i], my_colnames[my_balls_n*my_balls_n + i*my_balls_n+j]]
            rows[m][1]=[1.0,-1.0]

    # x(a,b)=x(b,a)
    for i in range(0,my_balls_n-1):
        for j in range(i+1,my_balls_n):
            m+=1
            rows[m][0]=[my_colnames[j*my_balls_n+i], my_colnames[i*my_balls_n+j]]
            rows[m][1]=[1.0,-1.0]

#    rows = [[["x1", "x2", "x3", "x4"], [-1.0, 1.0, 1.0, 10.0]],
#            [["x1", "x2", "x3"], [1.0, -3.0, 1.0]],
#            [["x2", "x4"], [1.0, -3.5]]]
            
            #rows = [[["f1","f2","f5","f8","f9"],[1.0,cosa,c2,-1.0,1.0]],
            #[["f7","f2","f5"],[1.0,-sina,-c2]],
            #[["f1","f3","f6","f11","f12"],[1.0,cosa,c2,1.0,-1.0]],
            #[["f10","f3","f6"],[1.0,-sina,-c2]],
            #[["f3","f4","f5"],[cosa,1.0,-c2]],
            #[["f3","f5"],[sina,c2]],
            #[["f2","f4","f6"],[cosa,1.0,-c2]],
            #[["f2","f6"],[sina,c2]],
            #[["f1","x1"],[1.0,-m1]],
            #[["f1","x1"],[-1.0,m2]],
            #[["f2","x2"],[1.0,-m1]],
            #[["f2","x2"],[-1.0,m2]],
            #[["f3","x3"],[1.0,-m1]],
            #[["f3","x3"],[-1.0,m2]],
            #[["f4","x4"],[1.0,-m1]],
            #[["f4","x4"],[-1.0,m2]],
            #[["f5","x5"],[1.0,-m1]],
            #[["f5","x5"],[-1.0,m2]],
            #[["f6","x6"],[1.0,-m1]],
            #[["f6","x6"],[-1.0,m2]]]
    
    #    rows = [[["f1","f2","f8","f9"],[1.0,c2,-1.0,1.0]],
    #       [["f7","f2","f5"],[1.0,-c2,-1.0]],
    #       [["f1","f3","f11","f12"],[-1.0,-c2,-1.0,1.0]],
    #       [["f10","f3","f6"],[1.0,-c2,-1.0]],
    #       [["f3","f4"],[c2,1.0]],
    #       [["f3","f5"],[c2,1.0]],
    #       [["f2","f4"],[-c2,-1.0]],
    #       [["f2","f6"],[c2,1.0]],
    #       [["f1","x1"],[1.0,-m1]],
    #       [["f1","x1"],[-1.0,m2]],
    #       [["f2","x2"],[1.0,-m1]],
    #       [["f2","x2"],[-1.0,m2]],
    #       [["f3","x3"],[1.0,-m1]],
    #       [["f3","x3"],[-1.0,m2]],
    #       [["f4","x4"],[1.0,-m1]],
    #       [["f4","x4"],[-1.0,m2]],
    #       [["f5","x5"],[1.0,-m1]],
    #       [["f5","x5"],[-1.0,m2]],
    #       [["f6","x6"],[1.0,-m1]],
    #       [["f6","x6"],[-1.0,m2]]]

    print(rows)
    prob.linear_constraints.add(lin_expr=rows, senses=my_sense,
                                rhs=my_rhs, names=my_rownames)


def populatebycolumn(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.linear_constraints.add(rhs=my_rhs, senses=my_sense,
                                names=my_rownames)

    c = [[["r1", "r2"], [-1.0, 1.0]],
         [["r1", "r2", "r3"], [1.0, -3.0, 1.0]],
         [["r1", "r2"], [1.0, 1.0]],
         [["r1", "r3"], [10.0, -3.5]]]

    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub,
                       names=my_colnames, types=my_ctype, columns=c)


def populatebynonzero(prob):
    prob.objective.set_sense(prob.objective.sense.maximize)

    prob.linear_constraints.add(rhs=my_rhs, senses=my_sense,
                                names=my_rownames)
    prob.variables.add(obj=my_obj, lb=my_lb, ub=my_ub, types=my_ctype,
                       names=my_colnames)

    rows = [0, 0, 0, 0, 1, 1, 1, 2, 2]
    cols = [0, 1, 2, 3, 0, 1, 2, 1, 3]
    vals = [-1.0, 1.0, 1.0, 10.0, 1.0, -3.0, 1.0, 1.0, -3.5]

    prob.linear_constraints.set_coefficients(zip(rows, cols, vals))


def mipex1(pop_method):

    try:
        my_prob = cplex.Cplex()

        if pop_method == "r":
            handle = populatebyrow(my_prob)
        elif pop_method == "c":
            handle = populatebycolumn(my_prob)
        elif pop_method == "n":
            handle = populatebynonzero(my_prob)
        else:
            raise ValueError('pop_method must be one of "r", "c" or "n"')

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
        print("Column %d:  Value = %10f" % (j, x[j]))

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ["-r", "-c", "-n"]:
        print("Usage: mipex1.py -X")
        print("   where X is one of the following options:")
        print("      r          generate problem by row")
        print("      c          generate problem by column")
        print("      n          generate problem by nonzero")
        print(" Exiting...")
        sys.exit(-1)
    mipex1(sys.argv[1][1])
