import numpy as np


def load_rama_xvg(filename):
    data = []
    with open(filename, 'rt', encoding='utf-8') as f:
        for l in f:
            if l.startswith('#') or l.startswith('@'):
                continue
            phi, psi, resn = l.split()
            data.append((float(phi), float(psi), resn))
    return np.array(data, dtype=[('phi', 'f'), ('psi', 'f'), ('resn', 'S6')])
