import numpy as np


class GROFile(object):
    dtype = np.dtype([('resi', 'i4'), ('resn', 'S6'), ('atomtype', 'S6'), ('atomidx', 'i4'), ('x', 'f4'),
                      ('y', 'f4'), ('z', 'f4'), ('vx', 'f4'), ('vy', 'f4'), ('vz', 'f4')])

    def __init__(self, comment, boxsize, grodata=None):
        if grodata is not None:
            self.grodata = grodata
        else:
            self.grodata = np.zeros(0, dtype=self.dtype)
        self.comment = comment
        self.boxsize = boxsize

    @classmethod
    def new_from_file(cls, grofile):
        """Loads a .gro file. Currently velocities are not supported."""
        with open(grofile, 'rt', encoding='utf-8') as f:
            comment = f.readline()
            nentries = int(f.readline())
            grodata = np.zeros(nentries,
                               dtype=cls.dtype)
            for i in range(nentries):
                l = f.readline()
                try:
                    resi = int(l[:5])
                    resn = l[5:10].strip()
                    atomtype = l[10:15].strip()
                    atomidx = int(l[15:20])
                    coords = l[20:].split()
                    try:
                        x, y, z, vx, vy, vz = coords
                    except ValueError:
                        x, y, z = coords
                        vx, vy, vz = 0, 0, 0
                except ValueError:
                    raise ValueError('Cannot parse line #{:d} in file {}: {}'.format(i + 2, grofile, l))
                grodata[i] = (
                    resi, resn, atomtype, atomidx,
                    float(x), float(y), float(z),
                    float(vx), float(vy), float(vz))
            boxsize = [float(x) for x in f.readline().split()]
            return cls(comment, boxsize, grodata)

    def write(self, filename):
        """Write a .gro file."""
        with open(filename, 'wt', encoding='utf-8') as f:
            f.write(self.comment.strip() + '\n')
            f.write('{:d}\n'.format(len(self.grodata)))
            iatom = 0
            iresidue = 0
            residue = None
            for atom in self.grodata:
                iatom += 1
                if str(atom['resi']) + atom['resn'].decode('ascii') != residue:
                    iresidue += 1
                    residue = str(atom['resi']) + atom['resn'].decode('ascii')
                f.write(
                    '{:>8}{:>7}{:>5}{:>8.3f}{:>8.3f}{:8.3f}{:8.3f}{:8.3f}{:8.3f}\n'.format(
                        residue, atom['atomtype'].decode('ascii'), iatom,
                        atom['x'], atom['y'], atom['z'],
                        atom['vx'], atom['vy'], atom['vz']))
            f.write(''.join(['{:>10.5f}'.format(b) for b in self.boxsize]) + '\n')

    def getresidues(self):
        return set(self.grodata['resn'].tolist())

    def getatomtypes(self, resn):
        if not isinstance(resn, bytes):
            resn = resn.encode('ascii')
        return set(self.grodata[self.grodata['resn'] == resn]['atomtype'].tolist())

    def filter_resn(self, resn):
        if not isinstance(resn, bytes):
            resn = resn.encode('ascii')
        return type(self)(self.comment, self.boxsize, self.grodata[self.grodata['resn'] == resn])

    def filter_resi(self, resi):
        return type(self)(self.comment, self.boxsize, self.grodata[self.grodata['resi'] == resi])

    def __add__(self, other):
        return type(self)(self.comment, self.boxsize, np.concatenate(self.grodata, other.grodata))

    def __sub__(self, other):
        flags = np.empty(len(self.grodata))
        resid = set(zip([other.resi(), other.resn()]))
        for i in range(len(self.grodata)):
            flags[i] = not (self.grodata[i]['resi'], self.grodata[i]['resn']) in resid
        return type(self)(self.comment, self.boxsize, self.grodata[flags])

    def filter_atomname(self, atomname):
        if not isinstance(atomname, bytes):
            atomname = atomname.encode('ascii')
        return type(self)(self.comment, self.boxsize, self.grodata[self.grodata['atomtype'] == atomname])

    def x(self):
        return self.grodata['x']

    def y(self):
        return self.grodata['y']

    def z(self):
        return self.grodata['z']

    def vx(self):
        return self.grodata['vx']

    def vy(self):
        return self.grodata['vy']

    exit

    def vz(self):
        return self.grodata['vz']

    def resi(self):
        return self.grodata['resi']

    def resn(self):
        return self.grodata['resn']

    def extend_boolflags_to_residues(self, boolflags: np.array):
        marked_residues = set(self.grodata['resi'][boolflags])
        for i in range(len(self.grodata)):
            if self.grodata[i]['resi'] in marked_residues:
                boolflags[i] = True
        return boolflags

    def filter_boolflags(self, boolflags):
        return type(self)(self.comment, self.boxsize, self.grodata[boolflags])

    def __len__(self):
        return len(self.grodata)

    def resids(self):
        return sorted(set(['{:d}{}'.format(g['resi'], g['resn'].decode('ascii')) for g in self.grodata]))
