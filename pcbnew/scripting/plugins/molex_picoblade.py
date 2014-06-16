from __future__ import division

import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import smd_inline_headers

class MolexPicoBlade():

    def Manufacturer(self):
        return "Molex"

    def PartRangeName(self):
        return "PicoBlade"

    def GetDescription(self):
        return "Molex PicoBlade 1.25mm shrouded header"

    def GetName(self):
        return "Molex PicoBlade"

class MolexThtVertHeader(MolexPicoBlade,
                            smd_inline_headers.ThtVerticalHeader):

    def GetValue(self):
        ref = "53047-%02d10" % (self.N())

        return HFPW.ConnectorWizard.GetValue(self, ref)

    def SetModule3DModel(self):
        # TODO implement this properly when 3d can be used
        path = "Connectors/conn_df13/df13-%dp-125dsa.wrl" % self.N()
        rot = [0, 0, 180]
        pos = [0, -0.0187, 0]

    def GetComponentParams(self):

        return {
            'E1': fmm(3.2 - 1.15),
            'E2': fmm(1.15),
            'D1': fmm(4.25 - 1.25)/2,
            'e' : 0,
            'd' : fmm(1.25),
            'b' : fmm(0.5),
            'B' : fmm(0.8),
            'ne' : 1,
            'nd' : self.N()
            }


class MolexThtRaHeader(MolexPicoBlade,
                       smd_inline_headers.ThtRaHeaderShrouded):

    def GetValue(self):
        ref = "53048-%02d10" % (self.N())

        return HFPW.ConnectorWizard.GetValue(self, ref)

    def GetComponentParams(self):

        return {
            'E1': fmm(1.05),
            'E2': fmm(5.5 - 1.05),
            'e' : 0,
            'd' : fmm(1.25),
            'b' : fmm(0.5),
            'E' : fmm(3.5),
            'D1' : fmm(1.5),
            'B' : fmm(0.8)
            }

class MolexSmdHeader(MolexPicoBlade,
                        smd_inline_headers.SMDInlineHeaderWithWings):

    def HaveRaOption(self):
        return True

    def GetValue(self):
        pn = "53261" if self.RightAngled() else "53398"
        ref = "_%s-%02d71" % (pn, self.N())

        return HFPW.ConnectorWizard.GetValue(self, ref)


    def GetComponentParams(self):

        return {
            'A': fmm(0.8),
            'B': fmm(1.6) if self.RightAngled() else fmm(1.3),
            'C' : fmm(2.1),
            'D' : fmm(3),
            'E' : fmm(0.6),
            'F' : fmm(1.5),
            'G' : fmm(1.5),
            'H' : fmm(0.4),
            'J' : fmm(0.4),
            'd' : fmm(1.25),
            }
