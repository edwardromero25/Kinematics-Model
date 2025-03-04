import numpy as np
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

class DataProcessor:
    def __init__(self, innerV, outerV, maxSeg, startAnalysis, endAnalysis):
        self.innerV = innerV
        self.outerV = outerV
        self.minSeg = 0
        self.maxSeg = maxSeg
        self.endTime = int(self.maxSeg * 3600)
        self.startAnalysis = startAnalysis
        self.endAnalysis = endAnalysis
        self.startSeg = int(self.startAnalysis * 3600) if self.startAnalysis is not None else None
        self.endSeg = int(self.endAnalysis * 3600) if self.endAnalysis is not None else None
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
        magSegList = magList[self.minSeg:self.endTime]
        if len(magList) < self.minSeg:
            print("\nERROR: Segment begins after data ends - " + str(len(magList)) + " sec\n")
            sys.exit()
        elif len(magSegList) < (self.endTime - self.minSeg):
            print("\nWARNING: Not enough data for segment - " + str(len(magList)) + " sec\n")
        avgMagFull = np.mean(magList[self.minSeg:self.endTime])
    
        if self.startSeg is not None and self.endSeg is not None:
            magSegListAnalysis = magList[self.startSeg:self.endSeg]
            if len(magList) < self.startSeg:
                print("\nERROR: Segment begins after data ends - " + str(len(magList)) + " sec\n")
                sys.exit()
            elif len(magSegListAnalysis) < (self.endSeg - self.startSeg):
                print("\nWARNING: Not enough data for analysis segment - " + str(len(magList)) + " sec\n")
            avgMagAnalysis = np.mean(magList[self.startSeg:self.endSeg])
        else:
            avgMagAnalysis = None

        return avgMagFull, avgMagAnalysis

    def getDistribution(self):
        path = PathVisualization(self.innerV, self.x, self.y, self.z)
        disScore = path.getDistribution()
        return disScore

class PathVisualization:
    def __init__(self, ID, x, y, z, saveFile=''):
        self.ID = ID

        self.x = x
        self.y = y
        self.z = z

        self.pathCoords = list(zip(self.x, self.y, self.z))
        self.num_points = 1000

        self.saveFile = saveFile

    def __createSphere(self):
        golden_r = (np.sqrt(5.0) + 1.0) / 2.0            
        golden_a = (2.0 - golden_r) * (2.0 * np.pi)     

        Xs, Ys, Zs = [], [], []
        
        for i in range(self.num_points):
            ys = 1 - (i / float(self.num_points - 1)) * 2
            radius = np.sqrt(1 - ys * ys)

            theta = golden_a * i

            xs = np.cos(theta) * radius
            zs = np.sin(theta) * radius

            Xs.append(xs)
            Ys.append(ys)
            Zs.append(zs)

        return(Xs, Ys, Zs)

    def __splitSphere(self, sphereCoords):
        octants = {'posI':[], 'posII':[], 'posIII':[], 'posIV':[], 'negI':[], 'negII':[], 'negIII':[], 'negIV':[]}
        
        for row in sphereCoords:
            if (row[2] > 0):
                if (row[1] > 0):
                    if (row[0] > 0):
                        octants['posI'].append(row)
                    else:
                        octants['posII'].append(row)
                elif (row[0] > 0):
                    octants['posIV'].append(row)
                else: 
                    octants['posIII'].append(row)
            else:
                if (row[1] > 0):
                    if (row[0] > 0):
                        octants['negI'].append(row)
                    else:
                        octants['negII'].append(row)
                elif (row[0] > 0):
                    octants['negIV'].append(row)
                else:
                    octants['negIII'].append(row)
        
        return(octants)

    def __getPathOctant(self, pathRow):
        if (pathRow[2] > 0):
            if (pathRow[1] > 0):
                if (pathRow[0] > 0):
                    return 'posI'
                else:
                    return 'posII'
            elif (pathRow[0] > 0):
                return 'posIV'
            else: 
                return 'posIII'
        else:
            if (pathRow[1] > 0):
                if (pathRow[0] > 0):
                    return 'negI'
                else:
                    return 'negII'
            elif (pathRow[0] > 0):
                return 'negIV'
            else:
                return 'negIII'

    def __getDistanceBetween(self, pathTupleCoords, sphereTupleCoords):
        pathX, pathY, pathZ = pathTupleCoords
        sphereX, sphereY, sphereZ = sphereTupleCoords

        diffX = pathX - sphereX
        diffY = pathY - sphereY
        diffZ = pathZ - sphereZ

        sumSquares = diffX ** 2 + diffY ** 2 + diffZ ** 2
        dist = np.sqrt(sumSquares)

        return dist

    def __getDistributionNum(self, sphereCoords):
        octants = self.__splitSphere(sphereCoords)
        
        pathMap = {} 
        repeatTime = -1

        for pathRow in self.pathCoords:
            pathOctant = self.__getPathOctant(pathRow)
            sphereCoordsSplit = octants[pathOctant]
            distDict = {}
            repeatTime += 1

            for sphereRow in sphereCoordsSplit:
                dist = self.__getDistanceBetween(pathRow, sphereRow) 
                distDict[sphereRow] = dist 
                    
            rankedDist = sorted(distDict.items(), key=lambda x:x[1]) 
            segmentVertices = (rankedDist[0][0], rankedDist[1][0], rankedDist[2][0]) 
            
            pathMap[segmentVertices] = pathMap.get(segmentVertices, []) + [repeatTime] 
        
        return(len(pathMap))

    def getDistribution(self):
        Xsphere, Ysphere, Zsphere = self.__createSphere()
        sphereCoords = list(zip(Xsphere, Ysphere, Zsphere))
        score = self.__getDistributionNum(sphereCoords)
        return score
    
    def formatTime(self, time):
        startTime = time[0]
        fTime = []
        for t in time:
            fTime.append((t - startTime) / 3600)
        return fTime