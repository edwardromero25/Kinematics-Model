import numpy as np

class FibonacciLattice:
    def __init__(self, ID, x, y, z):
        self.ID = ID

        self.x = x
        self.y = y
        self.z = z

        self.pathCoords = list(zip(self.x, self.y, self.z))
        self.num_points = 1000

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