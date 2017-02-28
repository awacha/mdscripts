import mdtraj
import numpy as np


def gmx_saxs(q, trajectory, topology):
    intensity = np.zeros_like(q)
    for chunk in mdtraj.iterload(trajectory, top=topology):
        for c in chunk:
            c1 = c.remove_solvent()
            for i in range(c1.n_atoms):
                rhoi = c1.topology.atom(i).element[0]
                for j in range(i, c1.n_atoms):
                    intensity += rhoi ** 2
                    dist = np.sum((c1.xyz[0, i, :] - c1.xyz[0, j, :]) ** 2) ** 0.5
                    intensity += 2 * rhoi * c1.topology.atom(j).element[0] * np.sin(dist * q) / (dist * q)
    return intensity


q = np.linspace(0.01, 100, 300)
trajectory = '/home/wachaandras/gromacs/cm15_folding/helix_unfold_gromos/analysis/cm15_unfold_gromos_nopbc.xtc'
topology = '/home/wachaandras/gromacs/cm15_folding/helix_unfold_gromos/production/cm15_npt.gro'
# I=gmx_saxs(q,trj,top)


intensity = np.zeros_like(q)
idx = 0
maxidx = 30
for chunk in mdtraj.iterload(trajectory, top=topology):
    if idx > maxidx:
        break
    for c in chunk:
        if idx > maxidx:
            break
        idx += 1
        print(idx)
        c1 = c.remove_solvent()
        for i in range(c1.n_atoms):
            rhoi = c1.topology.atom(i).element.number
            intensity += rhoi ** 2
            for j in range(i + 1, c1.n_atoms):
                dist = np.sum((c1.xyz[0, i, :] - c1.xyz[0, j, :]) ** 2) ** 0.5
                intensity += 2 * rhoi * c1.topology.atom(j).element.number * np.sin(dist * q) / (dist * q)
