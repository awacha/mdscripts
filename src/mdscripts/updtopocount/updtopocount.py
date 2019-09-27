#!/usr/bin/env python3

"""Update the molecule count in the [ system ] section of a gromacs topology, based on the actual number of atoms
in a .gro file."""
import argparse
import os
import re
from typing import Sequence, Tuple

from ..io.backoff import backoff
from ..io.cpreprocessorparser import CPreprocessorParser
from ..io.gro import GROFile


class TopologyParser:
    moleculetypes = {}

    def __init__(self, topologyfile, defines, includedirs):
        self.topologyfile = topologyfile
        self.defines = defines
        self.includedirs = includedirs

    def parse(self):
        parser = CPreprocessorParser(self.topologyfile, self.includedirs, self.defines, handle_ifdefs=True, substitute_macros=True)
        currentsection = None
        currentmoleculetype = None
        for line, filename, lineno in parser:
            l=line.split(';',1)[0].strip()
            if not l: continue # empty line or pure comment
            if l.startswith('[') and l.endswith(']'):
                section = l[1:-1].strip()
                if section == 'moleculetype':
                    currentmoleculetype = None
                currentsection = section
            elif currentsection == 'moleculetype':
                assert currentmoleculetype is None
                currentmoleculetype = l.split()[0].strip()
                self.moleculetypes[currentmoleculetype]=[]
            elif currentsection == 'atoms':
                try:
                    i, atomtype, resnr, resname, atname, cgroup, charge, *mass= l.split()
                    mass = None if not mass else float(mass[0])
                except ValueError:
                    print(line, filename, lineno)
                    raise
                self.moleculetypes[currentmoleculetype].append([int(i), atomtype, int(resnr), resname, atname, int(cgroup), float(charge), mass])
            else:
                pass

    def matchgrofile(self, filename:str):
        gro = GROFile.load(filename)
        sequencetobematched = list(zip([n.decode('utf-8') for n in gro.grodata['name']], [n.decode('utf-8') for n in gro.grodata['resn']]))
        patterns = {k:[(name, resname) for i, atomtype, resnr, resname, name, cgroup, charge, mass in v] for k,v in self.moleculetypes.items()}
        #print('Patterns:')
        #for p in patterns:
        #    print(p, len(p), patterns[p])
        matches = []
        matcheduntil=0
        while matcheduntil<len(sequencetobematched):
            # make a dictionary which maps the names of the patterns to the maximum count contiguous matches in the
            # sequence starting from the present point.
            matching = {p:self.doesmatch(patterns[p], sequencetobematched[matcheduntil:]) for p in patterns}
            longestmatchingpattern = sorted([(p,len(patterns[p])) for p in matching if matching[p]>0], key=lambda pl:pl[1])[-1][0]
            mostmatchingpattern = sorted([(p, matching[p]) for p in matching], key=lambda pl:pl[1])[-1][0]
            if matching[mostmatchingpattern]==0:
                raise ValueError('Coordinate file matched until atom {}. Cannot find matching moleculetype for the following part!'.format(matcheduntil))
            if longestmatchingpattern != mostmatchingpattern:
                raise ValueError('The longest moleculetype which matches the atom sequence is not the same as the moleculetype with the largest match count at atom {}.'.format(longestmatchingpattern, mostmatchingpattern, matcheduntil))
            matches.append((longestmatchingpattern, matching[longestmatchingpattern]))
            matcheduntil+=len(patterns[longestmatchingpattern])*matching[longestmatchingpattern]
            print('Matched: {} x {} (ready until atom #{})'.format(longestmatchingpattern, matching[longestmatchingpattern], matcheduntil+1))
        return matches

    @staticmethod
    def doesmatch(pattern:Sequence[Tuple[str,str]], sequence:Sequence[Tuple[str, str]]) -> int:
        if len(sequence)<len(pattern):
            return False
        #print('Trying pattern to sequence:')
#        for i in range(len(pattern)):
#            if sequence[i]!=pattern[i]:
#                break
        #print('First not matching index: {}'.format(i))
        i = 0
        nmatching=0
        while all([x==y for x,y in zip(sequence[nmatching*len(pattern):(nmatching+1)*len(pattern)],pattern)]) and nmatching*len(pattern)<len(sequence):
            nmatching +=1
        return nmatching



def main():
    argparser = argparse.ArgumentParser(
        description='Update the molecule count in the [ system ] section of a GROMACS topology, based on the actual number of atoms/residues in a .gro file.')
    argparser.add_argument('-p', action='store', default='topol.top', type=str, required=True,
                           help='Input topology file', dest='topologyin')
    argparser.add_argument('-c', action='store', default='conf.gro', type=str, required=True, help='Coordinate file',
                           dest='coordfile')
    argparser.add_argument('-o', action='store', default='topol.top', type=str, required=True,
                           help='Output topology file', dest='topologyout')
    argparser.add_argument('--nobackup', action='store_false', required=False,
                           help='Do not make backups of the output files', dest='backup')
    argparser.add_argument('-D', action='append', type=str, required=False,
                           help='Preprocessor #define. Can be specified multiple times. In contrast to GCC, leave a space between -D and the name!',
                           dest='defines')

    parsed = argparser.parse_args()

    if os.path.exists(parsed.topologyout) and os.path.exists(parsed.topologyin):
        if os.path.samefile(parsed.topologyin, parsed.topologyout):
            print('Input and output topology must not be the same file!')
            print(argparser.format_usage())
            return 1

    if parsed.backup:
        backoff(parsed.topologyout)

    parser = TopologyParser(parsed.topologyin, parsed.defines, [], ) # ToDo includedirs
    parser.parse()
    for mt in parser.moleculetypes:
        print(mt, len(parser.moleculetypes[mt]), 'atoms')
    molecules = parser.matchgrofile(parsed.coordfile)
    with open(parsed.topologyin, 'rt') as fin:
        with open(parsed.topologyout, 'wt') as fout:
            we_are_in_the_molecules_section=False
            for line in fin:
                if re.match('^\s*\[\s*molecules\s*\]', line):
                    we_are_in_the_molecules_section = True
                    fout.write(line)
                    for m, num in molecules:
                        fout.write('{:<10s} {:<5d}\n'.format(m, num))
                    fout.write('\n')
                elif re.match('^\s*\[.*\]', line):
                    we_are_in_the_molecules_section = False
                if not we_are_in_the_molecules_section:
                    fout.write(line)
