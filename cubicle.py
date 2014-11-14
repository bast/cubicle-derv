#!/usr/bin/env python

from pylab import *
import sys
import string
from optparse import OptionParser

usage = '''
  cubicle: utility to calculate various cube file derivatives
           requires python-pylab
  example: ./%prog -p 2 -d 1 --cubes="density-0.01.cube density+0.00.cube density+0.01.cube" --field="-0.01 +0.00 +0.01" > derv.cube'''

parser = OptionParser(usage)

parser.add_option('-p',
                  '--polynomial_order',
                  dest = 'polynomial_order',
                  help = 'order of the polynomial (2 for quadratic)',
                  metavar='N')
parser.add_option('-d',
                  '--derivative',
                  dest = 'derivative',
                  help = 'derivative (2 for second derivative)',
                  metavar='N')
parser.add_option('--cubes',
                  dest = 'cubes',
                  help = 'cube files to polyfit (space separated in "")',
                  metavar='"cube1 cube2 cube3 ..."')
parser.add_option('--field',
                  dest = 'field',
                  help = 'field strengths (space separated in "")',
                  metavar='"f1 f2 f3 ..."')

(options, args) = parser.parse_args()

if len(sys.argv) == 1:
    # user has given no arguments: print help and exit
    print parser.format_help().strip()
    sys.exit()

#-------------------------------------------------------------------------------

def from_file(file):
    f = open(file, 'r')
    s = f.read()
    f.close()
    return s

def file_to_array(s1):
    s1 = string.split(s1, '\n')
    s2 = ''
    for i in range(len(s1)):
        if i > 1:
            s2 = s2 + string.replace(s1[i], '\n', ' ')
    for x in range(10):
        s2 = string.replace(s2, '  ', ' ')
    return string.split(s2, ' ')

def fact(x):
    return (1 if x==0 else x * fact(x-1))

def get_derivative(x_l, y_l, p_order, d_order):
    c_l = polyfit(x_l, y_l, p_order)
    d_l = []
    for i in range(d_order + 1):
        d_l.append(fact(i)*c_l[len(c_l) - i - 1])
    return d_l[d_order]

#-------------------------------------------------------------------------------

cube_l = []
for cube in options.cubes.split():
    last_cube = cube
    cube_l.append(file_to_array(from_file(cube)))

f_l = []
for f in options.field.split():
    f_l.append(float(f))

#-------------------------------------------------------------------------------

nr_atoms = int(cube_l[0][1])

dim_x = int(cube_l[0][ 5])
dim_y = int(cube_l[0][ 9])
dim_z = int(cube_l[0][13])

first = 17 + nr_atoms*5
last  = len(cube_l[0]) - 1

polynomial_order = int(options.polynomial_order)
derivative       = int(options.derivative)

new_cube = []

for i in range(len(cube_l[0])):
    if i < first:
        new_cube.append(cube_l[0][i])
    else:
        if i < last + 1:
            p_l = []
            for cube in cube_l:
                p_l.append(float(cube[i]))
            new_cube.append(get_derivative(f_l, p_l, polynomial_order, derivative))

header = string.split(from_file(last_cube), '\n')
for x in range(6 + nr_atoms):
    print header[x]

index = first
for i in range(dim_x):
    for j in range(dim_y):
        s = ''
        count = 0
        for k in range(dim_z):
            if count < 6:
                s = s + '%13.5e' % new_cube[index]
                count = count + 1
            else:
                print s
                s = '%13.5e' % new_cube[index]
                count = 1
            if k == dim_z - 1:
                print s
            index = index + 1
