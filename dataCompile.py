import numpy as np
import matplotlib.pyplot as plt
import math
import sys

class Sim:
    def gVectorX(self, timeInSeconds, localInnerInRadSec, localOuterInRadSec):
        ret = math.sin(localOuterInRadSec*timeInSeconds)*math.cos(localInnerInRadSec*timeInSeconds)
        return ret

    def gVectorY(self, timeInSeconds, localOuterInRadSec):
        ret = math.cos(localOuterInRadSec*timeInSeconds)
        return ret

    def gVectorZ(self, timeInSeconds, localInnerInRadSec, localOuterInRadSec):
        ret = math.sin(localOuterInRadSec*timeInSeconds)*math.sin(localInnerInRadSec*timeInSeconds)
        return ret

    def RPMtoRadSec(self, RPM):
        ret = RPM * (math.pi / 30)
        return ret

    def gVectorData(self, startTimeInSeconds, endTimeInSeconds, innerRPM, outerRPM):
        innerInRadSec = self.RPMtoRadSec(innerRPM)
        outerInRadSec = self.RPMtoRadSec(outerRPM)
        timeArray, xArray, yArray, zArray = [], [], [], []
        for t in range(startTimeInSeconds, endTimeInSeconds + 1):
            timeArray.append(t)
            xArray.append(self.gVectorX(t, innerInRadSec, outerInRadSec))
            yArray.append(self.gVectorY(t, outerInRadSec))
            zArray.append(self.gVectorZ(t, innerInRadSec, outerInRadSec))
        data = timeArray, xArray, yArray, zArray
        return data

class MagnitudeAnalysis:
    def __init__(self, innerV, outerV, maxSeg, startAnalysis, endAnalysis):
        self.innerV = innerV
        self.outerV = outerV
        self.maxSeg = maxSeg
        self.endTime = int(self.maxSeg * 3600)
        self.startAnalysis = startAnalysis
        self.endAnalysis = endAnalysis
        self.startSeg = int(self.startAnalysis * 3600)
        self.endSeg = int(self.endAnalysis * 3600)
        self.minSeg = 0
        self.time, self.x, self.y, self.z = self._getSimAccelData()

    def _getSimAccelData(self):
        simInnerV = float(self.innerV)
        simOuterV = float(self.outerV)
        vectorSim = Sim()
        time, x, y, z = vectorSim.gVectorData(0, self.endTime, simInnerV, simOuterV)
        return time, x, y, z

    def _getTimeAvg(self):
        xTimeAvg = []
        xTempList = []
        for xIter in self.x:
            xTempList.append(xIter)
            xTimeAvg.append(np.mean(xTempList))
        
        yTimeAvg = []
        yTempList = []
        for yIter in self.y:
            yTempList.append(yIter)
            yTimeAvg.append(np.mean(yTempList))

        zTimeAvg = []
        zTempList = []
        for zIter in self.z:
            zTempList.append(zIter)
            zTimeAvg.append(np.mean(zTempList))
        
        return xTimeAvg, yTimeAvg, zTimeAvg

    def _getMagnitude(self, xTimeAvg, yTimeAvg, zTimeAvg):
        magList = []

        for i in range(len(self.x)):
            xIter = xTimeAvg[i]
            yIter = yTimeAvg[i]
            zIter = zTimeAvg[i]

            mag = (xIter ** 2 + yIter ** 2 + zIter ** 2) ** 0.5
            magList.append(mag)

        return magList

    def _getMagSeg(self, magList):
        magSegList = magList[self.minSeg:self.maxSeg]
        if len(magList) < self.minSeg:
            print("\nERROR: Segment begins after data ends - " + str(len(magList)) + " sec\n")
            sys.exit()
        elif len(magSegList) < (self.maxSeg - self.minSeg):
            print("\nWARNING: Not enough data for segment - " + str(len(magList)) + " sec\n")
        avgMagFull = np.mean(magList[self.minSeg:self.endTime])
    
        magSegListAnalysis = magList[self.startSeg:self.endSeg]
        if len(magList) < self.startSeg:
            print("\nERROR: Segment begins after data ends - " + str(len(magList)) + " sec\n")
            sys.exit()
        elif len(magSegListAnalysis) < (self.endSeg - self.startSeg):
            print("\nWARNING: Not enough data for analysis segment - " + str(len(magList)) + " sec\n")
        avgMagAnalysis = np.mean(magList[self.startSeg:self.endSeg])

        return avgMagFull, avgMagAnalysis

    def formatTime(self, time):
        startTime = time[0]
        fTime = []
        for t in time:
            fTime.append((t - startTime) / 3600)
        return fTime

    def createMagFig(self, magnitude, time, startAnalysis, endAnalysis, avgMagSeg, avgMagAnalysis, innerV, outerV, mode='save', title=True):
        fTime = self.formatTime(time)
        
        startIndex = next(i for i, t in enumerate(fTime) if t >= startAnalysis)
        endIndex = next(i for i, t in enumerate(fTime) if t >= endAnalysis)

        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.yscale('log')

        if title:
            fig.suptitle(f"Magnitude vs. Time (I={innerV}, O={outerV})")

        ax.plot(fTime, magnitude, color='dimgray', label="Average Magnitude: " + f"{avgMagSeg:.4g}")

        ax.axvline(x=startAnalysis, color='blue', linestyle='--')
        ax.axvline(x=endAnalysis, color='blue', linestyle='--')

        ax.plot(fTime[startIndex:endIndex], magnitude[startIndex:endIndex], color='blue', label="Average Magnitude: " + f"{avgMagAnalysis:.4g}")

        ax.legend()
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Magnitude (g)')

        if mode == 'save': 
            plt.savefig('timeMagFig.png')
        elif mode == 'show':
            plt.show()
        else:
            plt.savefig('timeMagFig.png')
            plt.show()