import pcbnew
from pcbnew import FromMM as FMM

import os.path, sys
import itertools

# hack to avoid futzing with pythonpaths for the test
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import plugins.smd_inline_headers as SIH

class TestBoard():

    def __init__(self):
        self.board = pcbnew.BOARD()

        self.margin = FMM(30)

        self.x = self.margin
        self.y = self.margin

        self.xmax = 200

        self.xsep = FMM(5)

    def addModule(self, mod):

        mod.SetPosition(pcbnew.wxPoint(self.x, self.y))

        #print mod.GetFootprintRect()
        #self.x += mod.GetBoundingBox().GetWidth() + self.xsep

        self.x += FMM(25)

        self.board.Add(mod)

    def testFP(self, fp, params):

        for page in range(fp.GetNumParameterPages()):

            paramList = fp.GetParameterNames(page)
            valList = fp.GetParameterValues(page)

            for k,v in params.iteritems():
                if k in paramList:
                    valList[paramList.index(k)] = v

            fp.SetParameterValues(page, valList)

        module = fp.GetModule()

        self.addModule(module)

tb = TestBoard()

tf = {True, False}

params = list(itertools.product(tf, {0, FMM(1)}))

for go in params:
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })

for go in params:
    tb.testFP(SIH.HarwinM40Wizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })

tb.board.Save("/tmp/test.kicad_pcb", pcbnew.IO_MGR.KICAD)
