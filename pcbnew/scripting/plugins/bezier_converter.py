from __future__ import division

import scipy as sp
import pylab as plt
import math


def plotBezier(bez):

    #Setup the parameterisation
    t = sp.linspace(0,1,100)

    #Read in the origin & destination points
    POx,POy = bez[0][0], bez[0][1]
    P3x,P3y = bez[3][0], bez[3][1]

    #Add those to the axes
    ax.plot(POx,POy, 'ob')
    ax.plot(P3x,P3y, 'or')

    #Work out the control points
    P1x, P1y = bez[1][0], bez[1][1]
    P2x, P2y = bez[2][0], bez[2][1]

    #Plot the control points and their vectors
    ax.plot((P3x,P2x),(P3y,P2y), 'r')
    ax.plot((POx,P1x),(POy,P1y), 'b')
    ax.plot(P1x, P1y, 'ob')
    ax.plot(P2x, P2y, 'or')

    Bx, By = pointOnBezier(bez, t)

    #Plot the Bezier curve
    ax.plot(Bx, By, 'k')

def plotArc(c, r, ts):

    def _pointOnArc(c, r, theta):
        return c[0] + r * sp.cos(theta), c[1] + r * sp.sin(theta)

    #Setup the parameterisation
    t = sp.linspace(ts[0],ts[1],100)

    Bx, By = _pointOnArc(c,r, t)

    #Plot the Bezier curve
    ax.plot(Bx, By, 'r')

def pointOnBezier(bez, t):

    #Use the Bezier formula
    x = (1-t)**3*bez[0][0] + 3*(1-t)**2*t*bez[1][0] + 3*(1-t)*t**2*bez[2][0] + t**3*bez[3][0]
    y = (1-t)**3*bez[0][1] + 3*(1-t)**2*t*bez[1][1] + 3*(1-t)*t**2*bez[2][1] + t**3*bez[3][1]

    return x, y

def findInflections(bz):

    # coefficients from
    # http://www.caffeineowl.com/graphics/2d/vectorial/cubic-inflexion.html
    ax = bz[1][0] - bz[0][0]
    ay = bz[1][1] - bz[0][1]

    bx = bz[2][0] - bz[1][0] - ax
    by = bz[2][1] - bz[1][1] - ay

    cx = bz[3][0] - bz[2][0] - ax - 2*bx
    cy = bz[3][1] - bz[2][1] - ay - 2*by

    # now solve for t:
    # ax*by - ay*bx + t(ax*cy - ay*cx) + t^2(bx*cy - by*cx) = 0

    # quadratic coefficients of at^2 + bt + c = 0
    qa = bx * cy - by * cx
    qb = ax * cy - ay * cx
    qc = ax * by - ay * bx

    sol = solveQuadraticReal(qa,qb,qc)

    return [x for x in sol if x > 0 and x < 1]

def solveQuadraticReal(a,b,c):
    dis = b * b - 4 * a * c

    if a == 0 and b == 0:
        sol = []
    if a == 0:
        sol = [-c / b]
    elif dis == 0:
        sol = [-b / (2 * a)]
    elif dis < 0:
        sol = []
    else:
        sol = [(-b - math.sqrt(dis))/ (2 * a),
               (-b + math.sqrt(dis))/ (2 * a)]

    return sorted(sol)

def splitBezier(bez, t):
    """
    Split a bezier at t and return both halves
    """
    x1, y1 = bez[0]
    x2, y2 = bez[1]
    x3, y3 = bez[2]
    x4, y4 = bez[3]

    x12 = (x2 - x1) * t + x1
    y12 = (y2 - y1) * t + y1

    x23 = (x3 - x2) * t + x2
    y23 = (y3 - y2) * t + y2

    x34 = (x4 - x3) * t + x3
    y34 = (y4 - y3) * t + y3

    x123 = (x23 - x12) * t + x12
    y123 = (y23 - y12) * t + y12

    x234 = (x34 - x23) * t + x23
    y234 = (y34 - y23) * t + y23

    x1234 = (x234 - x123) * t + x123
    y1234 = (y234 - y123) * t + y123

    return [[(x1, y1), (x12, y12), (x123, y123), (x1234, y1234)],
            [(x1234,y1234),(x234,y234),(x34,y34),(x4,y4)]]

def splitBezierAtInflections(bez):

    infl = findInflections(bez)

    print infl

    if not len(infl):
        curves = [bez]
    else:
        curves = []
        b2 = bez

        for t in infl:
            b1, b2 = splitBezier(b2, t)
            curves.append(b1)

        curves.append(b2)

    return curves

def lineFromPoints(p1, p2):
    """
    Return line in form ax + by = c given two points on the line
    """
    a = p1[1] - p2[1]
    b = p2[0] - p1[0]
    c = p2[0] * p1[1] - p1[0] * p2[1]

    return a, b, c

def intersectionOfLines(l1, l2):

    det = l1[0] * l2[1] - l1[1] * l2[0]
    if det == 0:
        return None

    detx = l1[2] * l2[1] - l1[1] * l2[2]
    dety = l1[0] * l2[2] - l1[2] * l2[0]

    x = detx / det
    y = dety / det

    return x, y

def length(v):
    math.sqrt(p1[0]**2 + p1[1]**2)

def distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def difference(p1, p2):
    """
    Vector from p1 to p2 = p2 - p1
    """
    return p2[0] - p1[0], p2[1] - p1[1]

def dot(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]

def incentre(p1, p2, p3):

    a = distance(p2, p3)
    b = distance(p1, p3)
    c = distance(p1, p2)

    P = a + b + c

    x = (a * p1[0] + b * p2[0] + c * p3[0]) / P
    y = (a * p1[1] + b * p2[1] + c * p3[1]) / P

    return x, y


def circleFromThreePoints(p1, p2, p3):

    return c, r, ts, te

def biarcForBezier(bez):

    # from Riskus 2006, section 4

    # use the midpoint of the the bezier as and arc point
    # this is approximation strategy A1 in Riskus
    """
    l1 = lineFromPoints(bez[0], bez[1])
    l2 = lineFromPoints(bez[2], bez[3])

    V = intersectionOfLines(l1, l2)

    # biarc joining point
    G = incentre(bez[0], bez[3], V)

    ax.plot(G[0], G[1], '+g')

    biarcForPointsAndJoin(bez[0], bez[3], bez[1], bez[2], G)
    """

    # point on approximation arc at bezier midpoint
    M = pointOnBezier(bez, 0.5)

    ax.plot(M[0], M[1], '+g')

    c, r, t = circleFromThreePoints(bez[0], bez[3], M)

    plotArc(c,r,t)


def circleFromThreePoints(a, b, g):
    """
    Arc from a to b via g

    Returns centre, radius, a tuple of the start (clockwise end) and end (ACW end) angles in radians
    """

    x1 = (b[0] + a[0]) / 2
    y1 = (b[1] + a[1]) / 2

    dy1 = b[0] - a[0]
    dx1 = a[1] - b[1]

    x2 = (g[0] + b[0]) / 2
    y2 = (g[1] + b[1]) / 2

    dy2 = g[0] - b[0]
    dx2 = b[1] - g[1]


    cx = (y1 - y2) * dx1 * dx2 + x2 * dx1 * dy2 - x1 * dy1 * dx2
    cx = cx / (dx1 * dy2 - dy1 * dx2)

    cy = y1 + (cx - x1) * dy1 / dx1

    c = (cx, cy)

    r = distance(c, a)

    ca = difference(c, a)
    cb = difference(c, b)

    ta = math.atan2(ca[1], ca[0])
    tb = math.atan2(cb[1], cb[0])

    am = difference(a, g)
    ab = difference(a, b)


    #left perpendicular of ab
    abperp = (-ab[1], ab[0])

    print abperp, "am", am

    side = dot(abperp, am)

    print "side", side

    # work out which side the centre point is on, and therefore
    # which of a and b comes first
    if side > 0:
        t = [tb, ta]
    else:
        t = [ta, tb]

    # ensure the end angle is greater than the start
    if t[1] < t[0]:
        t[1] = t[1] + 2 * math.pi

    assert (t[0] < t[1])

    print t

    #print t
    return c, r, t


def normalise(p1, p2):
    """
    Normalise a vector from p1 to p2 to a vector of length 1 from the origin
    """

    l = distance(p1, p2)

    x = (p2[0] - p1[0]) / l
    y = (p2[1] - p1[1]) / l

    return x, y

def biarcForPointsAndJoin(p1, p2, t1, t2, g):
    """
    Biarc from p1 (tangent p1->t1) to p2 (tangent p2->t2), with the join at g
    """

    # normalise the tangent vectors
    t1 = normalise(p1, t1)
    t2 = normalise(p2, t2)

    # normal vectors
    n1 = (-t1[1], t1[0])
    n2 = (-t2[1], t2[0])

    s1x = ((g[0] - p1[0]) ** 2) / (2 * n1[0] * (g[0] - p1[0]))
    s1y = ((g[1] - p1[1]) ** 2) / (2 * n1[1] * (g[1] - p1[1]))

    c1x = p1[0] + n1[0] * s1x
    c1y = p1[1] + n1[1] * s1y

    s2x = ((g[0] - p2[0]) ** 2) / (2 * n2[0] * (g[0] - p2[0]))
    s2y = ((g[1] - p2[1]) ** 2) / (2 * n2[1] * (g[1] - p2[1]))

    print n1, n2

    c2x = p2[0] + n2[0] * s2x
    c2y = p2[1] + n2[1] * s2y

    ax.plot(c2x, c2y, 'ok')
    ax.plot(c1x, c1y, 'ok')

def approximateBezierByArcs(bez):

    curves = splitBezierAtInflections(b)

    for curve in curves:
        plotBezier(curve)

        biarcForBezier(curve)


#### Inputs

#bez = [[ [1,0], [0.6, -0.2], [0.4, 0.3], [0,0] ],
#        [ [0,1], [1.5, 4], [0.5, 4], [2,1] ]]

bez = [[(16.9753, 0.7421), (18.2203, 2.2238), (21.0939, 2.4017), (23.1643, 1.6148)],
        [(17.5415, 0.9003), (18.4778, 3.8448), (22.4037, -0.9109), (22.563, 0.7782)]]

### Workings

#Generate the figure
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_aspect(1)
ax.hold(True)


for b in bez:
    approximateBezierByArcs(b)


plt.show()
#Bosch.
