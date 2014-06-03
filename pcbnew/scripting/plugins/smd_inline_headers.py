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

"""
Generate an inline SMD connector with a footprint like this:

          | XXX  XXX  XXX  XXX |
          | XXX  XXX  XXX  XXX |
      o   | XXX  XXX  XXX  XXX |
     ooo  | XXX  XXX  XXX  XXX |
      o   | XXX  XXX  XXX  XXX |
-----------                    -----------
XXXXXXX                            XXXXXXX
XXXXXXX                            XXXXXXX
XXXXXXX                            XXXXXXX
XXXXXXX                            XXXXXXX

Examples include Molex PicoBlades and Harwin M40
"""

from __future__ import division
from math import copysign
import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA

class SMDInlineHeader(HFPW.ConnectorWizard):

    def GenerateParameterList(self):
        HFPW.ConnectorWizard.GenerateParameterList(self)
        self.AddParam("Pads", "hand soldering ext", self.uMM, 0);

    def HandSolderingExt(self):
        return self.parameters["Pads"]["hand soldering ext"]

    def Rows(self):
        return 1

    def RowLength(self):
        return abs(self.GetPitch()) * (self.N() - 1)

    def TextSize(self):
        return pcbnew.FromMM(0.8)

    def BuildThisFootprint(self):

        pad_w, pad_h = self.GetPadSize()
        pad_pitch = self.GetPitch()

        pad_h += self.HandSolderingExt()

        # add in the pads
        print self.IsSMD()
        if self.IsSMD():
            pad = PA.PadMaker(self.module).SMDPad(pad_h, pad_w)
        else:
            pad = PA.PadMaker(self.module).THPad(pad_h, pad_w, fmm(0.5))

        if not len(self.GetPadRowOffsets()):
            pos = pcbnew.wxPoint(0, 0)
            array = PA.PadLineArray(pad, self.N(), pad_pitch, False, pos)
            array.AddPadsToModule()
        else:
            for offset in self.GetPadRowOffsets():
                off = offset;

                if not self.CentrePadsVertically():
                    off += copysign(pad_h/2, offset)

                pos = pcbnew.wxPoint(0, off)
                array = PA.PadLineArray(pad, self.N(), pad_pitch, False, pos)
                array.AddPadsToModule()

        self.supports = self.GetSupports()
        if (self.supports):
            self.supports.AddToConnector()


        self.AddDecoration()

        self.SetModuleDescription()


    def DrawPin1Arrow(self, x, y, direction):

        pts = [[x, y]]
        if direction == self.draw.dDOWN:
            pts.append([x + fmm(0.5), y - fmm(0.5)])
            pts.append([x - fmm(0.5), y - fmm(0.5)])

        pts.append([x, y])

        self.draw.Polyline(pts)

    def DrawPin1Circle(self, x, y):
        self.draw.Circle(x, y, fmm(0.4), True)

    def OpenTeeDecoration(self):

        pad_w, pad_h = self.GetPadSize()

        support_pitch = self.RowLength() + 2 * self.supports.hsep + self.supports.w

        rowOffset = self.GetPadRowOffsets()[0]

        # now draw the silkscreen
        lineOffset = pcbnew.FromMM(0.5)
        angleLineTop = rowOffset + copysign(pad_h, rowOffset)
        angleLineBottom = -self.supports.h / 2 - lineOffset
        angleLineInner = -(self.RowLength() + pad_w) / 2 - lineOffset
        angleLineOuter = -(support_pitch + self.supports.w) / 2

        pts = [[angleLineInner, angleLineTop],
                [angleLineInner, angleLineBottom],
                [angleLineOuter, angleLineBottom]]

        self.draw.MirroredPolyline(pts, mirrorX=True)

        bottomLineY = self.supports.h / 2 + lineOffset
        bottomLineX = (support_pitch - self.supports.w) / 2

        pts = [[-bottomLineX, bottomLineY],
               [bottomLineX, bottomLineY]]

        self.draw.Polyline(pts)

        circR = pcbnew.FromMM(0.3)

        self.draw.Circle(angleLineInner - circR * 2,
                        angleLineBottom - circR * 2,
                        circR, True)

    def DrawVertSMDDecoration(self):
        pad_w, pad_h = self.GetPadSize()

        support_pitch = self.RowLength() + 2 * self.supports.hsep + self.supports.w

        rowOffset = self.GetPadRowOffsets()[0]

        # now draw the silkscreen
        lineOffset = pcbnew.FromMM(0.5)
        angleLineTop = rowOffset + copysign(pad_h, rowOffset)
        angleLineBottom = -self.supports.h / 2 - lineOffset
        angleLineInner = -(self.RowLength() + pad_w) / 2 - lineOffset
        angleLineOuter = -(support_pitch + self.supports.w) / 2

class DoubleSupport():

    def __init__(self, conn, hsep, w, h):
        self.conn = conn
        self.hsep = hsep
        self.h = h
        self.w = w

    def AddToConnector(self):

        self.pitch = self.conn.RowLength() + 2 * self.hsep + self.w

        pad_w, pad_h = self.conn.GetPadSize()

        pos = pcbnew.wxPoint(0, 0)
        pad = PA.PadMaker(self.conn.module).SMDPad(self.h, self.w)
        array = PA.PadLineArray(pad, 2, self.pitch, False, pos, "")
        array.AddPadsToModule()

class SMDInlineHeaderWithWings(HFPW.ConnectorWizard):

    def BuildThisFootprint(self):

        prm = self.GetComponentParams();

        row_length = (self.N() - 1) * prm['d']

        pad_h = prm['B'] + self.HandSolderingExt()

        pad = PA.PadMaker(self.module).SMDPad(pad_h, prm['A'])


        off = -prm['D'] / 2 - prm['E'] - pad_h / 2;

        pos = pcbnew.wxPoint(0, off)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos)
        array.AddPadsToModule()

        # supports
        support_pitch = row_length + 2 * prm['F'] + prm['C']

        pos = pcbnew.wxPoint(0, 0)
        pad = PA.PadMaker(self.module).SMDPad(prm['D'], prm['C'])
        array = PA.PadLineArray(pad, 2, support_pitch, False, pos, "")
        array.AddPadsToModule()

        # silk line

        innerVerticalX = -row_length/2 - prm['A']/2 - fmm(0.5)
        outerVerticalX = -support_pitch/2 - prm['C']/2 - fmm(0.5)


        pts = [ [innerVerticalX,   -prm['D'] / 2 - prm['E'] - pad_h],
                [innerVerticalX,   -prm['D'] / 2 - fmm(0.5)],
                [outerVerticalX,   -prm['D'] / 2 - fmm(0.5)],
                [outerVerticalX,    prm['D'] / 2 + prm['H']],
                [-outerVerticalX,   prm['D'] / 2 + prm['H']],
                [-outerVerticalX,  -prm['D'] / 2 - fmm(0.5)],
                [-outerVerticalX - fmm(1),  -prm['D'] / 2 - fmm(0.5)],
              ]

        self.draw.Polyline(pts)

        TextSize = fmm(0.8)

        #texts
        self.draw.Value(row_length/2 + fmm(2.1), fmm(-2.8), TextSize)
        self.draw.Reference(0, fmm(2.8), TextSize)

    def GetComponentParams(self):
        raise NotImplementedError

class NewMolexSmdHeader(SMDInlineHeaderWithWings):

    def HaveRaOption(self):
        return True

    def GetName(self):
        return "Molex PicoBlade"

    def GetDescription(self):
        return "Molex PicoBlade 1.25mm shrouded header"

    def GetReference(self):

        suffix = "71"
        partNum = "53048" if self.RightAngled() else "53048"

        ref = "Molex_PicoBlade_%s-%02d%s" % (partNum, self.N(), suffix)

        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), [])

    def GetComponentParams(self):

        return {
            'A': fmm(0.8),
            'B': fmm(1.6) if self.RightAngled() else fmm(1.3),
            'C' : fmm(2.1),
            'D' : fmm(3),
            'E' : fmm(0.6),
            'F' : fmm(1.1),
            'H' : fmm(0.4),
            'd' : fmm(1.25),
            }

class ThtRaHeaderShrouded(HFPW.ConnectorWizard):

    def BuildThisFootprint(self):
        prm = self.GetComponentParams()

        pad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'])

        pos = pcbnew.wxPoint(0, 0)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos)
        array.AddPadsToModule()

        TextSize = fmm(0.8)
        self.draw.Value(0, fmm(-2.8), TextSize)
        self.draw.Reference(0, fmm(2.8), TextSize)

class NewMolexThtRaHeader(ThtRaHeaderShrouded):

    def GetName(self):
        return "Molex PicoBlade"

    def GetDescription(self):
        return "Molex PicoBlade 1.25mm shrouded header"

    def GetReference(self):

        suffix = "10"
        partNum = "53398"

        ref = "Molex_PicoBlade_%s-%02d%s" % (partNum, self.N(), suffix)

        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), [])

    def GetComponentParams(self):

        return {
            'L': fmm(5.5),
            'L1': fmm(5.5 - 1.05),
            'e' : 0,
            'd' : fmm(1.25),
            'b' : fmm(0.5),
            'E' : fmm(3.5),
            'D1' : fmm(1.5),
            'B' : fmm(0.8)
            }
