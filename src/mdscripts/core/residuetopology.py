class ResidueTopology(object):
    def __init__(self):
        self.name= ''
        self.atoms = []
        self.bonds = []
        self.angles = []
        self.dihedrals = []
        self.impropers = []
        self.cmaps=[]

    @classmethod
    def load(cls, filename):
        residue = None
        mode = None
        with open(filename, 'rt', encoding='utf-8') as f:
            for line in f:
                if line.strip().startswith(';'):
                    continue
                if line.strip().startswith('['):
                    caption = line.replace('[', '').replace(']', '').strip()
                    if caption == 'bondedtypes':
                        continue
                    elif caption in ['atoms', 'bonds', 'angles', 'impropers', 'dihedrals', 'cmap']:
                        mode = caption
                    else:
                        if residue is not None:
                            yield residue
                        residue = cls()
                        residue.name = caption
                        mode = None
                elif not line.strip():
                    continue
                elif mode == 'atoms':
                    name, type_, charge, cgroup = line.strip().split()
                    residue.atoms.append((name, type_, float(charge), int(cgroup)))
                elif mode == 'bonds':
                    first, last = line.strip().split()[:2]
                    residue.bonds.append((first, last))
                elif mode == 'angles':
                    first, mid, last = line.strip().split()[:3]
                    residue.angles.append((first, mid, last))
                elif mode == 'impropers':
                    a1, a2, a3, a4 = line.strip().split()[:4]
                    residue.impropers.append((a1,a2,a3,a4))
                elif mode == 'dihedrals':
                    a1,a2,a3,a4 = line.strip().split()[:4]
                    residue.dihedrals.append((a1,a2,a3,a4))
                elif mode == 'cmap':
                    a1, a2, a3, a4, a5 = line.strip().split()[:5]
                    residue.cmaps.append((a1, a2, a3, a4, a5))
        if residue is not None:
            yield residue
        return
