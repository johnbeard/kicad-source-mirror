
import pcbnew

class PadMaker:
    """
    Useful construction functions for common types of pads
    """

    def __init__(self, module):
        self.module = module

    def THPad(self, w, l, drill, shape = pcbnew.PAD_OVAL):
        pad = pcbnew.D_PAD(self.module)

        pad.SetSize(pcbnew.wxSize(l, w))

        pad.SetShape(shape)

        pad.SetAttribute(pcbnew.PAD_STANDARD)
        pad.SetLayerMask(pcbnew.PAD_STANDARD_DEFAULT_LAYERS)
        pad.SetDrillSize(pcbnew.wxSize(drill, drill))

        return pad

    def SMDPad(self, w, l, shape = pcbnew.PAD_RECT):
        pad = pcbnew.D_PAD(self.module)
        pad.SetSize(pcbnew.wxSize(l, w))

        pad.SetShape(shape)

        pad.SetAttribute(pcbnew.PAD_SMD)
        pad.SetLayerMask(pcbnew.PAD_SMD_DEFAULT_LAYERS)

        return pad

    def SMTRoundPad(self, size):
        pad = self.SMDPad(size, size, shape = pcbnew.PAD_CIRCLE)
        return pad

class PadArray:

    def __init__(self, pinNames=None):
        self.firstPad = 1
        self.pinNames = pinNames

    def SetFirstPadInArray(self, fpNum):
        self.firstPad = fpNum

    # HACK! pad should one day have its own clone method
    def ClonePad(self):

        pad = pcbnew.D_PAD(self.pad.GetParent())

        pad.SetSize(self.pad.GetSize())
        pad.SetShape(self.pad.GetShape())
        pad.SetAttribute(self.pad.GetAttribute())
        pad.SetLayerMask(self.pad.GetLayerMask())
        pad.SetDrillSize(self.pad.GetDrillSize())

        return pad

    def AddPad(self, pad):
        self.pad.GetParent().Add(pad)

class PadGridArray(PadArray):

    def __init__(self, pad, nx, ny, px, py, centre=pcbnew.wxPoint(0,0), pinNames=None):
        PadArray.__init__(self, pinNames)
        # this pad is more of a "context", we will use it as a source of
        # pad data, but not actually add it
        self.pad = pad
        self.nx = int(nx)
        self.ny = int(ny)
        self.px = px
        self.py = py
        self.centre = centre

    # handy utility function 1 - A, 2 - B, 26 - AA, etc
    # aIndex = 0 for 0 - A
    # alphabet = set of allowable chars if not A-Z, eg ABCDEFGHJKLMNPRTUVWY for BGA
    def AlphaNameFromNumber(self, n, aIndex = 1, alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"):

        div, mod = divmod(n - aIndex, len(alphabet))
        alpha = alphabet[mod]

        if div > 0:
            return self.AlphaNameFromNumber(div, aIndex, alphabet) + alpha;

        return alpha;

    # right to left, top to bottom
    def NamingFunction(self, x, y):
        return self.firstPad + (self.nx * y + x)

    #relocate the pad and add it as many times as we need
    def AddPadsToModule(self):

        pin1posX = self.centre.x - self.px * (self.nx - 1) / 2
        pin1posY = self.centre.y - self.py * (self.ny - 1) / 2

        for x in range(0, self.nx):

            posX = pin1posX + (x * self.px)

            for y in range(self.ny):
                posY = pin1posY + (self.py * y)

                pos = pcbnew.wxPoint(posX, posY)

                # THIS DOESN'T WORK yet!
                #pad = self.pad.Clone()
                pad = self.ClonePad()

                pad.SetPos0(pos)
                pad.SetPosition(pos)

                if self.pinNames == None:
                    pad.SetPadName(str(self.NamingFunction(x,y)))
                else:
                    pad.SetPadName(self.pinNames)

                self.AddPad(pad)

class PadLineArray(PadGridArray):

    def __init__(self, pad, n, pitch, isVertical, centre=pcbnew.wxPoint(0,0), pinNames=None):

        if isVertical:
            PadGridArray.__init__(self, pad, 1, n, 0, pitch, centre, pinNames)
        else:
            PadGridArray.__init__(self, pad, n, 1, pitch, 0, centre, pinNames)
