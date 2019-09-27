import os
from typing import Optional


def backoff(filename:str) -> Optional[str]:
    """Create a backup from a file as the GROMACS programs do.

    E.g. if filename is "topol.top", the backup files will be named
    "#topol.top.<index>#", where <index> is an integer starting from 1.

    If the file exists, it renames it to the next available backup file name.

    If the file does not exist, it returns None
    """
    if not os.path.exists(filename):
        return None
    path, fname = os.path.split(filename)
    if not path:
        path = '.'
    backupfiles = [f for f in os.listdir(path) if f.startswith('#' + fname) and f.endswith('#')]
    if not backupfiles:
        maxnum = 0
    else:
        fileends = [f[1 + len(fname):-1] for f in backupfiles]

        def safe_int(x):
            try:
                return int(x)
            except ValueError:
                return None

        nums = [safe_int(f[1:]) for f in fileends if f.startswith('.')]
        maxnum = max([n for n in nums if n is not None])
    backedoff = os.path.join(path, '#' + filename + '.{:d}#'.format(maxnum + 1))
    os.rename(filename, backedoff)
    print('Back Off! I just backed up {} to {}'.format(filename, backedoff))
    return backedoff
