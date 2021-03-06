# -*- coding: utf-8 -*-

"""
***************************************************************************
    NearestNeighbourAnalysis.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from builtins import next
from builtins import str

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import math
import codecs

from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsFeatureRequest, QgsFeature, QgsDistanceArea, QgsProcessingUtils

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.outputs import OutputHTML
from processing.core.outputs import OutputNumber
from processing.tools import dataobjects

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class NearestNeighbourAnalysis(QgisAlgorithm):

    POINTS = 'POINTS'
    OUTPUT = 'OUTPUT'
    OBSERVED_MD = 'OBSERVED_MD'
    EXPECTED_MD = 'EXPECTED_MD'
    NN_INDEX = 'NN_INDEX'
    POINT_COUNT = 'POINT_COUNT'
    Z_SCORE = 'Z_SCORE'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'neighbour.png'))

    def group(self):
        return self.tr('Vector analysis tools')

    def __init__(self):
        super().__init__()
        self.addParameter(ParameterVector(self.POINTS,
                                          self.tr('Points'), [dataobjects.TYPE_VECTOR_POINT]))

        self.addOutput(OutputHTML(self.OUTPUT, self.tr('Nearest neighbour')))

        self.addOutput(OutputNumber(self.OBSERVED_MD,
                                    self.tr('Observed mean distance')))
        self.addOutput(OutputNumber(self.EXPECTED_MD,
                                    self.tr('Expected mean distance')))
        self.addOutput(OutputNumber(self.NN_INDEX,
                                    self.tr('Nearest neighbour index')))
        self.addOutput(OutputNumber(self.POINT_COUNT,
                                    self.tr('Number of points')))
        self.addOutput(OutputNumber(self.Z_SCORE, self.tr('Z-Score')))

    def name(self):
        return 'nearestneighbouranalysis'

    def displayName(self):
        return self.tr('Nearest neighbour analysis')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.POINTS), context)
        output = self.getOutputValue(self.OUTPUT)

        spatialIndex = QgsProcessingUtils.createSpatialIndex(layer, context)

        neighbour = QgsFeature()
        distance = QgsDistanceArea()

        sumDist = 0.00
        A = layer.extent()
        A = float(A.width() * A.height())

        features = QgsProcessingUtils.getFeatures(layer, context)
        count = QgsProcessingUtils.featureCount(layer, context)
        total = 100.0 / count if count else 1
        for current, feat in enumerate(features):
            neighbourID = spatialIndex.nearestNeighbor(
                feat.geometry().asPoint(), 2)[1]
            request = QgsFeatureRequest().setFilterFid(neighbourID).setSubsetOfAttributes([])
            neighbour = next(layer.getFeatures(request))
            sumDist += distance.measureLine(neighbour.geometry().asPoint(),
                                            feat.geometry().asPoint())

            feedback.setProgress(int(current * total))

        do = float(sumDist) / count
        de = float(0.5 / math.sqrt(count / A))
        d = float(do / de)
        SE = float(0.26136 / math.sqrt(count ** 2 / A))
        zscore = float((do - de) / SE)

        data = []
        data.append('Observed mean distance: ' + str(do))
        data.append('Expected mean distance: ' + str(de))
        data.append('Nearest neighbour index: ' + str(d))
        data.append('Number of points: ' + str(count))
        data.append('Z-Score: ' + str(zscore))

        self.createHTML(output, data)

        self.setOutputValue(self.OBSERVED_MD, float(data[0].split(': ')[1]))
        self.setOutputValue(self.EXPECTED_MD, float(data[1].split(': ')[1]))
        self.setOutputValue(self.NN_INDEX, float(data[2].split(': ')[1]))
        self.setOutputValue(self.POINT_COUNT, float(data[3].split(': ')[1]))
        self.setOutputValue(self.Z_SCORE, float(data[4].split(': ')[1]))

    def createHTML(self, outputFile, algData):
        with codecs.open(outputFile, 'w', encoding='utf-8') as f:
            f.write('<html><head>')
            f.write('<meta http-equiv="Content-Type" content="text/html; \
                    charset=utf-8" /></head><body>')
            for s in algData:
                f.write('<p>' + str(s) + '</p>')
            f.write('</body></html>')
