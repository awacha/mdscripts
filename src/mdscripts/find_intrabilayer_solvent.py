import argparse
import re
import sys

import numpy as np


def loadgro(grofile):
    with open(grofile, 'rt', encoding='utf-8') as f:
        comment = f.readline()
        nentries = int(f.readline())
        grodata = np.zeros(nentries,
                           dtype=[('resi', 'i4'), ('resn', 'S6'), ('atomtype', 'S6'), ('atomidx', 'i4'), ('x', 'f4'),
                                  ('y', 'f4'),
                                  ('z', 'f4')])
        for i in range(nentries):
            l = f.readline()
            m = re.match(
                "\s*(?P<resi>\d+)(?P<resn>\w+)\s+(?P<atomtype>\w{1,3})\s*(?P<atomidx>\d+)\s+(?P<x>[+-]?\d+\.\d+)\s+(?P<y>[+-]?\d+\.\d+)\s+(?P<z>[+-]?\d+\.\d+)",
                l)
            if m is None:
                raise ValueError('Cannot parse line #{:d} in file {}:\n'.format(i + 2, grofile), l)
            resi, resn, atomtype, atomidx, x, y, z = m.groups()
            grodata[i] = (int(resi), resn, atomtype, int(atomidx), float(x), float(y), float(z))
        boxx, boxy, boxz = [float(x) for x in f.readline().split()]
        return grodata, comment, (boxx, boxy, boxz)


def getresidues(grodata):
    return set(grodata['resn'].tolist())


def getatomtypes(grodata, resn):
    if not isinstance(resn, bytes):
        resn = resn.encode('ascii')
    return set(grodata[grodata['resn'] == resn]['atomtype'].tolist())


def getheadlayers(grodata, lipidname, atomtype=b'P8'):
    print(atomtype)
    if not isinstance(atomtype, bytes):
        atomtype = atomtype.encode('ascii')
    if not isinstance(lipidname, bytes):
        lipidname = lipidname.encode('ascii')
    zP = grodata[(grodata['resn'] == lipidname) & (grodata['atomtype'] == atomtype)]['z']
    lower = zP[zP < np.median(zP)].mean()
    upper = zP[zP > np.median(zP)].mean()
    return lower, upper


def interlayersolvents(grodata, lipidname, solventname, headgroup_atomtype=b'P8'):
    if not isinstance(solventname, bytes):
        solventname = solventname.encode('ascii')
    lower, upper = getheadlayers(grodata, lipidname, headgroup_atomtype)
    badsolventidx = (grodata['resn'] == solventname) & (grodata['z'] >= lower) & (grodata['z'] <= upper)
    badresids = {b['resi'] for b in grodata[badsolventidx]}
    return badresids, lower, upper


def run():
    parser = argparse.ArgumentParser(
        description="Find misplaced solvent molecules in the phospholipid carbon chain region")
    parser.add_argument('-f', action='store', dest='inputfile', type=str, help='Input .gro file')
    parser.add_argument('-s', action='store', dest='solventname', type=str, help='Solvent residue name', default='SOL')
    parser.add_argument('-l', action='store', dest='lipidname', type=str, help='Lipid residue name')
    parser.add_argument('-a', action='store', dest='atomtype', type=str, help='Lipid headgroup atom type', default='P8')
    parser.add_argument('-t', action='store', dest='topology', type=str, help='Topology  file (.top)',
                        default=None)
    parser.add_argument('-o', action='store', dest='finalgro', type=str, help='The output .gro file',
                        default='confout.gro')
    # parser.add_help()
    args = vars(parser.parse_args())
    if args['inputfile'] is None or args['lipidname'] is None:
        parser.print_help()
        sys.exit(1)
    grodata, comment, boxsize = loadgro(args['inputfile'])
    print('Loaded {:d} atoms from file {}.'.format(len(grodata), args['inputfile']))
    badresids, lower, upper = interlayersolvents(grodata, args['lipidname'], args['solventname'], args['atomtype'])
    print('Lower and upper mean z coordinates of the head group layer: {} and {}'.format(lower, upper))
    print('Found {} misplaced solvent molecules:'.format(len(badresids)))
    print('  ', ', '.join('{:d}{}'.format(b, args['solventname']) for b in sorted(badresids)))
    for g in grodata:
        if g['resn'] == args['solventname'].encode('ascii') and g['resi'] in badresids:
            g['atomtype'] = b'$$'
    goodgro = grodata[grodata['atomtype'] != b'$$']
    print(len(goodgro))
    print(goodgro)
    with open(args['finalgro'], 'wt', encoding='utf-8') as f:
        f.write(comment.strip() + '\n')
        f.write('{:d}\n'.format(len(goodgro)))
        iatom = 0
        iresidue = 0
        residue = None
        for atom in goodgro:
            iatom += 1
            if str(atom['resi']) + atom['resn'].decode('ascii') != residue:
                iresidue += 1
                residue = str(atom['resi']) + atom['resn'].decode('ascii')
            f.write('{:>8}{:>7}{:>5}{:>8.3f}{:>8.3f}{:8.3f}\n'.format(residue, atom['atomtype'].decode('ascii'), iatom,
                                                                      atom['x'], atom['y'], atom['z']))
        f.write('{:>10.5f}{:>10.5f}{:>10.5f}\n'.format(*boxsize))
    print('Wrote filtered structure to {}.'.format(args['finalgro']))
