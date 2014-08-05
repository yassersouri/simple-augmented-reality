class Plane(object):
    def __init__(self, n, d):
        assert len(n) == 3
        self.n = n
        self.d = d
    
    @classmethod
    def plane_from_three_points(cls, a, b, c):
        pass
    
    def interset_line(self, line):
        def dot(a, b):
            return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
        
        t0 = (float(self.d) - dot(self.n, line.l0)) / dot(self.n, line.l)
        return line.at_t(t0)

class Line(object):
    def __init__(self, l0, l):
        assert len(l0) == 3
        assert len(l) == 3
        self.l0 = l0
        self.l = l
    
    def at_t(self, t):
        def scale(a, s):
            return [a1 * s for a1 in a]
        
        def add(a, b):
            return [a1 + b1 for (a1, b1) in zip(a, b)]
        
        return add(self.l0, scale(self.l, t))