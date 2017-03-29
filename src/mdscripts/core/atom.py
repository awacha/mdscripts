class Atom(object):
    def __init__(self, index, name, x, y, z, atomtype, resid=0, resn='UNK', charge=0):
        self.index=index
        self.name=name
        self.x=x
        self.y=y
        self.z=z
        self.atomtype=atomtype
        self.resid=int(resid)
        self.resn=resn
        self.charge=float(charge)
        self.bonded_neighbours=[]
        self.chainid=0
        self.occupancy=1.0
        self.tempfactor=0.0
        self.element=atomtype

    def _neighbourroutes(self, steps=1, route=None):
        if route is None:
            #print('Initializing neighbourroutes for atom #{}, steps={}'.format(self.index, steps))
            route = ()
        if steps == 1:
            routes = [route + (self,n,) for n in self.bonded_neighbours]
            #print('Steps = 1 in atom #{}: returning routes:'.format(self.index))
            #for r in routes:
            #    print('  '+'->'.join([str(a.index) for a in r]))
            return routes
        else:
            routes = []
            for neighbourroutes in [n._neighbourroutes(steps-1, route=route+(self,)) for n in self.bonded_neighbours]:
                routes.extend(neighbourroutes)
            return routes

    def neighbours(self, steps=1):
        routes=self._neighbourroutes(steps)
        lis = []
        for r in routes:
            if len(set(r)) == steps+1:
                lis.append(r[-1])
        return lis

    def neighbours_of_type(self, atomtype, steps=1):
        return [a for a in self.neighbours(steps) if a.atomtype.startswith(atomtype)]

    def distance(self, atom):
        return ((self.x-atom.x)**2+(self.y-atom.y)**2+(self.z-atom.z)**2)**0.5

    @property
    def chainname(self):
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[self.chainid-1]
