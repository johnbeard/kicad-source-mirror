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

dUP = 0
dDOWN = 1
dLEFT = 2
dRIGHT = 3

class SMDInlineHeader(HFPW.ConnectorWizard):



    def GenerateParameterList(self):
        HFPW.ConnectorWizard.GenerateParameterList(self)
        self.AddParam("Pads", "hand soldering ext", self.uMM, 0);

    def Rows(self):
        return 1

    def RowLength(self):
        return abs(self.GetPitch()) * (self.N() - 1)

    def HandSolderingExt(self):
        return self.parameters["Pads"]["hand soldering ext"]

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

                if self.CentrePadsVertically():
                    off += copysign(pad_h/2, offset)

                pos = pcbnew.wxPoint(0, off)
                array = PA.PadLineArray(pad, self.N(), pad_pitch, False, pos)
                array.AddPadsToModule()

        self.supports = self.GetSupports()
        if (self.supports):
            self.supports.AddToConnector()


        self.AddDecoration()


    def DrawPin1Arrow(self, x, y, direction):

        pts = [[x, y]]
        if direction == dDOWN:
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

        self.draw.Polyline(pts)
        self.draw.SetXScale(-1)
        self.draw.Polyline(pts)
        self.draw.ResetScale()

        bottomLineY = self.supports.h / 2 + lineOffset
        bottomLineX = (support_pitch - self.supports.w) / 2

        pts = [[-bottomLineX, bottomLineY],
               [bottomLineX, bottomLineY]]

        self.draw.Polyline(pts)

        circR = pcbnew.FromMM(0.3)

        self.draw.Circle(angleLineInner - circR * 2,
                        angleLineBottom - circR * 2,
                        circR, True)

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

class MolexPicoBladeWizard(SMDInlineHeader):

    def HaveRaOption(self):
        return True

    def HaveSMDOption(self):
        return True

    def GetName(self):
        return "Molex PicoBlade"

    def GetDescription(self):
        return "Molex PicoBlade 1.25mm header"

    def GetReference(self):

        suffix = "71" if self.IsSMD() else "10" # for SMDs

        var = []

        if self.RightAngled():
            partNum = "53261" if self.IsSMD() else "53048"
        else:
            partNum = "53398" if self.IsSMD() else "53047"

        ref = "MOLEX_%s-%02d%s" % (partNum, self.N(), suffix)

        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), var)

    def GetPadSize(self):
        if self.RightAngled():
            h = pcbnew.FromMM(1.6)
        else:
            h = pcbnew.FromMM(1.3)

        w = pcbnew.FromMM(0.8)
        return w, h

    def GetPitch(self):
        return pcbnew.FromMM(1.25)

    def GetPadRowOffsets(self):
        if not self.IsSMD():
            return [-fmm(1.7)] if self.RightAngled() else [fmm(0.475)]

        return [-fmm(0.6 + 3/2)]

    def GetSupports(self):
        if not self.IsSMD():
            return None

        return DoubleSupport(self, pcbnew.FromMM(3.6 - 2.1),
                                pcbnew.FromMM(2.1), pcbnew.FromMM(3))

    def AddDecoration(self):
        if self.IsSMD():
            if self.RightAngled():
                self.DrawRASMDDecoration()
            else:
                self.DrawVertSMDDecoration()
        else:
            if self.RightAngled():
                self.DrawRATHTDecoration()
            else:
                self.DrawVertTHTDecoration()

    def DrawVertSMDDecoration(self):
        rl = self.RowLength()

        self.draw.Box(0, 0, rl + 2 * fmm(1.3), fmm(3.8))

        self.draw.SetWidth(fmm(0.1))

        self.DrawWings()

        for n in range(self.N()):
            self.DrawPinEnd(n * self.GetPitch() - rl/2, fmm(0.3),
                            fmm(0.4), fmm(0.8))

        pts = [ [0,                 fmm(1.5)],
                [rl/2 + fmm(0.9),   fmm(1.5)],
                [rl/2 + fmm(0.9),   fmm(0.725)],
                [rl/2 + fmm(1.1),   fmm(0.725)],
                [rl/2 + fmm(1.1),   fmm(0)],
                [rl/2 + fmm(0.9),   fmm(0)],
                [rl/2 + fmm(0.9),   -fmm(0.9)]]

        pts2 = [ [rl/2 + fmm(1.3),  -fmm(0.9)],
                [rl/2 + fmm(0.6),   -fmm(0.9)],
                [rl/2 + fmm(0.6),   -fmm(1.4)],
                [rl/2 + fmm(1.3),   -fmm(1.4)]]

        self.draw.Polyline(pts)
        self.draw.Polyline(pts2)

        self.draw.SetXScale(-1)

        self.draw.Polyline(pts)
        self.draw.Polyline(pts2)

        self.draw.ResetScale()

        self.draw.Value(rl/2 + fmm(2.1), fmm(-2.8), self.TextSize())
        self.draw.Reference(0, fmm(2.8), self.TextSize())

        self.DrawPin1Circle(-self.RowLength()/2 - fmm(1.5), fmm(-3));

    def DrawRASMDDecoration(self):
        rl = self.RowLength()
        body_width2 = rl/2 + fmm(1.3)
        body_height = fmm(3.8)
        self.draw.Box(0, 0, body_width2*2, body_height)

        self.draw.SetWidth(fmm(0.1))

        self.DrawRAPinOpening(body_height/2, body_width2)

        self.DrawPin1Circle(-self.RowLength()/2 - fmm(1.5), fmm(-3));

        self.DrawWings()

        self.draw.Value(rl/2 + fmm(2.1), fmm(-2.8), self.TextSize())
        self.draw.Reference(0, fmm(2.8), self.TextSize())

    def DrawVertTHTDecoration(self):
        rl = self.RowLength()

        self.draw.Box(0, 0, rl + 2 * fmm(1.5), fmm(3.2))

        self.draw.SetWidth(fmm(0.1))

        pts = [ [0,                 fmm(1.2)],
                [rl/2 + fmm(0.9),   fmm(1.2)],
                [rl/2 + fmm(0.9),   fmm(0.4)],
                [rl/2 + fmm(1.1),   fmm(0.4)],
                [rl/2 + fmm(1.1),   -fmm(0.4)],
                [rl/2 + fmm(0.9),   -fmm(0.4)],
                [rl/2 + fmm(0.9),   -fmm(1.2)]]

        pts2 = [ [-rl/2 - fmm(1.5),  -fmm(1.2)],
                [rl/2 + fmm(1.5),   -fmm(1.2)]]

        self.draw.Polyline(pts)
        self.draw.Polyline(pts2)

        self.draw.SetXScale(-1)

        self.draw.Polyline(pts)

        self.draw.ResetScale()

        self.draw.Value(0, fmm(-2.8), self.TextSize())
        self.draw.Reference(0, fmm(2.8), self.TextSize())

        self.DrawPin1Arrow(-rl/2, -fmm(1.6), dDOWN);

    def DrawRATHTDecoration(self):
        rl = self.RowLength()

        body_width2 = rl/2 + fmm(1.5)

        pts = [ [0,                 fmm(2.75)],
                [body_width2,       fmm(2.75)],
                [body_width2,       -fmm(2.75)],
                [rl/2 + fmm(0.8),   -fmm(2.75)],
                [rl/2 + fmm(0.8),   -fmm(2)],
                [0,                 -fmm(2)],
            ]

        self.draw.Polyline(pts)
        self.draw.SetXScale(-1)
        self.draw.Polyline(pts)
        self.draw.ResetScale()

        self.draw.SetWidth(fmm(0.1))

        self.DrawRAPinOpening(fmm(2.75), body_width2)

        self.draw.HLine(-rl/2 - fmm(1.5), -fmm(1.7), rl + fmm(3))

        self.draw.Value(0, fmm(-3.5), self.TextSize())
        self.draw.Reference(0, fmm(3.5), self.TextSize())

        self.DrawPin1Arrow(-rl/2, -fmm(3), dDOWN);

    def DrawRAPinOpening(self, ybottom, body_width2):
        rl2 = self.RowLength()/2
        pts = [ [0,                   ybottom - fmm(2.1)],
                [rl2 + fmm(0.6),     ybottom - fmm(2.1)],
                [rl2 + fmm(0.6),     ybottom - fmm(0.8)],
                [rl2 + fmm(1),    ybottom - fmm(0.8)],
                [rl2 + fmm(1),    ybottom - fmm(0.4)],
                [0,                   ybottom - fmm(0.4)]]

        pts2 = [[rl2 + fmm(1),    ybottom - fmm(0.4)],
                [body_width2,      ybottom]]

        self.draw.Polyline(pts)
        self.draw.Polyline(pts2)
        self.draw.SetXScale(-1)
        self.draw.Polyline(pts)
        self.draw.Polyline(pts2)
        self.draw.ResetScale()

        for n in range(self.N()):
            self.DrawPinSide(n * self.GetPitch() - rl2, ybottom - fmm(2.1))

    def DrawWings(self):
        rl = self.RowLength()

        wing = [[rl/2 + fmm(1.3),    fmm(1.6)],
                [rl/2 + fmm(3.7),    fmm(1.6)],
                [rl/2 + fmm(3.7),    fmm(-1.6)],
                [rl/2 + fmm(1.3),    fmm(-1.6)]]

        self.draw.Polyline(wing)
        self.draw.SetXScale(-1)
        self.draw.Polyline(wing)
        self.draw.ResetScale()

    def DrawPinSide(self, x, y):

        width = fmm(0.15625)
        length = fmm(1.25)
        chamferLen = fmm(0.3125)

        pts = [ [x - width,  y],
                [x - width,  y + length - chamferLen],
                [x,          y + length],
                [x + width,  y + length - chamferLen],
                [x + width,  y]]

        self.draw.Polyline(pts)

    def DrawPinEnd(self, x, y, w, h):

        z = min(w/2, h/2)

        self.draw.Box(x, y, w, h)

        if h > w:
            self.draw.Line(x, y + h/2 - z,
                           x, y - h/2 + z)

            pts = [ [x - w/2, y - h/2],
                    [x,       y - h/2 + z],
                    [x + w/2, y - h/2]]

            self.draw.Polyline(pts)

            pts = [ [_[0], y - (_[1] - y)] for _ in pts]
            self.draw.Polyline(pts)

        else:
            self.draw.Line(x - w/2 + z, y,
                           x + w/2 - z, y)

            pts = [ [x - w/2, y - h/2],
                    [x - w/2 + z, y],
                    [x - w/2, y + h/2]]

            self.draw.Polyline(pts)
            pts = [ [x - (_[0] - x), _[1]] for _ in pts]
            self.draw.Polyline(pts)

MolexPicoBladeWizard().register()


class HarwinM40Wizard(SMDInlineHeader):

    def HaveRaOption(self):
        return True;

    def GetName(self):
        return "Harwin M40"

    def GetDescription(self):
        return "Harwin M40 1.00mm SMD headers"

    def GetReference(self):

        var = [HFPW.ConnectorWizard.SMD]

        if self.RightAngled():
            partNum = "401"
        else:
            partNum = "301"

        ref = "Harwin_M40-%s%02d46" % (partNum, self.N())
        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), var)

    def GetPadSize(self):
        if self.RightAngled():
            h = pcbnew.FromMM(5.5 - 4.0)
        else:
            h = pcbnew.FromMM(4.2 - 2.6)

        w = pcbnew.FromMM(0.6)
        return w, h

    def GetPitch(self):
        if self.RightAngled():
            return pcbnew.FromMM(1)

        return pcbnew.FromMM(-1)

    def GetSupports(self):
        return DoubleSupport(self, pcbnew.FromMM(0.7),
                                pcbnew.FromMM(1.2), pcbnew.FromMM(1.8))

    def AddDecoration(self):
        self.OpenTeeDecoration()

    def GetPadRowOffsets(self):

        if not self.IsSMD():
            return []

        if self.RightAngled():
            vsep = pcbnew.FromMM(4 - 1.8/2)
        else:
            vsep = pcbnew.FromMM(2.6 - 1.8/2)

        return [-vsep]

HarwinM40Wizard().register()
