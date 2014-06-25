#  PadArray.py
#
#  Copyright 2014 john <john@johndev>
#
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
#

import pcbnew


class PadMaker:
    """
    Useful construction functions for common types of pads
    """

    def __init__(self, module):
        self.module = module

    def THPad(self, w, l, drill, shape=pcbnew.PAD_OVAL):
        pad = pcbnew.D_PAD(self.module)

        pad.SetSize(pcbnew.wxSize(l, w))

        pad.SetShape(shape)

        pad.SetAttribute(pcbnew.PAD_STANDARD)
        pad.SetLayerMask(pcbnew.PAD_STANDARD_DEFAULT_LAYERS)
        pad.SetDrillSize(pcbnew.wxSize(drill, drill))

        return pad

    def SMDPad(self, w, l, shape=pcbnew.PAD_RECT):
        pad = pcbnew.D_PAD(self.module)
        pad.SetSize(pcbnew.wxSize(l, w))

        pad.SetShape(shape)

        pad.SetAttribute(pcbnew.PAD_SMD)
        pad.SetLayerMask(pcbnew.PAD_SMD_DEFAULT_LAYERS)

        return pad

    def SMTRoundPad(self, size):
        pad = self.SMDPad(size, size, shape=pcbnew.PAD_CIRCLE)
        return pad


class PadArray:

    def __init__(self, pinNames=None):
        self.firstPadNum = 1
        self.pinNames = pinNames

    def SetFirstPadInArray(self, fpNum):
        self.firstPadNum = fpNum

    # HACK! pad should one day have its own clone method
    def ClonePad(self, toClone):

        pad = pcbnew.D_PAD(toClone.GetParent())

        pad.SetSize(toClone.GetSize())
        pad.SetShape(toClone.GetShape())
        pad.SetAttribute(toClone.GetAttribute())
        pad.SetLayerMask(toClone.GetLayerMask())
        pad.SetDrillSize(toClone.GetDrillSize())

        return pad

    def AddPad(self, pad):
        self.pad.GetParent().Add(pad)


class PadGridArray(PadArray):

    def __init__(self, pad, nx, ny, px, py, centre=pcbnew.wxPoint(0, 0),
                 pinNames=None, firstPad=None):
        PadArray.__init__(self, pinNames)
        # this pad is more of a "context", we will use it as a source of
        # pad data, but not actually add it
        self.pad = pad
        self.firstPad = firstPad
        self.nx = int(nx)
        self.ny = int(ny)
        self.px = px
        self.py = py
        self.centre = centre

    # handy utility function 1 - A, 2 - B, 26 - AA, etc
    # aIndex = 0 for 0 - A
    # alphabet = set of allowable chars if not A-Z,
    #            eg ABCDEFGHJKLMNPRTUVWY for BGA
    def AlphaNameFromNumber(self, n, aIndex=1,
                            alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):

        div, mod = divmod(n - aIndex, len(alphabet))
        alpha = alphabet[mod]

        if div > 0:
            return self.AlphaNameFromNumber(div, aIndex, alphabet) + alpha

        return alpha

    # right to left, top to bottom
    def NamingFunction(self, x, y):
        return self.firstPadNum + (self.nx * y + x)

    #relocate the pad and add it as many times as we need
    def AddPadsToModule(self, dc):

        pin1posX = self.centre.x - self.px * (self.nx - 1) / 2
        pin1posY = self.centre.y - self.py * (self.ny - 1) / 2

        for x in range(0, self.nx):

            posX = pin1posX + (x * self.px)

            for y in range(self.ny):
                posY = pin1posY + (self.py * y)

                pos = dc.TransformPoint(posX, posY)

                if (self.firstPad and x == 0 and y == 0):
                    pad = self.firstPad
                else:
                    pad = self.pad

                # THIS DOESN'T WORK YET!
                # pad = self.pad.Clone()
                pad = self.ClonePad(pad)

                pad.SetPos0(pos)
                pad.SetPosition(pos)

                if self.pinNames is None:
                    pad.SetPadName(str(self.NamingFunction(x, y)))
                else:
                    pad.SetPadName(self.pinNames)

                self.AddPad(pad)


class PadLineArray(PadGridArray):

    def __init__(self, pad, n, pitch, isVertical,
                 centre=pcbnew.wxPoint(0, 0), pinNames=None, firstPad=None):

        if isVertical:
            PadGridArray.__init__(self, pad, 1, n, 0, pitch, centre,
                                  pinNames, firstPad)
        else:
            PadGridArray.__init__(self, pad, n, 1, pitch, 0, centre,
                                  pinNames, firstPad)
