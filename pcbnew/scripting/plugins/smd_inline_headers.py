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

    def IsSMD(self):
        return True

    def BuildThisFootprint(self):

        prm = self.GetComponentParams();

        row_length = (self.N() - 1) * prm['d']

        pad_h = prm['B'] + self.HandSolderingExt()

        pad = PA.PadMaker(self.module).SMDPad(pad_h, prm['A'])

        off = -prm['D'] / 2 - prm['E'] - pad_h / 2;

        pos = pcbnew.wxPoint(0, off)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos)
        array.AddPadsToModule(self.draw)

        # supports
        support_pitch = row_length + 2 * prm['F'] + prm['C']

        pos = pcbnew.wxPoint(0, 0)
        pad = PA.PadMaker(self.module).SMDPad(prm['D'], prm['C'])
        array = PA.PadLineArray(pad, 2, support_pitch, False, pos, "")
        array.AddPadsToModule(self.draw)

        # silk line

        innerVerticalX = -row_length/2 - prm['A']/2 - fmm(0.5)
        outerVerticalX = -support_pitch/2 - prm['C']/2 - fmm(0.5)

        topY = -prm['D'] / 2 - prm['E'] - pad_h


        pts = [ [innerVerticalX,   topY],
                [innerVerticalX,   -prm['D'] / 2 - fmm(0.5)],
                [outerVerticalX,   -prm['D'] / 2 - fmm(0.5)],
                [outerVerticalX,    prm['D'] / 2 + prm['H']],
                [-outerVerticalX,   prm['D'] / 2 + prm['H']],
                [-outerVerticalX,  -prm['D'] / 2 - fmm(0.5)],
                [-outerVerticalX - fmm(1),  -prm['D'] / 2 - fmm(0.5)],
              ]

        self.draw.Polyline(pts)

        # marker arrow
        self.draw.MarkerArrow(-row_length / 2, topY - fmm(0.5), direction=self.draw.dirS)

        #assembly layer
        self.draw.SetLayer(pcbnew.ADHESIVE_N_FRONT)

        mainBodyX = row_length/2 + prm['F']
        mainBodyTop = -prm['D']/2 - prm['E']
        mainBodyBot = prm['D']/2 + prm['H']
        pts = [ [-mainBodyX,    mainBodyTop],
                [-mainBodyX,    mainBodyBot],
                [ mainBodyX,    mainBodyBot],
                [ mainBodyX,    mainBodyTop],
                [-mainBodyX,    mainBodyTop]]

        self.draw.Polyline(pts)

        wingOuterX = mainBodyX + prm['C']

        pts = [ [ mainBodyX,    -prm['D']/2],
                [ wingOuterX,   -prm['D']/2],
                [ wingOuterX,    prm['D']/2],
                [ mainBodyX,     prm['D']/2] ]

        self.draw.Polyline(pts, mirrorX=0)

        #assembly layer - pin 1
        pin1X = -row_length/2
        pin1MarkSize = min(abs(-mainBodyX - pin1X), fmm(3)) #make sure we can fit horizontally
        pin1MarkSize = min(pin1MarkSize, abs(0.5 * (mainBodyTop - mainBodyBot))) #and vertically

        pts = [ [pin1X - pin1MarkSize,  mainBodyTop],
                [pin1X,                 mainBodyTop + pin1MarkSize],
                [pin1X + pin1MarkSize,  mainBodyTop]]

        self.draw.Polyline(pts)

        TextSize = fmm(1)

        #texts
        self.draw.Value(row_length/2 + fmm(2.1), fmm(-2.8), TextSize)
        self.draw.Reference(0, fmm(2.8), TextSize)

        self.SetModuleDescription()


class ThtRaHeaderShrouded(HFPW.ConnectorWizard):

    def IsRightAngled(self):
        return True

    def BuildThisFootprint(self):
        prm = self.GetComponentParams()

        row_length = (self.N() - 1) * prm['d']

        self.draw.TransformTranslate(row_length/2, 0)

        pad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'])
        firstPad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'], shape=pcbnew.PAD_RECT)

        pos = pcbnew.wxPoint(0, 0)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos, firstPad=firstPad)
        array.AddPadsToModule(self.draw)

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

        self.DrawPin1MarkerAndTexts(prm['E1'], prm['E2'], -row_length/2)

        self.draw.SetLayer(pcbnew.ADHESIVE_N_FRONT)

        bodyH = bottomY - topY
        setback = min(fmm(2), bodyH/2)
        self.draw.BoxWithDiagonalAtCorner(0, (bottomY + topY)/2, boxX*2,
                                            bodyH, setback)

        #origin to pin 1
        self.module.SetPosition(pcbnew.wxPoint(-row_length/2, fmm(4)))

        self.SetModuleDescription()

class ThtVerticalHeader(HFPW.ConnectorWizard):

    def BuildThisFootprint(self):
        prm = self.GetComponentParams()

        row_length = (self.N() - 1) * prm['d']

        self.draw.TransformTranslate(row_length/2, 0)

        pad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'])
        firstPad = PA.PadMaker(self.module).THPad(prm['B'], prm['B'], drill=prm['b'], shape=pcbnew.PAD_RECT)

        pos = pcbnew.wxPoint(0, 0)
        array = PA.PadLineArray(pad, self.N(), prm['d'], False, pos, firstPad=firstPad)
        array.AddPadsToModule(self.draw)

        # silk screen box
        topY = -prm['E1']
        bottomY = prm['E2']
        boxW = row_length + 2 * prm['D1']
        bodyH = bottomY - topY
        bodyYMid = (topY + bottomY) / 2

        self.draw.BoxWithOpenCorner(0, bodyYMid, boxW, bodyH, flip=self.draw.flipY)

        self.DrawPin1MarkerAndTexts(prm['E1'], prm['E2'], -row_length / 2)

        self.draw.SetLayer(pcbnew.ADHESIVE_N_FRONT)

        self.draw.BoxWithDiagonalAtCorner(0, bodyYMid, boxW, bodyH, flip=self.draw.flipY)

        #origin to pin 1
        self.module.SetPosition(pcbnew.wxPoint(-row_length/2, 0))

        self.SetModuleDescription()
