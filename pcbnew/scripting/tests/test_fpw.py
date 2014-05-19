import pcbnew
from pcbnew import FromMM as FMM

import os.path, sys
import itertools

# hack to avoid futzing with pythonpaths for the test
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))

import plugins.smd_inline_headers as SIH

def testFP(fp, params):

    for page in range(fp.GetNumParameterPages()):

        paramList = fp.GetParameterNames(page)
        valList = fp.GetParameterValues(page)

        for k,v in params.iteritems():
            if k in paramList:
                valList[paramList.index(k)] = v

        fp.SetParameterValues(page, valList)

    module = fp.GetModule()

    print module.GetBoard()


tf = {True, False}

params = list(itertools.product(tf, {0, FMM(1)}))

for go in params:
    testFP(SIH.MolexPicoBladeWizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })

for go in params:
    testFP(SIH.HarwinM40Wizard(), {
        "*n": 5,
        "*ra": go[0],
        "hand soldering ext": go[1],
    })
