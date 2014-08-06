from math import sqrt
import numpy as np
""" Helper functions """


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def scale(a, s):
    return [a1 * s for a1 in a]


def add(a, b):
    return [a1 + b1 for (a1, b1) in zip(a, b)]


def sub(a, b):
    return [a1 - b1 for (a1, b1) in zip(a, b)]


def normalize(l):
    l_norm = sqrt(l[0] ** 2 + l[1] ** 2 + l[2] ** 2)
    if l_norm == 0:
        return [0, 0, 0]
    return [l1/l_norm for l1 in l]


def cross(a, b):
    c1 = a[1] * b[2] - a[2] * b[1]
    c2 = a[0] * b[2] - a[2] * b[0]
    c3 = a[0] * b[1] - a[1] * b[0]

    return [c1, c2, c3]


""" actual classes """


class Plane(object):
    def __init__(self, n, d):
        assert len(n) == 3
        self.n = n
        self.d = d

    @classmethod
    def plane_normal_from_three_points(cls, a, b, c):
        A = b - a
        B = c - a
        n_prime = np.cross(A, B)
        return normalize(n_prime)
        

    def interset_line(self, line):
        if dot(self.n, line.l) == 0:
            raise Exception("Line does not intersets with plane")
        t0 = (float(self.d) - dot(self.n, line.l0)) / dot(self.n, line.l)
        return line.at_t(t0)


class Line(object):
    def __init__(self, l0, l):
        assert len(l0) == 3
        assert len(l) == 3
        self.l0 = l0
        self.l = l

    def at_t(self, t):
        return add(self.l0, scale(self.l, t))
