import pcbnew
from pcbnew import FromMM as FMM

import os, sys
import re
import itertools

# hack to avoid futzing with pythonpaths for the test
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import plugins.molex_picoblade as MPB
import plugins.harwin_m40 as HM40

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

        self.x += FMM(25) + self.xsep #todo get bounding box

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

    def ripOutAndSaveModules(self, filename, modPath):
        # hack to rip out modules from board
        brd = open(filename, 'r')

        mod = ''
        inMod = False

        for line in brd:
            if line.startswith("  (module"):
                inMod = True

                line = re.sub(r"\(t(stamp|edit).*?\)", "", line)

                ref = line.split()[1]

            if inMod:
                if not line.startswith("    (at "):
                    mod += line[2:].rstrip() + "\n"

                if line.startswith("  )"):
                    inMod = False

                    modFile = os.path.join(modPath, "%s.%s" % (ref, "kicad_mod"))

                    f = open(modFile, 'w')
                    f.write(mod)
                    f.close()

                    mod = ''


tb = TestBoard()

tf = {True, False}

params = list(itertools.product(tf, {0, FMM(1)}))

for n in range(2,16):
    tb.testFP(MPB.MolexSmdHeader(), {
        "*n": n,
        "*ra": False,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(MPB.MolexSmdHeader(), {
        "*n": n,
        "*ra": True,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(MPB.MolexThtVertHeader(), {
        "*n": n,
        "hand soldering ext": 0,
    })

tb.newRow()

for n in range(2,16):
    tb.testFP(MPB.MolexThtRaHeader(), {
        "*n": n,
        "hand soldering ext": 0,
    })

tb.newRow()

'''
for n in range(2,16):
    tb.testFP(HM40.HarwinM40Wizard(), {
        "*n": n,
        "*ra": True,
        "*smd": True,
        "hand soldering ext": 0,
    })
'''

tb.newRow()

filename = "/tmp/test.kicad_pcb"
modPath = "/tmp/molex"

if not os.path.isdir(modPath):
    os.makedirs(modPath)

tb.board.Save(filename, pcbnew.IO_MGR.KICAD)

tb.ripOutAndSaveModules(filename, modPath)
