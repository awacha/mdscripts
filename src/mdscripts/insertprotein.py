#!/usr/bin/env python

import argparse
import os
import re
import subprocess
import sys


def get_areaperlipid(areafile):
    with open(areafile, 'rt', encoding='utf-8') as f:
        total, upperleaflet, lowerleaflet = f.readline().split()
    return float(total), float(upperleaflet), float(lowerleaflet)


def shrink(inputfile, shrinkfactor, lipidname, searchcutoff, shrunkfile, gridspacing, areafile):
    result = subprocess.run(
        ['perl', 'inflategro.pl', inputfile, str(shrinkfactor), lipidname, str(searchcutoff), shrunkfile,
         str(gridspacing), areafile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def inflate(inputfile, inflatedfile, inflategro, inflationfactor, lipidname, searchcutoff, gridspacing,
            areafile='areaperlipid.dat'):
    result = subprocess.run(
        ['perl', inflategro, inputfile, str(inflationfactor), lipidname, str(searchcutoff), inflatedfile,
         str(gridspacing), areafile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        print(result.stdout)
        print(result.stderr)
        raise
    return get_areaperlipid(areafile)


def find_lipid_indices(inputfile, lipidname):
    """Find the lipid indices in the .gro file"""
    with open(inputfile, 'rt', encoding='utf-8') as f:
        matches = [re.match('\s*(?P<index>\d+)%s\s+' % lipidname, l) for l
                   in f]
    indices = {int(m.group('index')) for m in matches if m is not None}
    return indices


def adjust_topology(topology, newtopology, lipidname, number):
    """Adjust the topology to have the correct number of lipids"""
    with open(topology, 'rt', encoding='utf-8') as topin:
        with open(newtopology, 'wt', encoding='utf-8') as topout:
            molecules_seen = False
            while topin:
                l = topin.readline()
                if not l:
                    break
                if re.match('\s*\[\s*molecules\s*\]', l):
                    molecules_seen = True
                elif re.match('\s*\[\s*', l):
                    molecules_seen = False
                if re.match('\s*%s\s+' % lipidname, l) and molecules_seen:
                    topout.write('{}        {:d}\n'.format(lipidname, number))
                else:
                    topout.write(l)


def run():
    parser = argparse.ArgumentParser(description="Insert a protein by using InflateGRO")
    parser.add_argument('-i', action='store', dest='inflationfactor', type=float, help='Inflation factor', default=4)
    parser.add_argument('-d', action='store', dest='shrinkfactor', type=float, help='Shrinking factor', default=0.95)
    parser.add_argument('-l', action='store', dest='lipidname', type=str, help='Lipid name')
    parser.add_argument('-f', action='store', dest='inputfile', type=str, help='Input .gro file')
    parser.add_argument('-c', action='store', dest='searchcutoff', type=float, help='Search cutoff (Ångström)',
                        default=14)
    parser.add_argument('-g', action='store', dest='gridspacing', type=float, help='Grid spacing (Ångström)', default=5)
    parser.add_argument('-t', action='store', dest='topology', type=str, help='Topology  file (.top)',
                        default='topol.top')
    parser.add_argument('-m', action='store', dest='mdpfile', type=str, help='.mdp file for energy minimization',
                        default='minim.mdp')
    parser.add_argument('-o', action='store', dest='finalgro', type=str, help='The output .gro file',
                        default='confout.gro')
    parser.add_argument('--inflategro', action='store', dest='inflategro', type=str,
                        help='path to the inflategro.pl script',
                        default='inflategro.pl')
    # parser.add_help()
    args = vars(parser.parse_args())
    print(args)
    if (args['lipidname'] is None) or (args['inputfile'] is None):
        parser.print_help()
        sys.exit(1)
    # inflate the lipids
    indices_pre = find_lipid_indices(args['inputfile'], args['lipidname'])
    inflatedfile = os.path.splitext(args['inputfile'])[0] + '_inflated.gro'
    # do a dummy inflation just to calculate the area per lipid
    areaperlipid = []
    areaperlipid.append(inflate(args['inputfile'], os.devnull, args['inflategro'], 1.0, args['lipidname'],
                                args['searchcutoff'], args['gridspacing']))
    # now inflate for real.
    areaperlipid.append(
        inflate(args['inputfile'], inflatedfile, args['inflategro'], args['inflationfactor'], args['lipidname'],
                args['searchcutoff'], args['gridspacing']))
    indices = find_lipid_indices(inflatedfile, args['lipidname'])
    indices_removed = [i for i in indices_pre if i not in indices]
    print('{:d} lipids removed during inflation:'.format(len(indices_removed)),
          ', '.join(str(i) for i in indices_removed))
    # update the topology
    topology = os.path.splitext(args['topology'])[0] + '_shrink0.top'
    adjust_topology(args['topology'], topology, args['lipidname'], len(indices))
    # do the enegy minimization
    minimize(inflatedfile, args['mdpfile'], topology)  # -> confout.gro
    i = 0
    while areaperlipid[-1][0] > areaperlipid[0][0]:
        i += 1
        print('Shrinking step #{:d}'.format(i))
        # shrink the structure
        indices_pre = indices
        shrunkfile = os.path.splitext(args['inputfile'])[0] + '_shrunk.gro'.format(i)
        areaperlipid.append(
            inflate('confout.gro', shrunkfile, args['inflategro'], args['shrinkfactor'], args['lipidname'],
                    0, args['gridspacing'])
        )
        print('Area per lipid: {:f}'.format(areaperlipid[-1][0]))
        indices = find_lipid_indices(shrunkfile, args['lipidname'])
        indices_removed = [j for j in indices_pre if not j in indices]
        print('{:d} lipids removed: {}'.format(len(indices_removed), ', '.join(str(x) for x in indices_removed)))
        topology = os.path.splitext(args['topology'])[0] + '_shrink.top'.format(i)
        adjust_topology(args['topology'], topology, args['lipidname'], len(indices))
        minimize(shrunkfile, args['mdpfile'], topology)
    print('Shrinking done. Area per lipid history:')
    for apl in areaperlipid:
        print('{}\t{}\t{}'.format(*apl))
    finaltop = os.path.splitext(args['topology'])[0] + '_insertprotein.top'
    if args['finalgro'] != 'confout.gro':
        os.rename('confout.gro', args['finalgro'])
    adjust_topology(args['topology'], finaltop, args['lipidname'], len(indices))
    os.rename(finaltop, args['topology'])
    print('You can find the final structure in {}. The topology file {} has been adjusted'.format(args['finalgro'],
                                                                                                  args['topology']))


def minimize(grofile, mdpfile, topology, tprfile='shrinking.tpr'):
    print('Minimizing...')
    result = subprocess.run(['gmx', 'grompp', '-c', grofile, '-f', mdpfile, '-p', topology, '-o', tprfile],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        # print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        #        print(*(result.stdout.split('\n')))
        #        print(*(result.stderr.split('\n')))
        raise
    result = subprocess.run(['gmx', 'mdrun', '-s', tprfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        result.check_returncode()
    except subprocess.CalledProcessError:
        # print(result.stdout.decode('utf-8'))
        print(result.stderr.decode('utf-8'))
        raise
