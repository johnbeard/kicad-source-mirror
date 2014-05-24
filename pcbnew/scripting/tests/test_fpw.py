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

        self.x = 0
        self.y = 0

        self.xmax = FMM(225)

        self.xsep = FMM(5)
        self.ysep = FMM(10)

    def newRow(self):
        self.x = 0
        self.y += self.ysep + FMM(4)

    def addModule(self, mod):

        mod.SetPosition(pcbnew.wxPoint(self.margin + self.x, self.margin + self.y))

        #print mod.GetFootprintRect()
        #self.x += mod.GetBoundingBox().GetWidth() + self.xsep

        self.board.Add(mod)

        self.x += FMM(20) + self.xsep #todo get bounding box

        if self.x > self.xmax:
            self.x = 0
            self.y += self.ysep

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

"""
for go in params:
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })
"""

for n in range(2,16):
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": n,
        "*ra": False,
        "*smd": True,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": n,
        "*ra": True,
        "*smd": True,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": n,
        "*ra": False,
        "*smd": False,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(SIH.MolexPicoBladeWizard(), {
        "*n": n,
        "*ra": True,
        "*smd": False,
        "hand soldering ext": 0,
    })

tb.newRow()
"""
for go in params:
    tb.testFP(SIH.HarwinM40Wizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })
"""

tb.board.Save("/tmp/test.kicad_pcb", pcbnew.IO_MGR.KICAD)
