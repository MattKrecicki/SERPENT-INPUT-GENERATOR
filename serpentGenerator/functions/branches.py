"""branches

Class representing branches in reactor operation conditions. 
Includes types of perturbations and their respective values. 
A container for individual branches. 

email: dan.kotlyar@me.gatech.edu
email: iaguirre6@gatech.edu
"""
import numpy as np
from serpentGenerator.functions.branch import branch
from serpentGenerator.functions.mix import mix
from serpentGenerator.data.materialLibrary import MATLIB
from serpentGenerator.functions.checkerrors import (
    _isinstanceList, _islist
)
class branches:

    def __init__(self, pertFT = None, pertMD= None, pertBPPM = None):
        if (pertFT != None):
            _islist(pertFT, "fuel temp perturbations")
        if (pertMD != None):
            _islist(pertMD, "mod dens perturbations")
        if (pertBPPM != None):
            _islist(pertBPPM, "bppm perturbations")

        self.pertFT = pertFT
        self.pertMD = pertMD
        self.pertBPPM = pertBPPM

        self.isPertFT = True if (pertFT != None) else False
        self.isPertMD = True if (pertMD != None) else False
        self.isPertBPPM = True if (pertBPPM != None) else False

        self.mats = []
        self.branches = {}
        self.nbranches = 0

    def addBranches(self, branches):
        _isinstanceList(branches, branch, "branch list")

        for i in range(0, len(branches)):
            self.branches[branches[i].id] = branches[i]

        self.nbranches = self.nbranches + len(branches)

    def toString(self):
        branchString = ""
        for key in self.branches:
            branchString = branchString + self.branches[key].toString()

        return branchString + "\n"

    @staticmethod
    def branchBuilderPWR(nomFuel = None, nomMod = None, fuelTemps=None, 
        modDens = None, bppms = None):

        isPertFT = True if (fuelTemps != None) else False
        isPertMD = True if (modDens != None) else False
        isPertBPPM = True if (bppms != None) else False

        nfuelt = len(fuelTemps) if (fuelTemps != None) else 1
        nmodd = len(modDens) if (modDens != None) else 1
        nbppm = len(bppms) if (bppms != None) else 1

        numBranches = nfuelt*nmodd*nbppm
        branchs = [None]*numBranches

        branchy = None

        def matsBuilderPWRMB(nomMat, modDens, bppms):
            numMats = nmodd
            numMixs = nmodd*nbppm
            branchMats = [None]*numMats
            branchMixs = [None]*numMixs
            mats = [ [0]*len(bppms) for i in range(len(modDens))]
            mixs = [ [0]*len(bppms) for i in range(len(modDens))]
            counter = 0
            for i in range(0, len(modDens)):
                for j in range(0, len(bppms)):
                    mats[i][j] = nomMat.duplicateMat(nomMat.id+"d"+str(modDens[i]))
                    mats[i][j].set('dens', -1*float(modDens[i]/1000))
                    mixs[i][j] = mix(nomMat.id+"d"+str(modDens[i])+"b"+str(bppms[j]),
                        [mats[i][j], MATLIB['boron']], [-1*(1 - bppms[j]*1e-6),
                        -1*bppms[j]*1e-6])
                    branchMixs[counter] = mixs[i][j]
                    counter = counter + 1
                branchMats[i] = mats[i][0]
            
            branchMats = branchMats+branchMixs
            return mixs, branchMats

        def matsBuilderPWRM(nomMat, modDens):
            numMats = nmodd
            numMixs = nmodd
            branchMats = [None]*numMats
            branchMixs = [None]*numMixs
            mats = [0]*len(modDens)
            mixs = [0]*len(modDens)
            counter = 0
            for i in range(0, len(modDens)):
                mats[i] = nomMat.duplicateMat(nomMat.id+"d"+str(modDens[i]))
                mats[i].set('dens', -1*float(modDens[i]/1000))
                branchMixs[counter] = mats[i]
                counter = counter + 1
                branchMats[i] = mats[i]

            branchMats = branchMats+branchMixs
            return mats, branchMats

        def matsBuilderPWRB(nomMat, bppms):
            numMats = 1
            numMixs = nbppm
            branchMats = [None]*numMats
            branchMixs = [None]*numMixs
            mats = [nomMat]
            mixs = [0]*len(bppms)
            counter = 0
            for j in range(0, len(bppms)):
                mixs[j] = mix(nomMat.id+"b"+str(bppms[j]),
                    [mats[0], MATLIB['boron']], [-1*(1 - bppms[j]*1e-6),
                    -1*bppms[j]*1e-6])
                branchMixs[counter] = mixs[j]
                counter = counter + 1
            
            branchMats = branchMats+branchMixs
            return mixs, branchMats

        def matsBuilderPWRNONE(nomMat):
            return nomMat

        def setBranchesFMB(fuelTemps, modDens, bppms, mixs, branchMats, nomFuel):
            counter = 0
            for i in range(0, len(fuelTemps)):
                for k in range(0, len(modDens)):
                    for o in range(0, len(bppms)):
                        branchs[counter] = branch("f"+str(fuelTemps[i])+"d"
                            +str(modDens[k])+"b"+str(bppms[o]),
                            repmat = [nomMod, mixs[k][o]], 
                            stp = [nomFuel, nomFuel.dens, fuelTemps[i]])

                        counter = counter + 1
            branchy = branches(pertFT=fuelTemps, pertMD=modDens, pertBPPM=bppms)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesFM(fuelTemps, modDens, mixs, branchMats, nomFuel):
            counter = 0
            for i in range(0, len(fuelTemps)):
                for k in range(0, len(modDens)):
                    branchs[counter] = branch("f"+str(fuelTemps[i])+"d"
                        +str(modDens[k]), repmat = [nomMod, mixs[k]], 
                        stp = [nomFuel, nomFuel.dens, fuelTemps[i]])

                    counter = counter + 1
            branchy = branches(pertFT=fuelTemps, pertMD=modDens)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesFB(fuelTemps, bppms,mixs, branchMats, nomFuel):
            counter = 0
            for i in range(0, len(fuelTemps)):
                for o in range(0, len(bppms)):
                    branchs[counter] = branch("f"+str(fuelTemps[i])+"b"
                    +str(bppms[o]), repmat = [nomMod, mixs[o]], 
                        stp = [nomFuel, nomFuel.dens, fuelTemps[i]])
                    counter = counter + 1
            branchy = branches(pertFT=fuelTemps, pertBPPM=bppms)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesMB(modDens, bppms, mixs, branchMats):
            counter = 0
            for k in range(0, len(modDens)):
                for o in range(0, len(bppms)):
                    branchs[counter] = branch("d"+str(modDens[k])+"b"+str(bppms[o]),
                        repmat = [nomMod, mixs[k][o]])

                    counter = counter + 1

            branchy = branches(pertMD=modDens, pertBPPM=bppms)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesF(fuelTemps, branchMats, nomFuel):
            counter = 0
            for i in range(0, len(fuelTemps)):
                branchs[counter] = branch("f"+str(fuelTemps[i]),
                    stp = [nomFuel, nomFuel.dens, fuelTemps[i]])
                counter = counter + 1
            branchy = branches(pertFT=fuelTemps)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesM(modDens, mixs, branchMats):
            counter = 0
            for k in range(0, len(modDens)):
                branchs[counter] = branch("d"+str(modDens[k]),
                    repmat = [nomMod, mixs[k]])

                counter = counter + 1

            branchy = branches(pertMD=modDens)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        def setBranchesB(bppms, mixs, branchMats):
            counter = 0
            for o in range(0, len(bppms)):
                branchs[counter] = branch("b"+str(bppms[o]), 
                    repmat = [nomMod, mixs[o]])
                counter = counter + 1
            branchy = branches(pertBPPM=bppms)
            branchy.addBranches(branchs)
            branchy.mats = branchMats
            return branchy

        if(isPertFT & isPertMD & isPertBPPM):
            mixs, branchMats = matsBuilderPWRMB(nomMod, modDens, bppms)
            branchy = setBranchesFMB(fuelTemps, modDens, bppms, mixs,
                branchMats, nomFuel)
        elif(isPertFT & isPertMD):
            mixs, branchMats = matsBuilderPWRM(nomMod, modDens)
            branchy = setBranchesFM(fuelTemps, modDens, mixs, branchMats, nomFuel)          
        elif(isPertMD & isPertBPPM):
            mixs, branchMats = matsBuilderPWRMB(nomMod, modDens, bppms)
            branchy = setBranchesMB(modDens, bppms, mixs, branchMats)
        elif(isPertFT & isPertBPPM):
            mixs, branchMats = matsBuilderPWRB(nomMod, bppms)
            branchy = setBranchesFB(fuelTemps, bppms, mixs, branchMats, nomFuel)
        elif(isPertFT):
            branchMats = matsBuilderPWRNONE(nomMod)
            branchy = setBranchesF(fuelTemps, branchMats, nomFuel)
        elif(isPertMD):
            mixs, branchMats = matsBuilderPWRM(nomMod, modDens)
            branchy = setBranchesM(modDens, mixs, branchMats)
        elif(isPertBPPM):
            mixs, branchMats = matsBuilderPWRB(nomMod, bppms)
            branchy = setBranchesB(bppms, mixs, branchMats)

        return branchy