from cProfile import Profile
from pstats import SortKey, Stats

import numpy as np
from atom import Atom
from system import System
from dynamics import applyThermalBath, computeMechanicalEnergy, computeDistance, computeKinetic, updateAcc
from constants import RMIN

x = 6
y = 6
z = 6
x2 = 12
y2 = 12
delta = 0.1
d = RMIN + delta
listPos = np.asarray(
    [
        [ 0,  0, 0],
        [ d,  0, 0],
        [ 0,  d, 0],
        [-d,  0, 0],
        [ 0, -d, 0],

        [ 0,  y, 0],
        [ d,  y, 0],
        [ 0,  y + d, 0],
        [-d,  y, 0],
        [ 0,  y - d, 0],

        [ x,  0, 0],
        [ x + d,  0, 0],
        [ x,  d, 0],
        [ x - d,  0, 0],
        [ x, -d, 0],
        ########################

        [ 0,  0, z],
        [ d,  0, z],
        [ 0,  d, z],
        [-d,  0, z],
        [ 0, -d, z],

        [ 0,  y2, z],
        [ d,  y2, z],
        [ 0,  y2 + d, z],
        [-d,  y2, z],
        [ 0,  y2 - d, z],

        [ x2,  0, z],
        [ x2 + d,  0, z],
        [ x2,  d, z],
        [ x2 - d,  0, z],
        [ x2, -d, z],
    ],
    dtype=float
)


listAtom = []
for (i, pos) in enumerate(listPos):
    atom = Atom()
    atom.pos = np.asarray(pos.copy(), dtype=float)
    atom.vel = np.asarray([0, 0, 0], dtype=float)
    atom.acc = np.asarray([0, 0, 0], dtype=float)
    if i in [0, 5, 15, 20, 25]:
        atom.mass = 100
    else:
        atom.mass = 0.5
    #
    listAtom.append(atom)

system = System(listAtom)

initialEnergy = computeMechanicalEnergy(system)
desiredKinetic = initialEnergy / 2

n = 20000 #200000

with Profile() as profile:

    isInsideBall = False
    for i in range(n):
        system.move()

        # updateLennarJonesAcc(atom1, atom2)
        updateAcc(system)

        _, distance = computeDistance(listAtom[0], listAtom[1]) #<<< include other atoms!

        if abs(distance - RMIN) < 0.01:
            if not isInsideBall:
                isInsideBall = True

                # kinetic = computeKinetic(system)
                # print("Applying thermal bath. Kinetic energy = ", kinetic)

                applyThermalBath(system, desiredKinetic)           
        else:
            isInsideBall = False
    #
    (
        Stats(profile).strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats()
    )