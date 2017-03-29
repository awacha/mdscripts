from .atom import Atom
from .bond import Bond
from .forcefield import ForceField

class Molecule(object):
    def __init__(self):
        self.atoms=[]
        self.bonds=[]
        self.maxresid=0
        self.maxchainid=0

    def add_atom(self, atom):
        self.atoms.append(atom)
        if atom.resid > self.maxresid:
            self.maxresid = atom.resid

    def add_bond(self, bond):
        already_bonded = [b for b in self.bonds if (b.atom1 is bond.atom1 and b.atom2 is bond.atom2) or (b.atom1 is bond.atom2 and b.atom2 is bond.atom1) ]
        if not already_bonded:
            self.bonds.append(bond)

    def atom(self, index):
        atms = [a for a in self.atoms if a.index == index]
        if not atms:
            raise IndexError
        if len(atms)>1:
            raise ValueError
        return atms[0]

    def mergeresids(self, resid1, resid2):
        for a in self.atoms:
            if a.resid in [resid1, resid2]:
                a.resid = min(resid1, resid2)

    def mergechainids(self, chainid1, chainid2):
        for a in self.atoms:
            if a.chainid in [chainid1, chainid2]:
                a.chainid = min(chainid1, chainid2)

    def updatemaxresid(self):
        self.maxresid=max(a.resid for a in self.atoms)

    def updatemaxchainid(self):
        self.maxchainid=max(a.chainid for a in self.atoms)

    def getresidue(self, resid):
        mol = Molecule()
        mol.atoms = [a for a in self.atoms if a.resid == resid]
        mol.bonds = [b for b in self.bonds if b.atom1 in mol.atoms and b.atom2 in mol.atoms]
        return mol

    def getchain(self, chainid):
        mol = Molecule()
        mol.atoms = [a for a in self.atoms if a.chainid == chainid]
        mol.bonds = [b for b in self.bonds if b.atom1 in mol.atoms and b.atom2 in mol.atoms]
        return mol

    def updateneighbours(self):
        for a in self.atoms:
            a.bonded_neighbours=[]
        for b in self.bonds:
            b.atom1.bonded_neighbours.append(b.atom2)
            b.atom2.bonded_neighbours.append(b.atom1)

    def findexclusions(self, distance=3):
        excl = []
        for d in range(distance):
            excl.extend(self.findpairs(d))
        def sortatomtuple(t):
            if t[0].index > t[-1].index:
                return tuple(reversed(t))
            else:
                return t
        excl = [sortatomtuple(p) for p in excl]
        return sorted(excl, key=lambda p:1000*p[0].index+p[1].index)

    def findpairs(self, steps=3):
        pairs = []
        for a in self.atoms:
            neighbours = a.neighbours(steps=steps)
            for n in neighbours:
                if ((a,n) not in pairs) and ((n,a) not in pairs):
                    pairs.append((a,n))
        def sortatomtuple(t):
            if t[0].index > t[-1].index:
                return tuple(reversed(t))
            else:
                return t
        pairs = [sortatomtuple(p) for p in pairs]
        return sorted(pairs, key=lambda p:1000*p[0].index+p[1].index)

    def findangles(self):
        angles = []
        for a in self.atoms:
            for route in a._neighbourroutes(2):
                if len(set(route))==3:
                    if not (route in angles or tuple(reversed(route)) in angles):
                        angles.append(route)
        def sortatomtuple(t):
            if t[0].index > t[-1].index:
                return tuple(reversed(t))
            else:
                return t
        angles = [sortatomtuple(a) for a in angles]
        return sorted(angles, key=lambda a:100000*a[0].index+1000*a[1].index+1*a[2].index)

    def finddihedrals(self):
        dihedrals = []
        for a in self.atoms:
            for route in a._neighbourroutes(3):
                if len(set(route))==4:
                    if not (route in dihedrals or tuple(reversed(route)) in dihedrals):
                        dihedrals.append(route)
        def sortatomtuple(t):
            if t[1].index > t[2].index:
                return tuple(reversed(t))
            else:
                return t
        dihedrals=[sortatomtuple(d) for d in dihedrals]
        return sorted(dihedrals, key=lambda d:100000000*d[1].index+1000000*d[2].index+1000*d[0].index+d[3].index)

    @classmethod
    def load_from_mol2(cls, mol2file):
        self=cls()
        with open(mol2file, 'rt') as f:
            while True:
                l=f.readline()
                if l.strip().startswith('@<TRIPOS>ATOM'):
                    break
                if not l:
                    raise EOFError
            while True:
                l=f.readline()
                if l.startswith('@<TRIPOS>BOND'):
                    break
                if not l:
                    raise EOFError
                l=l.strip()
                if not l:
                    continue
                l=l.rsplit(';')[0].rsplit('#')[0]
                idx, atomname, x, y, z, atomtype, *others = l.split()
                self.add_atom(Atom(int(idx), atomname.strip(), float(x), float(y), float(z), atomtype.strip(), *others))
            while True:
                l=f.readline()
                if not l:
                    break
                l=l.rsplit(';')[0].rsplit('#')[0]
                idx, atom1, atom2, bondtype = l.split()
                self.add_bond(Bond(self.atom(int(atom1)), self.atom(int(atom2)), bondtype))
        self.updateneighbours()
        self.updatemaxresid()
        self.updatemaxchainid()
        return self

    @classmethod
    def load_from_pdb(cls, pdbfile):
        self = cls()
        with open(pdbfile, 'rt') as f:
            for l in f:
                if l.startswith('ATOM  '):
                    idx = int(l[6:11])
                    atomname = l[12:16].strip()
                    altloc = l[16]
                    resname = l[17:20].strip()
                    chainid = l[21]
                    resid = int(l[22:26])
                    icode = l[26]
                    x=float(l[30:38])
                    y=float(l[38:46])
                    z=float(l[46:54])
                    occupancy=float(l[54:60])
                    tempFactor=float(l[60:66])
                    element=l[76:78].strip()
                    charge=l[78:80]
                    if not charge.strip():
                        charge = 0
                    else:
                        charge = int(charge[0])*int(charge[1]+'1')
                    self.add_atom(Atom(idx, atomname, x, y, z, element, resid, resname, charge))
                elif l.startswith('CONECT'):
                    atom1=int(l[6:11])
                    for span in [(11,16),(16,21),(21,26),(26,31)]:
                        try:
                            bondedatom = int(l[span[0]:span[1]])
                        except (IndexError, ValueError):
                            break
                        self.add_bond(Bond(self.atom(atom1), self.atom(bondedatom),1))
        self.updateneighbours()
        self.updatemaxresid()
        self.updatemaxchainid()
        return self

    def check_bonds(self, forcefield:ForceField):
        errors = 0
        for b in self.bonds:
            at1=b.atom1.atomtype
            at2=b.atom2.atomtype
            bt=forcefield.get_bond(at1,at2)
            if len(bt)==0:
                print('Error: no bond type in the forcefield between atom types {} and {}'.format(at1,at2))
                errors +=1
            if len(bt)>1:
                print('Error: ambiguous bond types ({} found) in the forcefield between atom types {} and {}'.format(len(bt),at1,at2))
                errors +=1

    def check_angles(self, forcefield:ForceField):
        errors = 0
        for angle in self.findangles():
            at1, at2, at3 = [a.atomtype for a in angle]
            at = forcefield.get_angle(at1, at2, at3)
            if len(at)==0:
                print('Error: no angle type in the forcefield between atom types {}, {} and {}'.format(at1,at2, at3))
                errors +=1
            if len(at)>1:
                print('Error: ambiguous angle types ({} found) in the forcefield between atom types {}, {} and {}'.format(len(at),at1,at2,at3))
                errors +=1

    def check_dihedrals(self, forcefield:ForceField):
        errors = 0
        for dihedral in self.finddihedrals():
            at1, at2, at3, at4 = [a.atomtype for a in dihedral]
            dt = forcefield.get_dihedral(at1, at2, at3, at4)
            if len(dt)==0:
                print('Error: no dihedral angle type in the forcefield between atom types {}, {}, {} and {}'.format(at1,at2,at3,at4))
                errors +=1
            if len(dt)>1:
                print('Error: ambiguous angle types ({} found) in the forcefield between atom types {}, {}, {} and {}'.format(len(dt),at1,at2,at3,at4))
                errors +=1

    def check_forcefield(self, forcefield:ForceField):
        return self.check_bonds(forcefield)+self.check_angles(forcefield)

    def write_topology(self, filename):
        if isinstance(filename, str):
            f = open(filename, 'wt')
        else:
            f = filename
        try:
            f.write('[ moleculetype ]\n')
            f.write('; Name            nrexcl\n')
            f.write('Protein             3\n')
            f.write('\n')
            f.write('[ atoms ]\n')
            f.write(';   nr       type  resnr residue  atom   cgnr     charge       mass  typeB    chargeB      massB\n')
            qtot = 0
            for resid in range(self.maxresid+1):
                residue = self.getresidue(resid)
                f.write('; residue {:3d} {} rtp {}  q  0.0\n'.format(residue.atoms[0].resid, residue.atoms[0].resn, residue.atoms[0].resn))
                for a in residue.atoms:
                    a.chargegroup=1
                    qtot+=a.charge
                    f.write('{0.index:6d} {0.atomtype:>10} {0.resid:6} {0.resn:>6} {0.name:>6} {0.chargegroup:6}      {0.charge:>5.2f} {0.mass:>10.3f}   ; qtot {1:<.2f}\n'.format(a, qtot))
            f.write('\n')
            f.write('[ bonds ]\n')
            f.write(';  ai    aj funct            c0            c1            c2            c3\n')
            for b in self.bonds:
                f.write('{.index:5} {.index:5}     1\n'.format(b.atom1, b.atom2))
            f.write('\n')
            f.write('[ pairs ]\n')
            f.write(';  ai    aj funct            c0            c1            c2            c3\n')
            for p in self.findpairs(3):
                f.write('{.index:5} {.index:5}     1\n'.format(*p))
            f.write('\n')
            f.write('[ angles ]\n')
            f.write(';  ai    aj    ak funct            c0            c1            c2            c3\n')
            for a in self.findangles():
                f.write('{.index:5} {.index:5} {.index:5}     5\n'.format(*a))
            f.write('\n')
            f.write('[ dihedrals ]\n')
            f.write(';  ai    aj    ak    al funct            c0            c1            c2            c3            c4            c5\n')
            for d in self.finddihedrals():
                f.write('{.index:5} {.index:5} {.index:5} {.index:5}     9\n'.format(*d))
            f.write('\n')
            f.write('[ dihedrals ]\n')
            f.write(';  ai    aj    ak    al funct            c0            c1            c2            c3\n')
        finally:
            if f is not filename:
                f.close()
