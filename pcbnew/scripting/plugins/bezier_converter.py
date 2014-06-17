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

math.pi2 = math.pi/2
straight_tolerance = 0.0001
straight_distance_tolerance = 0.0001
min_arc_radius = 0.1
EMC_TOLERANCE_EQUAL = 0.00001
biarc_max_split_depth = 4
biarc_tolerance = 0.1

def between(c,x,y):
    return x-straight_tolerance<=c<=y+straight_tolerance or y-straight_tolerance<=c<=x+straight_tolerance

################################################################################
###     Point (x,y) operations
################################################################################
class P:
    def __init__(self, x, y=None):
        if y is not None:
            self.x, self.y = float(x), float(y)
        else:
            self.x, self.y = float(x[0]), float(x[1])

    def __add__(self, other):
        return P(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return P(self.x - other.x, self.y - other.y)

    def __neg__(self):
        return P(-self.x, -self.y)

    def __mul__(self, other):
        if isinstance(other, P):
            return self.x * other.x + self.y * other.y
        return P(self.x * other, self.y * other)

    __rmul__ = __mul__

    def __truediv__(self, other):
        return P(self.x / other, self.y / other)

    def mag(self):
        return math.hypot(self.x, self.y)

    def unit(self):
        h = self.mag()
        if h:
            return self / h
        else:
            return P(0,0)

    def dot(self, other):
        return self.x * other.x + self.y * other.y
    def rot(self, theta):
        c = math.cos(theta)
        s = math.sin(theta)
        return P(self.x * c - self.y * s,  self.x * s + self.y * c)

    def angle(self):
        return math.atan2(self.y, self.x)

    def __repr__(self):
        return '%f,%f' % (self.x, self.y)

    def ccw(self):
        return P(-self.y,self.x)

    def l2(self):
        return self.x*self.x + self.y*self.y

def csp_at_t(bez,t):
    ax,bx,cx,dx = bez[0][0], bez[1][0], bez[2][0], bez[3][0]
    ay,by,cy,dy = bez[0][1], bez[1][1], bez[2][1], bez[3][1]

    x1, y1 = ax+(bx-ax)*t, ay+(by-ay)*t
    x2, y2 = bx+(cx-bx)*t, by+(cy-by)*t
    x3, y3 = cx+(dx-cx)*t, cy+(dy-cy)*t

    x4,y4 = x1+(x2-x1)*t, y1+(y2-y1)*t
    x5,y5 = x2+(x3-x2)*t, y2+(y3-y2)*t

    x,y = x4+(x5-x4)*t, y4+(y5-y4)*t
    return [x,y]

def point_to_arc_distance(p, arc):
    """
    Distance calculation from point to arc
    """
    P0,P2,c,a = arc
    dist = None
    p = P(p)
    r = (P0 - c).mag()

    if r > 0:
        i = c + (p - c).unit() * r
        alpha = ((i-c).angle() - (P0-c).angle())
        if a*alpha<0:
            if alpha>0:
                alpha = alpha-math.pi2
            else:
                alpha = math.pi2+alpha
        if between(alpha,0,a) or min(abs(alpha),abs(alpha-a))<straight_tolerance:
            return (p-i).mag(), [i.x, i.y]
        else:
            d1, d2 = (p-P0).mag(), (p-P2).mag()
            if d1<d2 :
                return (d1, [P0.x,P0.y])
            else :
                return (d2, [P2.x,P2.y])

def csp_to_arc_distance(bez, arc1, arc2, tolerance = 0.01 ): # arc = [start,end,center,alpha]
    n, i = 10, 0
    d, d1, dl = (0,(0,0)), (0,(0,0)), 0

    while i<1 or (abs(d1[0]-dl[0])>tolerance and i<4):
        i += 1
        dl = d1*1
        for j in range(n+1):
            t = float(j)/n
            p = csp_at_t(bez,t)
            d = min(point_to_arc_distance(p,arc1), point_to_arc_distance(p,arc2))
            d1 = max(d1,d)
        n=n*2
    return d1[0]

################################################################################
###
###     Biarc function
###
###     Calculates biarc approximation of cubic super path segment
###     splits segment if needed or approximates it with straight line
###
################################################################################
def biarc(bez, depth=0):

    def line_approx(bez):
        return [ [bez[0], bez[1], 'line'] ]

    def biarc_split(bez, depth):

        if depth >= biarc_max_split_depth:
            return line_approx(bez)

        bez1, bez2 = splitBezier(bez, t=0.5)

        return biarc(bez1, depth+1) + biarc(bez2, depth+1)

    P0 = P(bez[0])
    P4 = P(bez[3])

    TS = (P(bez[1]) - P0)
    TE = -(P(bez[2]) - P4)
    v = P0 - P4

    tsa = TS.angle()
    tea = TE.angle()
    va = v.angle()

    if TE.mag() < straight_distance_tolerance and TS.mag() < straight_distance_tolerance:
        # Both tangents are zero - line straight
        return line_approx(bez)

    if TE.mag() < straight_distance_tolerance:
        TE = -(TS + v).unit()
        r = TS.mag() / v.mag()*2
    elif TS.mag() < straight_distance_tolerance:
        TS = -(TE + v).unit()
        r = 1 / ( TE.mag() / v.mag()*2 )
    else:
        r=TS.mag()/TE.mag()

    TS = TS.unit()
    TE = TE.unit()

    tang_are_parallel = ((tsa - tea) % math.pi<straight_tolerance
                            or math.pi-(tsa-tea)%math.pi<straight_tolerance)

    if ( tang_are_parallel and
                ((v.mag()<straight_distance_tolerance or TE.mag()<straight_distance_tolerance or TS.mag()<straight_distance_tolerance) or
                    1-abs(TS*v/(TS.mag()*v.mag()))<straight_tolerance)  ):
                # Both tangents are parallel and start and end are the same - line straight
                # or one of tangents still smaller then tollerance

                # Both tangents and v are parallel - line straight
        return line_approx(bez)

    c,b,a = v*v, 2*v*(r*TS+TE), 2*r*(TS*TE-1)

    if v.mag() == 0:
        return biarc_split(bez, depth)

    asmall = abs(a) < 10**-10
    bsmall = abs(b) < 10**-10
    csmall = abs(c) < 10**-10

    if asmall and b!=0:
        beta = -c/b
    elif csmall and a!=0:
        beta = -b/a
    elif not asmall:
        discr = b*b-4*a*c
        if discr < 0:
            raise ValueError, (a,b,c,discr)
        disq = discr**.5
        beta1 = (-b - disq) / 2 / a
        beta2 = (-b + disq) / 2 / a
        if beta1*beta2 > 0 :
            raise ValueError, (a,b,c,disq,beta1,beta2)
        beta = max(beta1, beta2)
    elif asmall and bsmall:
        return biarc_split(bez, depth)

    alpha = beta * r
    ab = alpha + beta
    P1 = P0 + alpha * TS
    P3 = P4 - beta * TE
    P2 = (beta / ab) * P1 + (alpha / ab) * P3


    def calculate_arc_params(P0,P1,P2):
        D = (P0 + P2) / 2

        if (D - P1).mag() == 0:
            return None, None

        R = D - ((D - P0).mag()**2 / (D - P1).mag() )*(P1 - D).unit()

        p0a = (P0-R).angle()%(2*math.pi)
        p1a = (P1-R).angle()%(2*math.pi)
        p2a = (P2-R).angle()%(2*math.pi)
        alpha = (p2a - p0a) % (2*math.pi)

        if (p0a < p2a and (p1a < p0a or p2a < p1a)) or (p2a < p1a < p0a) :
            alpha = -2*math.pi + alpha

        if abs(R.x) > 1000000 or abs(R.y) > 1000000 or (R-P0).mag < min_arc_radius**2 :
            return None, None
        else :
            return R, alpha

    R1, a1 = calculate_arc_params(P0,P1,P2)
    R2, a2 = calculate_arc_params(P2,P3,P4)

    if R1 == None or R2 == None or (R1-P0).mag() < straight_tolerance or (R2-P2).mag() < straight_tolerance:
        return line_approx(bez)

    d = csp_to_arc_distance(bez, [P0,P2,R1,a1],[P2,P4,R2,a2])

    if d > biarc_tolerance and depth < biarc_max_split_depth:
        return biarc_split(bez, depth)

    #otherwise construct a line or arc as needed

    l = (P0-P2).l2()
    if  l < EMC_TOLERANCE_EQUAL**2 or l<EMC_TOLERANCE_EQUAL**2 * R1.l2() /100 :
        # arc should be straight otherwise it could be threated as full circle
        arc1 = [ bez[0], 'line', [P2.x,P2.y] ]
    else :
        arc1 = [ bez[0], 'arc', [R1.x,R1.y], a1, [P2.x,P2.y] ]

    l = (P4-P2).l2()
    if  l < EMC_TOLERANCE_EQUAL**2 or l<EMC_TOLERANCE_EQUAL**2 * R2.l2() /100 :
        # arc should be straight otherwise it could be threated as full circle
        arc2 = [ [P2.x,P2.y], 'line', [P4.x,P4.y]]
    else :
        arc2 = [ [P2.x,P2.y], 'arc', [R2.x,R2.y], a2, [P4.x,P4.y] ]

    return [ arc1, arc2 ]

def biarc_curve_segment_length(seg):
    if seg[1] == "arc" :
        return math.sqrt((seg[0][0] - seg[2][0])**2 + (seg[0][1] - seg[2][1])**2) * seg[3]
    elif seg[1] == "line" :
        return math.sqrt((seg[0][0]-seg[4][0])**2+(seg[0][1]-seg[4][1])**2)
    else:
        return 0

if __name__ == "__main__":


    bez = [[(16.9753, 0.7421), (18.2203, 2.2238), (21.0939, 2.4017), (23.1643, 1.6148)],
            [(17.5415, 0.9003), (18.4778, 3.8448), (22.4037, -0.9109), (22.563, 0.7782)]]

    ### Workings

    #Generate the figure
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect(1)
    ax.hold(True)

    ba = biarc(bez[1])

    print "%d arcs" % len(ba)


    plotBezier(bez[1])

    for i in range(len(ba)):
        a = ba[i]

        ax.plot(a[0][0], a[0][1], 'ok')
        #ax.plot(a[2][0], a[2][1], 'ok')
        ax.plot(a[4][0], a[4][1], 'ok')

    plt.show()
