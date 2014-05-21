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

import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA


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
        pad = PA.PadMaker(self.module).SMDPad(pad_h, pad_w)

        for offset in self.GetPadRowOffsets():
            off = offset + copysign(pad_h/2, offset)

            pos = pcbnew.wxPoint(0, off)

            pad = PA.PadMaker(self.module).SMDPad(pad_h, pad_w)
            array = PA.PadLineArray(pad, self.N(), pad_pitch, False, pos)
            array.AddPadsToModule()

        support_w, support_h = self.GetSupportSize()
        pad_w, pad_h = self.GetPadSize()

        support_pitch = self.RowLength() + 2 * self.GetSupportHSep() + support_w

        pos = pcbnew.wxPoint(0, 0)
        pad = PA.PadMaker(self.module).SMDPad(support_h, support_w)
        array = PA.PadLineArray(pad, 2, support_pitch, False, pos, "")
        array.AddPadsToModule()

        self.AddDecoration()

    def AddDecoration(self):
        # only smds have the support
        if len(self.GetPadRowOffsets()) == 1: # we have a pair of supports
            self.OpenTeeDecoration()

    def OpenTeeDecoration(self):

        support_w, support_h = self.GetSupportSize()
        pad_w, pad_h = self.GetPadSize()

        support_pitch = self.RowLength() + 2 * self.GetSupportHSep() + support_w

        rowOffset = self.GetPadRowOffsets()[0]

        # now draw the silkscreen
        lineOffset = pcbnew.FromMM(0.5)
        angleLineTop = rowOffset + copysign(pad_h, rowOffset)
        angleLineBottom = -support_h / 2 - lineOffset
        angleLineInner = -(self.RowLength() + pad_w) / 2 - lineOffset
        angleLineOuter = -(support_pitch + support_w) / 2

        pts = [[angleLineInner, angleLineTop],
                [angleLineInner, angleLineBottom],
                [angleLineOuter, angleLineBottom]]

        self.draw.Polyline(pts)
        self.draw.SetXScale(-1)
        self.draw.Polyline(pts)
        self.draw.ResetScale()

        bottomLineY = support_h / 2 + lineOffset
        bottomLineX = (support_pitch - support_w) / 2

        pts = [[-bottomLineX, bottomLineY],
               [bottomLineX, bottomLineY]]

        self.draw.Polyline(pts)

        circR = pcbnew.FromMM(0.3)

        self.draw.Circle(angleLineInner - circR * 2,
                        angleLineBottom - circR * 2,
                        circR, True)

        textSize = self.TextSize()

        self.draw.Value(-(angleLineInner + angleLineOuter) / 2,
                         angleLineBottom - textSize, textSize)
        self.draw.Reference(0, bottomLineY + textSize, textSize)

class MolexPicoBladeWizard(SMDInlineHeader):

    def HaveRaOption(self):
        return True;

    def GetName(self):
        return "Molex PicoBlade"

    def GetDescription(self):
        return "Molex PicoBlade 1.25mm header"

    def GetReference(self):

        suffix = "71" # for SMDs

        var = [HFPW.ConnectorWizard.SMD]

        if self.RightAngled():
            partNum = "53261"
        else:
            partNum = "53398"

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

    def GetSupportSize(self):
        return pcbnew.FromMM(2.1), pcbnew.FromMM(3)

    def GetSupportHSep(self):
        return pcbnew.FromMM(3.6 - 2.1)

    def GetPadRowOffsets(self):
        # centre of support to innner edge of
        return [-pcbnew.FromMM(0.6 + 3/2)]

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

    def GetSupportSize(self):
        return pcbnew.FromMM(1.2), pcbnew.FromMM(1.8)

    def GetSupportHSep(self):
        return pcbnew.FromMM(0.7)

    def GetPadRowOffsets(self):

        if self.RightAngled():
            vsep = pcbnew.FromMM(4 - 1.8/2)
        else:
            vsep = pcbnew.FromMM(2.6 - 1.8/2)

        return [-vsep]

HarwinM40Wizard().register()
