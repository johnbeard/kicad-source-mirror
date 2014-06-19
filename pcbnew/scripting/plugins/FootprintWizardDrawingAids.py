#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

from __future__ import division

import pcbnew

import math

class FootprintWizardDrawingAids:
    """
    Collection of handy functions to simplify drawing shapes from within
    footprint wizards

    A "drawing context" is provided which can be used to set and retain
    settings such as line width and layer
    """

    # directions (in degrees, compass-like)
    dirN = 0
    dirNE = 45
    dirE = 90
    dirSE = 135
    dirS = 180
    dirSW = 225
    dirW = 270
    dirNW = 315

    flipNone = 0
    flipX = 1 #flip X values, i.e. about Y
    flipY = 2 #flip Y valuersabout X
    flipBoth = 3

    xfrmIDENTITY = [1, 0, 0, 0, 1, 0]  #no transform

    def __init__(self, module):
        self.module = module
        #drawing context defaults
        self.dc = {
            'layer': pcbnew.SILKSCREEN_N_FRONT,
            'width': pcbnew.FromMM(0.2),
            'transforms': [],
            'transform': self.xfrmIDENTITY
        }

    def PushTransform(self, mat):
        self.dc['transforms'].append(mat)
        self.RecomputeTransforms()

    def PopTransform(self, num=1):

        for i in range(num):
            mat = self.dc['transforms'].pop()
        self.RecomputeTransforms()
        return mat

    def ResetTransform(self):
        self.dc['transforms'] = []
        self.RecomputeTransforms()

    def _ComposeMatricesWithIdentity(self, mats):

        x = self.xfrmIDENTITY

        for mat in mats:
            #precompose with each transform in turn
            x = [ x[0] * mat[0] + x[1] * mat[3],
                    x[0] * mat[1] + x[1] * mat[4],
                    x[0] * mat[2] + x[1] * mat[5] + x[2],
                    x[3] * mat[0] + x[4] * mat[3],
                    x[3] * mat[1] + x[4] * mat[4],
                    x[3] * mat[2] + x[4] * mat[5] + x[5]]

        return x

    def RecomputeTransforms(self):
        self.dc['transform'] = self._ComposeMatricesWithIdentity(self.dc['transforms'])

    def TransformTranslate(self, x, y, push=True):
        mat = [1, 0, x, 0, 1, y]

        if push:
            self.PushTransform(mat)
        return mat

    def TransformFlipOrigin(self, flip, push=True):
        mat = None
        if flip == self.flipX:
            mat = [-1,0, 0, 0, 1, 0]
        elif flip == self.flipY:
            mat = [ 1,0, 0, 0,-1, 0]
        elif flip == self.flipBoth:
            mat = [-1,0, 0, 0,-1, 0]
        elif flip == self.flipNone:
            mat = self.xfrmIDENTITY
        else:
            raise ValueError

        if push:
            self.PushTransform(mat)
        return mat


    def TransformFlip(self, x, y, flip=flipNone, push=True):
        mats = [self.TransformTranslate(x, y, push=False),
                self.TransformFlipOrigin(flip, push=False),
                self.TransformTranslate(-x,-y, push=False)]

        #distill into a single matrix
        mat = self._ComposeMatricesWithIdentity(mats)

        if push:
            self.PushTransform(mat)
        return mat


    def TransformRotationOrigin(self, rot, push=True):
        rads = rot * math.pi / 180
        mat = [math.cos(rads), -math.sin(rads), 0, math.sin(rads), math.cos(rads), 0]

        if push:
            self.PushTransform(mat)
        return mat

    def TransformRotation(self, x, y, rot, push=True):

        mats = [self.TransformTranslate(x, y, push=False),
                self.TransformRotationOrigin(rot, push=False),
                self.TransformTranslate(-x, -y, push=False)]

        #distill into a single matrix
        mat = self._ComposeMatricesWithIdentity(mats)

        if push:
            self.PushTransform(mat)
        return mat

    def TransformScaleOrigin(self, sx, sy = None, push = True):

        if sy is None:
            sy = sx

        mat = [sx, 0, 0, 0, sy, 0]

        if push:
            print "push", mat
            self.PushTransform(mat)
        return mat

    def TransformPoint(self, x, y, mat = None):

        if not mat:
            mat = self.dc['transform']

        return pcbnew.wxPoint(  x * mat[0] + y * mat[1] + mat[2],
                                x * mat[3] + y * mat[4] + mat[5] )

    def SetWidth(self, width):
        self.dc['width'] = width

    def SetLayer(self, layer):
        self.dc['layer'] = layer

    def Line(self, x1, y1, x2, y2):

        outline = pcbnew.EDGE_MODULE(self.module)
        outline.SetWidth(self.dc['width'])
        outline.SetLayer(self.dc['layer'])
        outline.SetShape(pcbnew.S_SEGMENT)
        start = self.TransformPoint(x1, y1)
        end = self.TransformPoint(x2, y2)
        outline.SetStartEnd(start, end)
        self.module.Add(outline)

    def Circle(self, x, y, r, filled=False):
        circle = pcbnew.EDGE_MODULE(self.module)
        start = self.TransformPoint(x, y)

        if filled:
            circle.SetWidth(r)
            end = self.TransformPoint(x, y + r/2)
        else:
            circle.SetWidth(self.dc['width'])
            end = self.TransformPoint(x, y + r)

        circle.SetLayer(self.dc['layer'])
        circle.SetShape(pcbnew.S_CIRCLE)
        circle.SetStartEnd(start, end)
        self.module.Add(circle)

    def Arc(self, cx, cy, sx, sy, a):
        circle = pcbnew.EDGE_MODULE(self.module)
        circle.SetWidth(self.dc['width'])

        center = self.TransformPoint(cx, cy)
        start = self.TransformPoint(sx, sy)

        circle.SetLayer(self.dc['layer'])
        circle.SetShape(pcbnew.S_ARC)

        circle.SetAngle(a)
        circle.SetStartEnd(center, start)
        self.module.Add(circle)


    # extends from (x1,y1) right
    def HLine(self, x, y, l):
        """
        Draw a horizontal line from (x,y), rightwards
        """
        self.Line(x, y, x + l, y)

    def VLine(self, x, y, l):
        """
        Draw a vertical line from (x1,y1), downwards
        """
        self.Line(x, y, x, y + l)


    def Polyline(self, pts, mirrorX=None, mirrorY=None):
        """
        Draw a polyline, optinally mirroring around the given points
        """

        def _PolyLineInternal(pts):
            if len(pts) < 2:
                return

            for i in range(0, len(pts) - 1):
                self.Line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])

        _PolyLineInternal(pts) #original

        if mirrorX is not None:
            self.TransformFlip(mirrorX, 0, self.flipX)
            _PolyLineInternal(pts)
            self.PopTransform()

        if mirrorY is not None:
            self.TransformFlipOrigin(0, mirrorY, self.flipY)
            _PolyLineInternal(pts)
            self.PopTransform()

        if mirrorX is not None and mirrorY is not None:
            self.TransformFlip(mirrorX, mirrorY, self.flipBoth) #both
            _PolyLineInternal(pts)
            self.PopTransform()

    def Reference(self, x, y, size):
        """
        Draw the module's reference as the given point.

        The actual setting of the reference is not done in this drawing
        aid - that is up to the wizard
        """

        text_size = pcbnew.wxSize(size, size)

        self.module.Reference().SetPos0(self.TransformPoint(x, y))
        self.module.Reference().SetTextPosition(self.module.Reference().GetPos0())
        self.module.Reference().SetSize(text_size)

    def Value(self, x, y, size):
        """
        As for references, draw the module's value
        """
        text_size = pcbnew.wxSize(size, size)

        self.module.Value().SetPos0(self.TransformPoint(x, y))
        self.module.Value().SetTextPosition(self.module.Value().GetPos0())
        self.module.Value().SetSize(text_size)

    def Box(self, x, y, w, h):
        """
        Draw a rectangular box, centred at (x,y), with given width and
        height
        """

        pts = [ [x - w/2, y - h/2], # left
                [x + w/2, y - h/2], # right
                [x + w/2, y + h/2], # bottom
                [x - w/2, y + h/2], # top
                [x - w/2, y - h/2]] # close

        self.Polyline(pts)

    def NotchedBox(self, x, y, w, h, notchW, notchH):
        """
        Draw a box with a notch in the top edge
        """
        #limit to half the overall width
        notchW = min(x + w/2, notchW)

        # draw notch
        self.Polyline([ #three sides of box
                        (x - w/2, y - h/2),
                        (x - w/2, y + h/2),
                        (x + w/2, y + h/2),
                        (x + w/2, y - h/2),
                        #the notch
                        (notchW/2, y - h/2),
                        (notchW/2, y - h/2 + notchH),
                        (-notchW/2, y - h/2 + notchH),
                        (-notchW/2, y - h/2),
                        (x - w/2, y - h/2)
                    ])

    def BoxWithDiagonalAtCorner(self, x, y, w, h, setback=pcbnew.FromMM(1.27), flip = flipNone):
        """
        Draw a box with a diagonal at the top left corner
        """

        self.TransformFlip(x, y, flip, push=True)

        pts = [ [x - w/2 + setback, y - h/2],
                [x - w/2,           y - h/2 + setback],
                [x - w/2,           y + h/2],
                [x + w/2,           y + h/2],
                [x + w/2,           y - h/2],
                [x - w/2 + setback, y - h/2]]

        self.Polyline(pts)

        self.PopTransform()

    def BoxWithOpenCorner(self, x, y, w, h,
                            setback = pcbnew.FromMM(1.27), flip = flipNone):
        """
        Draw a box with an opening at the top left corner
        """

        self.TransformTranslate(x, y)
        self.TransformFlipOrigin(flip)


        pts = [ [- w/2,           - h/2 + setback],
                [- w/2,             h/2],
                [  w/2,             h/2],
                [  w/2,           - h/2],
                [- w/2 + setback, - h/2]]

        self.Polyline(pts)

        self.PopTransform(num=2)

    def MarkerArrow(self, x, y, direction=dirN, width=pcbnew.FromMM(1)):
        """
        Draw a marker arrow facing in the given direction, with the point at (x,y)

        Direction of 0 is north
        """

        self.TransformTranslate(x, y)
        self.TransformRotationOrigin(direction)


        pts = [ [0,          0],
                [ width / 2, width / 2],
                [-width / 2, width / 2],
                [0,          0]]

        self.Polyline(pts)
        self.PopTransform(2)

    ####################################################################
    def DrawPinSide(self, w, l, chamferLen, x, y):

        pts = [ [x - w,  y],
                [x - w,  y + l - chamferLen],
                [x,      y + l],
                [x + w,  y + l - chamferLen],
                [x + w,  y]]

        self.Polyline(pts)

    def DrawPinEnd(self, x, y, w, h):

        z = min(w/2, h/2)

        self.Box(x, y, w, h)

        if h > w:
            self.Line(x, y + h/2 - z,
                           x, y - h/2 + z)

            pts = [ [x - w/2, y - h/2],
                    [x,       y - h/2 + z],
                    [x + w/2, y - h/2]]

            self.Polyline(pts)

            pts = [ [_[0], y - (_[1] - y)] for _ in pts]
            self.Polyline(pts)

        else:
            self.draw.Line(x - w/2 + z, y,
                           x + w/2 - z, y)

            pts = [ [x - w/2, y - h/2],
                    [x - w/2 + z, y],
                    [x - w/2, y + h/2]]

            self.Polyline(pts)
            pts = [ [x - (_[0] - x), _[1]] for _ in pts]
            self.Polyline(pts)

    def SawtoothLine(self, n, pitch, ybottom, ytop, wbottom, wtop):

        for i in range(n):
            cx = i * pitch - (n-1)*pitch/2

            pts = [ [cx - pitch/2,          ytop],
                    [cx - pitch/2 + wtop/2, ytop],
                    [cx - wbottom/2,        ybottom],
                    [cx + wbottom/2,        ybottom],
                    [cx + pitch/2 - wtop/2, ytop],
                    [cx + pitch/2,          ytop],
                ]

            self.Polyline(pts)
