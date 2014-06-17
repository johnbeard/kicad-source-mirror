from __future__ import division

import pcbnew
from pcbnew import FromMM as fmm

import HelpfulFootprintWizardPlugin as HFPW
import bezier_converter as BC
import xml.etree.ElementTree as ET

class SVGPathConverter(HFPW.HelpfulFootprintWizardPlugin):

    def GetName(self):
        return "SVG Path"

    def GetDescription(self):
        return "Render an SVG's paths into a module"

    def GenerateParameterList(self):

        self.AddParam("SVG", "filename", self.uNatural, "")
        self.AddParam("SVG", "biarc tolerance", self.uNatural, "0.1")

    def GetValue(self):

        return "SVG"

    def GetReferencePrefix(self):
        return ""

    def BuildThisFootprint(self):
        print ET
