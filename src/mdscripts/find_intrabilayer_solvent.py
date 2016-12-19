import argparse
import sys

import numpy as np

from .insertprotein import adjust_topology
from .io.backoff import backoff
from .io.gro import GROFile


def getheadlayers(grofile: GROFile, lipidname, atomtype=b'P8'):
    zP = grofile.filter_resn(lipidname).filter_atomname(atomtype).z()
    lower = zP[zP < np.median(zP)].mean()
    upper = zP[zP > np.median(zP)].mean()
    return lower, upper


def interlayersolvents(grofile: GROFile, lipidname, solventname, headgroup_atomtype=b'P8'):
    lower, upper = getheadlayers(grofile, lipidname, headgroup_atomtype)
    solvents = grofile.filter_resn(solventname)
    badatomidx = (solvents.z() >= lower) & (solvents.z() <= upper)
    return solvents.filter_boolflags(solvents.extend_boolflags_to_residues(badatomidx)), lower, upper


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
    gro = GROFile.new_from_file(args['inputfile'])
    print('Loaded {:d} atoms from file {}.'.format(len(gro), args['inputfile']))
    badsolvents, lower, upper = interlayersolvents(gro, args['lipidname'], args['solventname'], args['atomtype'])
    print('Lower and upper mean z coordinates of the head group layer: {} and {}'.format(lower, upper))
    badsolventresidues = badsolvents.resids()
    print('Found {} misplaced solvent molecules:'.format(len(badsolventresidues)))
    print('  ', ', '.join('{:d}{}'.format(b, args['solventname']) for b in sorted(badsolventresidues)))

    print('Original number of atoms:', len(gro))
    print('Number of bad atoms:', len(badsolvents))
    goodgro = gro - badsolvents
    print('Number of atoms kept:', len(goodgro))
    print('Number of removed {} molecules: {}'.format(args['solventname'], len(badsolventresidues)))
    ngoodsolventresidues = len((goodgro.filter_resn(args['solventname']) - badsolvents).resids())
    print('Remaining {} molecules: {}'.format(
        args['solventname'], ngoodsolventresidues))
    backoff(args['finalgro'])
    goodgro.write(args['finalgro'])
    print('Wrote filtered structure to {}.'.format(args['finalgro']))
    if args['topology'] is not None:
        adjust_topology(backoff(args['topology']), args['topology'], args['solventname'], ngoodsolventresidues)
        print('Wrote adjusted topology in {}.'.format(args['topology']))
