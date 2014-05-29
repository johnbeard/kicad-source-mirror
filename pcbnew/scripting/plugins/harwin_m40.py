from __future__ import division

import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import smd_inline_headers

class HarwinM40Wizard(smd_inline_headers.SMDInlineHeader):

    def HaveRaOption(self):
        return True

    def HaveSMDOption(self):
        return True

    def GetName(self):
        return "Harwin M40"

    def GetDescription(self):
        return "Harwin M40 1.00mm SMD headers"

    def GetReference(self):

        if self.RightAngled():
            partNum = "401"
        else:
            partNum = "301"

        ref = "Harwin_M40-%s%02d46" % (partNum, self.N())
        return HFPW.ConnectorWizard.GetReference(self, ref, self.N(), [])

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
        return smd_inline_headers.DoubleSupport(self, pcbnew.FromMM(0.7),
                                pcbnew.FromMM(1.2), pcbnew.FromMM(1.8))

    def AddDecoration(self):
        if self.IsSMD():
            self.OpenTeeDecoration()

    def GetPadRowOffsets(self):

        if not self.IsSMD():
            return []

        if self.RightAngled():
            vsep = fmm(4 - 1.8/2)
        else:
            vsep = fmm(2.6 - 1.8/2)

        return [-vsep]

HarwinM40Wizard().register()
