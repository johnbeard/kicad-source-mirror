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
import pcbnew

import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA


class SMDInlineHeader(HFPW.ConnectorWizard):

    def GenerateParameterList(self):
        HFPW.ConnectorWizard.GenerateParameterList(self)

        self.AddParam("Pads", "hand soldering ext", self.uMM, 0);

    def BuildThisFootprint(self):

        pads = self.parameters["Pads"]

        ext = pads["hand soldering ext"]

        support_hsep, support_vsep = self.GetPadToSupportSep()
        support_w, support_h = self.GetSupportSize()
        pad_w, pad_h = self.GetPadSize()
        pad_pitch = self.GetPitch()

        pad_h += ext

        # offset goes in the middle of the supports
        if support_h and support_vsep:
            pad_row_offset = (support_h + pad_h) / 2 + support_vsep
        else:
            pad_row_offset = 0

        row_len = abs(pad_pitch) * (self.N() - 1)

        # add in the pads
        pad = PA.PadMaker(self.module).SMDPad(pad_h, pad_w)

        pos = pcbnew.wxPoint(0, -pad_row_offset)

        pad = PA.PadMaker(self.module).SMDPad(pad_h, pad_w)
        array = PA.PadLineArray(pad, self.N(), pad_pitch, False, pos)
        array.AddPadsToModule()

        #reference and value
        textSize = pcbnew.FromMM(0.8)

        # only smds have the support
        if support_h and support_w:
            support_pitch = row_len + 2 * support_hsep + support_w
            pos = pcbnew.wxPoint(0, 0)
            pad = PA.PadMaker(self.module).SMDPad(support_h, support_w)
            array = PA.PadLineArray(pad, 2, support_pitch, False, pos, "")
            array.AddPadsToModule()

            # now draw the silkscreen
            lineOffset = pcbnew.FromMM(0.5)
            angleLineTop = -pad_row_offset - pad_h/2 + ext
            angleLineBottom = -support_h / 2 - lineOffset
            angleLineInner = -(row_len + pad_w) / 2 - lineOffset
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

    def GetPadToSupportSep(self):
        return pcbnew.FromMM(3.6 - 2.1), pcbnew.FromMM(0.6)

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

    def GetPadToSupportSep(self):
        hsep = pcbnew.FromMM(0.7)

        if self.RightAngled():
            vsep = pcbnew.FromMM(4 - 1.8)
        else:
            vsep = pcbnew.FromMM(2.6 - 1.8)

        return hsep, vsep

HarwinM40Wizard().register()
