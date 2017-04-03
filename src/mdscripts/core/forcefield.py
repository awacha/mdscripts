import os

import numpy as np


class ForceField(object):
    def __init__(self):
        self.atomtypes = []
        self.pairtypes = []
        self.bondtypes = []
        self.constrainttypes = []
        self.angletypes = []
        self.dihedraltypes = []
        self.implicit_genborn_params = []
        self.cmaptypes = []
        self.nonbond_params = []

    @classmethod
    def load_gromacs_ff(cls, ffdir):
        self=cls()
        self.load_from_file(os.path.join(ffdir,'forcefield.itp'))
        return self

    def load_from_file(self, filename, mode=None, defs=None, ifdefs = None):
        mode = mode
        if defs is None:
            defs = []
        if ifdefs is None:
            ifdefs = []
        inactive_because_ifdef = False
        previous_line = ''
        with open(filename, 'rt') as f:
            for l in f:
                if ';' in l:
                    l=l.split(';')[0]
                l = previous_line +l
                previous_line = ''
                l=l.strip()
                if not l:
                    continue
                if l.endswith('\\'):
                    previous_line = l[:-1]+' '
                    continue
                if l.startswith('#'):
                    #preprocessor directive
                    target = l.split(None, 1)[-1]
                    if l.startswith('#define '):
                        defs.append(target)
                    elif l.startswith('#undef '):
                        defs = [d for d in defs if d!=target]
                    elif l.startswith('#ifdef '):
                        ifdefs.append((target, target in defs))
                    elif l.startswith('#ifndef '):
                        ifdefs.append((target, target not in defs))
                    elif l.startswith('#else '):
                        ifdefs[-1] = (ifdefs[-1][0], not ifdefs[-1][1])
                    elif l.startswith('#endif'):
                        ifdefs=ifdefs[:-1]
                    elif l.startswith('#include'):
                        #print('#Including {}'.format(target))
                        mode, defs, ifdefs = self.load_from_file(os.path.join(os.path.split(filename)[0],target[1:-1]), mode, defs, ifdefs)
                    continue
                if ifdefs and (not ifdefs[-1][1]):
                    #print('Skipping line in mode [ {} ] because of an unsatisfied preprocessor conditional ({}): {}'.format(mode, ifdefs[-1][0],l))
                    continue
                if l.startswith('[') and l.endswith(']'):
                    mode = l[1:-1].strip()
                    continue
                if mode == 'defaults':
                    nbfunc, combrule, genpairs, fudgeLJ, fudgeQQ = l.split()
                    self.nbfunc=int(nbfunc)
                    self.combrule=int(combrule)
                    self.genpairs = genpairs.lower()=='yes'
                    self.fudgeLJ=float(fudgeLJ)
                    self.fudgeQQ=float(fudgeQQ)
                elif mode == 'atomtypes':
                    at, atnum, mass, charge, ptype, sigma, epsilon = l.split()
                    self.atomtypes.append((at, int(atnum), float(mass), float(charge), ptype, float(sigma), float(epsilon)))
                elif mode == 'pairtypes':
                    at1, at2, func, sigma, epsilon = l.split()
                    self.pairtypes.append((at1, at2, int(func), float(sigma), float(epsilon)))
                elif mode == 'bondtypes':
                    lis=l.split()
                    self.bondtypes.append((lis[0], lis[1], int(lis[2]))+tuple(float(x) for x in lis[3:]))
                elif mode == 'constrainttypes':
                    at1, at2, func, value = l.split()
                    self.constrainttypes.append((at1, at2, int(func), float(value)))
                elif mode == 'angletypes':
                    lis = l.split()
                    self.angletypes.append(tuple(lis[:3])+(int(lis[3]),) + tuple([float(x) for x in lis[4:]]))
                elif mode == 'dihedraltypes':
                    lis = l.split()
                    self.dihedraltypes.append(tuple(lis[:4])+(int(lis[4]),)+tuple([float(x) for x in lis[5:]]))
                elif mode == 'implicit_genborn_params':
                    at, sar, st, pi, gbr, hct = l.split()
                    self.implicit_genborn_params.append((at, float(sar), float(st), float(pi), float(gbr), float(hct)))
                elif mode == 'cmaptypes':
                    at1, at2, at3, at4, at5, func, nx, ny, data = l.split(None,8)
                    data = np.array([float(d) for d in data.split()]).reshape(int(nx), int(ny))
                    self.cmaptypes.append((at1, at2, at3, at4, at5, int(func), int(nx), int(ny), data))
                elif mode == 'nonbond_params':
                    at1, at2, func, sigma, epsilon = l.split()
                    self.nonbond_params.append((at1, at2, int(func), float(sigma), float(epsilon)))
                else:
                    print('Unknown mode: {}'.format(mode))
        return mode, defs, ifdefs

    def get_atomtype(self, at1):
        return [a for a in self.atomtypes if a[0] == at1]

    def get_bond(self, at1, at2):
        return [b for b in self.bondtypes if (b[0]==at1 and b[1]==at2) or (b[1] == at1 and b[0] == at2)]

    def get_angle(self, at1, at2, at3):
        return [a for a in self.angletypes if (a[0]==at1 and a[1] == at2 and a[2]==at3) or (a[0]==at3 and a[1]==at2 and a[2]==at1)]

    def get_dihedral(self, at1, at2, at3, at4):
        return [d for d in self.dihedraltypes if
               (d[0] in (at1,'X') and d[1]==at2 and d[2]==at3 and d[3] in (at4, 'X')) or
               (d[0] in (at4,'X') and d[1]==at3 and d[2]==at2 and d[3] in (at1, 'X'))]

    def get_pair(self, at1, at2):
        return [p for p in self.pairtypes if (p[0]==at1 and p[1]==at2) or (p[0]==at2 and p[1]==at1) ]

    def get_nonbond_param(self, at1, at2):
        return [p for p in self.nonbond_params if (p[0]==at1 and p[1]==at2) or (p[0]==at2 and p[1]==at1) ]

    def new_atomtype(self, newname, basedon):
        """Create a new atom type by copying another."""
        def replaceif(newname, basedon, tup, length):
            if length > 0:
                for t in replaceif(newname, basedon, tup[1:], length-1):
                    if tup[0] == basedon:
                        yield (newname,) + t
                    yield (tup[0],) +t
            else:
                yield tup
            return
        for length, attr in [(1, 'atomtypes'),
                             (2, 'bondtypes'),
                             (3, 'angletypes'),
                             (4, 'dihedraltypes'),
                             (2, 'constrainttypes'),
                             (2, 'pairtypes'),
                             (1, 'implicit_genborn_params'),
                             (5, 'cmaptypes'),
                             (2, 'nonbond_params')]:
            lis = getattr(self, attr)
            newlis = []
            for row in lis:
                newlis.extend(list(replaceif(newname, basedon, row, length)))
            setattr(self, attr, newlis)

    def write_forcefield(self):

        self.atomtypes = sorted(self.atomtypes, key=lambda at:at[0])
        self.bondtypes = sorted(self.bondtypes, key=lambda bt:bt[:2])
        self.angletypes = sorted()


