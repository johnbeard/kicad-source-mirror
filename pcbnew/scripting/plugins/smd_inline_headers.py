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
Base classes for SMD and THT headers
"""

from __future__ import division
from math import copysign
import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import PadArray as PA

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

        self.SetModuleDescription()


class ThtRaHeaderShrouded(HFPW.ConnectorWizard):

    def BuildThisFootprint(self):
        prm = self.GetComponentParams()

        pad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'])
        firstPad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'], shape=pcbnew.PAD_RECT)

        pos = pcbnew.wxPoint(0, 0)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos, firstPad=firstPad)
        array.AddPadsToModule()

        row_length = (self.N() - 1) * prm['d']

        # silk screen line
        topY = -prm['E1']
        bottomY = prm['E2']
        boxX = row_length/2 + prm['D1']

        pts = [ [-boxX,  -prm['B']],
                [-boxX,  prm['E2']],
                [boxX,   prm['E2']],
                [boxX,   prm['B']]
              ]

        self.draw.Polyline(pts)

        self.draw.SetLayer(pcbnew.ADHESIVE_N_FRONT)

        bodyH = bottomY - topY
        setback = min(fmm(2), bodyH/2)
        self.draw.BoxWithDiagonalAtCorner(0, (bottomY + topY)/2, boxX*2,
                                            bodyH, setback)

        TextSize = fmm(0.8)
        self.draw.Value(0, topY - TextSize, TextSize)
        self.draw.Reference(0, prm['E2'] + TextSize, TextSize)

        #origin to pin 1
        self.module.SetPosition(pcbnew.wxPoint(-row_length/2, fmm(4)))

        self.SetModuleDescription()

class ThtVerticalHeader(HFPW.ConnectorWizard):

    def BuildThisFootprint(self):
        prm = self.GetComponentParams()

        pad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'])
        firstPad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'], shape=pcbnew.PAD_RECT)

        pos = pcbnew.wxPoint(0, 0)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos, firstPad=firstPad)
        array.AddPadsToModule()

        row_length = (self.N() - 1) * prm['d']

        # silk screen box
        topY = -prm['E1']
        bottomY = prm['E2']
        boxX = row_length/2 + prm['D1']

        cornerGap = fmm(1.5)

        pts = [ [-boxX + cornerGap, topY],
                [boxX,              topY],
                [boxX,              bottomY],
                [-boxX,             bottomY],
                [-boxX,             topY + cornerGap]]

        self.draw.Polyline(pts)

        self.draw.SetLayer(pcbnew.ADHESIVE_N_FRONT)

        bodyH = bottomY - topY
        setback = min(fmm(2), bodyH/2)
        self.draw.BoxWithDiagonalAtCorner(0, (bottomY + topY)/2, boxX*2,
                                            bodyH, setback)

        TextSize = fmm(0.8)
        self.draw.Value(0, topY - TextSize, TextSize)
        self.draw.Reference(0, prm['E2'] + TextSize, TextSize)

        #origin to pin 1
        self.module.SetPosition(pcbnew.wxPoint(-row_length/2, 0))

        self.SetModuleDescription()

