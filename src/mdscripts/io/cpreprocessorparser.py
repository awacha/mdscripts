import os
import re
import warnings
from typing import List, Tuple, Optional

from .backoff import backoff


class CPreprocessorParser:
    """This class is an iterator for parsing files with C-style preprocessor directives. As the main intention of this
    is to enable parsing of GROMACS topologies and force fields, we only support the following directives:

    1. Conditionals:
        #ifdef <name> [optional comment, ignored]
        #ifndef <name> [optional comment, ignored]
        #else [optional comment, ignored]
        #endif [optional comment, ignored]

    2. Errors and warnings
        #error <error message>
        #warning <warning message>

    3. Macro definitions
        #define <name> [<remaining part of the line>]
        #undef <name> [optional comment, ignored]

    4. File inclusions (difference between the two versions is the same as in ANSI C)
        #include "includefilepath" [optional comment, ignored]
        #include <includefilepath> [optional comment, ignored]

    Typical usage:

    >>> for line, filename, lineno in CPreprocessorParser("<initial filename>"):
        ...

    will iterate over all lines in the given file and all other files #included.

    Notes:
        Handling of conditionals can be switched off. In this case all #ifdef directives will
        appear in the lines yielded by the iterator, as well as all lines which would be ignored.
        Note that in the handling of macro definition directives the conditionals will still be obeyed.

        Macro definition directives are always output by the iterator.

        Macro substitution can also be switched off.

        If the handling of conditionals is on, #include directives are only checked if they appear inside
        an "enabled" block. If off, all #include directives are checked and handled. The included file will be
        iterated first, then the lines of the present file will continue. I.e. the #include directive won't appear
        among the returned lines in any case.

        #error and #warning directives will only be checked if they appear inside an "enabled" block and conditional
        handling is on.
    """

    _currentfilename:str
    """The name of the file being read"""

    _defines:List[Tuple[str, str]]
    """Defined macros and their contents"""

    _ifdefs:List[Tuple[str, bool]]
    """Active ifdef clauses """

    _includedirs:List[str]
    """Include directories"""

    _handle_ifdefs:bool=True
    """If #ifdef clauses are to be handled"""

    _substitute_macros:bool=True
    """If #define-d macros are to be substituted"""

    def __init__(self, filename:str, includedirs:Optional[List[str]]=None, defines:Optional[List[Tuple[str,str]]]=None,
                 handle_ifdefs:bool=True, substitute_macros:bool=True):
        self._handle_ifdefs = handle_ifdefs
        self._defines = defines if defines is not None else []
        self._includedirs = includedirs if includedirs is not None else []
        self._currentfilename = filename
        self._substitute_macros = substitute_macros
        self._ifdefs = []

    def defined(self, label:str) -> bool:
        return bool([l for l,v in self._defines if l==label])

    def _ifdefsAllowReading(self) -> bool:
        """Check if all the currently active #ifdef/#ifndef clauses are satisfied"""
        for label, expected in self._ifdefs:
            if (expected and (not self.defined(label))) or ((not expected) and (self.defined(label))):
                # either #ifdef but label is not defined, or #ifndef but label is defined.
                return False
            # otherwise go on.
        # if we reach here, all #ifdef / #ifndef clauses were satisfied
        return True


    def __iter__(self):
        with open(self._currentfilename, 'rt') as f:
            for lineno, line in enumerate(f, start=1):
                # strip leading whitespace from the line
                l = line.strip()
                # note that conditional directives are always checked and honored. This is needed for the correct
                # handling of macro definition and error/warning directives. Also, #include directives are only
                # followed if the enclosing #ifdef clauses allow to. When the user opts to disregard preprocessor
                # conditionals, they are output.

                # first check if we have an empty line. If yes, print it out if needed

                if not l:
                    if (self._ifdefsAllowReading()) or (not self._handle_ifdefs):
                        yield line, self._currentfilename, lineno
                    continue
                assert len(l)>0
                # The next hierarchy of "if"s handles the preprocessor logic.
                if l.split()[0]=='#ifdef':
                    label = l.split()[1]
                    self._ifdefs.append((label, True))
                elif l.split()[0]=='#ifndef':
                    label = l.split()[1]
                    self._ifdefs.append((label, False))
                elif l.split()[0]=='#endif':
                    self._ifdefs.pop()
                elif l.split()[0]=='#else':
                    self._ifdefs[-1]=(self._ifdefs[-1][0], not self._ifdefs[-1][1])
                elif l.split()[0]=='#define':
                    if self._ifdefsAllowReading():
                        # handle the #define directive
                        directive, label, *value = l.split(None, 2)
                        assert directive=='#define'
                        value = value[0] if value else ''
                        self._defines.append((label, value))
                elif l.split()[0]=='#undef':
                    if self._ifdefsAllowReading():
                        directive, label, *comments = l.split(None, 2)
                        assert directive == '#undef'
                        self._defines = [(l, v) for l,v in self._defines if l!=label]
                elif l.split()[0]=='#error':
                    if self._ifdefsAllowReading():
                        raise RuntimeError('#error directive encountered in file {} on line {}. Message: {}'.format(self._currentfilename, lineno, l.split(None, 1)[1]))
                elif l.split()[0] == '#warning':
                    if self._ifdefsAllowReading():
                        warnings.warn('#warning directive encountered in file {} on line {}. Message: {}'.format(
                            self._currentfilename, lineno, l.split(None, 1)[1]), RuntimeWarning)
                elif l.split()[0]=='#include':
                    if (self._ifdefsAllowReading() or (not self._handle_ifdefs)):
                        # follow the #include directive if we are in an "enabled" block or we do not handle the conditionals.
                        # Apply de Morgan's law to the above: do not follow the #include directive if we are in a "disabled"
                        # block and handle the conditionals. In all other cases follow it.
                        includefile = None
                        m = re.match(r'^#include\s+"(?P<includefile>[^"]+)"', l)
                        if m is not None:
                            # find the include file, first try to test in the current directory
                            includefile = self._findIncludeFile(m['includefile'], in_current_folder=True)
                        m = re.match(r'^#include\s+<(?P<includefile>[^>]+)>', l)
                        if m is not None:
                            # find the include file, do not check the current directory
                            includefile = self._findIncludeFile(m['includefile'], in_current_folder=False)
                        if not includefile:
                            raise ValueError('Invalid #include directive {} on line {} in file {}'.format(l, lineno, self._currentfilename))
                        # create a new parser for the include file
                        nextreader = CPreprocessorParser(includefile, self._includedirs, self._defines, self._handle_ifdefs, self._substitute_macros)
                        nextreader._ifdefs = self._ifdefs
                        for line, filename, lineno in nextreader:
                            # whenever we get a line from the reader, update the global state: _defines, _ifdefs
                            self._defines = nextreader._defines
                            self._ifdefs = nextreader._ifdefs
                            yield line, filename, lineno
                elif l.split()[0].startswith('#'):
                    raise RuntimeError('Unknown preprocessor directive {} encountered on line {} in file {}'.format(l.split()[0], lineno, self._currentfilename))

                if l.split()[0] in ['#ifdef', '#ifndef', '#else', '#endif', '#define', '#undef', '#error', '#warning']:
                    if not self._handle_ifdefs:
                        # we have to output the conditional directives, the error/warning directives and the macro
                        # definition directives intact.
                        yield line, self._currentfilename, lineno
                    # otherwise we do not write them.
                elif l.split()[0] in ['#include']:
                    pass # never write #include directives
                elif l.startswith('#'):
                    raise RuntimeError('Unknown preprocessor directive {} encountered on line {} in file {}'.format(l.split()[0], lineno, self._currentfilename))
                elif self._ifdefsAllowReading() or (not self._handle_ifdefs):
                    yield self._substituteMacros(line), self._currentfilename, lineno
                else:
                    # do nothing
                    pass

    def _substituteMacros(self, line:str) -> str:
        if not self._substitute_macros:
            return line
        for macro, value in self._defines:
            line=line.replace(macro, value)
        return line


    def _findIncludeFile(self, includefilename:str, in_current_folder:bool) -> str:
        includedirs = self._includedirs
        if in_current_folder:
            # watch out, "current folder" is not equal to os.getcwd(). Instead, it is the path where file being read
            # resides.

            # does not matter if we have an absolute path or a relative path or just a bare filename. The first
            # part will be the directory where the file resides or ''.
            currentfolder = os.path.split(self._currentfilename)[0]
            includedirs = [currentfolder] + includedirs
        for path in includedirs:
            if os.path.exists(os.path.join(path, includefilename)):
                return os.path.join(path, includefilename)
        raise FileNotFoundError(includefilename)

def topologypreprocessor():
    import argparse

    argparser = argparse.ArgumentParser(
        description='Preprocess a topology file')
    argparser.add_argument('-p', action='store', default='topol.top', type=str, required=True,
                           help='Input topology file', dest='topologyin')
    argparser.add_argument('-o', action='store', default='topol.top', type=str, required=True,
                           help='Output topology file', dest='topologyout')
    argparser.add_argument('--nobackup', action='store_false', required=False,
                           help='Do not make backups of the output files', dest='backup')
    argparser.add_argument('-D', action='append', type=str, required=False,
                           help='Preprocessor #define. Can be specified multiple times. In contrast to GCC, leave a space between -D and the name!',
                           dest='defines')
    argparser.add_argument('-I', action='append', type=str, required=False,
                           help='Include directory. Can be specified multiple times. In contrast to GCC, leave a space between -I and the name!',
                           dest='includedirs')
    argparser.add_argument('--nosubstitute', action='store_false', required=False,
                           help='Do not substitute macros', dest='macro_substitution')
    argparser.add_argument('--noconditionals', action='store_false', required=False,
                           help='Do not follow #ifdefs', dest='ifdefs')

    parsed = argparser.parse_args()
    parser = CPreprocessorParser(parsed.topologyin, parsed.includedirs, parsed.defines, parsed.ifdefs, parsed.macro_substitution)
    if os.path.exists(parsed.topologyout) and os.path.exists(parsed.topologyin):
        if os.path.samefile(parsed.topologyin, parsed.topologyout):
            print('Input and output topology must not be the same file!')
            print(argparser.format_usage())
            return 1

    if parsed.backup:
        backoff(parsed.topologyout)

    with open(parsed.topologyout, 'wt') as f:
        for line, filename, lineno in parser:
            f.write(line)
    return 0

