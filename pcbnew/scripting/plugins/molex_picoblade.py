
import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import smd_inline_headers

class MolexPicoBladeWizard(smd_inline_headers.SMDInlineHeader):

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

        if self.RightAngled():
            partNum = "53261" if self.IsSMD() else "53048"
        else:
            partNum = "53398" if self.IsSMD() else "53047"

        ref = "MOLEX_%s-%02d%s" % (partNum, self.N(), suffix)

        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), [])

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

        return smd_inline_headers.DoubleSupport(self, pcbnew.FromMM(3.6 - 2.1),
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

        self.draw.MirroredPolyline(pts, mirrorX=True)
        self.draw.MirroredPolyline(pts2, mirrorX=True)

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

        self.draw.MirroredPolyline(pts, mirrorX=True)
        self.draw.Polyline(pts2)

        self.draw.Value(0, fmm(-2.8), self.TextSize())
        self.draw.Reference(0, fmm(2.8), self.TextSize())

        self.DrawPin1Arrow(-rl/2, -fmm(1.6), self.draw.dDOWN);

    def DrawRATHTDecoration(self):
        rl = self.RowLength()

        body_width2 = rl/2 + fmm(1.5)

        pts = [ [0,                         fmm(2.75)],
                [body_width2,               fmm(2.75)],
                [body_width2,               -fmm(2.75)],
                [rl/2 + self.GetPitch()/2,  -fmm(2.75)],
                [rl/2 + self.GetPitch()/2,  -fmm(1.8)]
            ]

        self.draw.MirroredPolyline(pts, mirrorX=True)

        self.draw.SetWidth(fmm(0.1))

        self.DrawRAPinOpening(fmm(2.75), body_width2)

        self.draw.HLine(-rl/2 - fmm(1.5), -fmm(1.7), rl + fmm(3))

        self.draw.Value(0, fmm(-3.5), self.TextSize())
        self.draw.Reference(0, fmm(3.7), self.TextSize())

        self.DrawPin1Arrow(-rl/2, -fmm(3), self.draw.dDOWN);

        self.SawtoothLine(self.N(), self.GetPitch(), fmm(-1.7), fmm(-2.3), fmm(0.6), fmm(0.3))

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

        self.draw.MirroredPolyline(pts, mirrorX=True)
        self.draw.MirroredPolyline(pts2, mirrorX=True)

        for n in range(self.N()):
            self.DrawPinSide(fmm(0.15), fmm(1.25), fmm(0.4),
                    n * self.GetPitch() - rl2, ybottom - fmm(2.1))

    def DrawWings(self):
        rl = self.RowLength()

        wing = [[rl/2 + fmm(1.3),    fmm(1.6)],
                [rl/2 + fmm(3.7),    fmm(1.6)],
                [rl/2 + fmm(3.7),    fmm(-1.6)],
                [rl/2 + fmm(1.3),    fmm(-1.6)]]

        self.draw.MirroredPolyline(wing, mirrorX=True)

    def DrawPinSide(self, w, l, chamferLen, x, y):

        pts = [ [x - w,  y],
                [x - w,  y + l - chamferLen],
                [x,      y + l],
                [x + w,  y + l - chamferLen],
                [x + w,  y]]

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

            self.draw.Polyline(pts)

MolexPicoBladeWizard().register()
