# -*- coding: utf-8 -*-

"""
***************************************************************************
    ExportGeometryInfo.py
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

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QVariant

from qgis.core import QgsProject, QgsCoordinateTransform, QgsFeature, QgsField, QgsWkbTypes, QgsFeatureSink, QgsProcessingUtils
from qgis.utils import iface

from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.parameters import ParameterVector
from processing.core.parameters import ParameterSelection
from processing.core.outputs import OutputVector
from processing.tools import vector

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]


class ExportGeometryInfo(QgisAlgorithm):

    INPUT = 'INPUT'
    METHOD = 'CALC_METHOD'
    OUTPUT = 'OUTPUT'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'images', 'ftools', 'export_geometry.png'))

    def tags(self):
        return self.tr('export,measurements,areas,lengths,perimeters,latitudes,longitudes,x,y,z,extract,points,lines,polygons').split(',')

    def group(self):
        return self.tr('Vector table tools')

    def __init__(self):
        super().__init__()
        self.calc_methods = [self.tr('Layer CRS'),
                             self.tr('Project CRS'),
                             self.tr('Ellipsoidal')]

        self.addParameter(ParameterVector(self.INPUT,
                                          self.tr('Input layer')))
        self.addParameter(ParameterSelection(self.METHOD,
                                             self.tr('Calculate using'), self.calc_methods, 0))

        self.addOutput(OutputVector(self.OUTPUT, self.tr('Added geom info')))

    def name(self):
        return 'exportaddgeometrycolumns'

    def displayName(self):
        return self.tr('Export/Add geometry columns')

    def processAlgorithm(self, parameters, context, feedback):
        layer = QgsProcessingUtils.mapLayerFromString(self.getParameterValue(self.INPUT), context)
        method = self.getParameterValue(self.METHOD)

        geometryType = layer.geometryType()
        fields = layer.fields()

        export_z = False
        export_m = False
        if geometryType == QgsWkbTypes.PolygonGeometry:
            areaName = vector.createUniqueFieldName('area', fields)
            fields.append(QgsField(areaName, QVariant.Double))
            perimeterName = vector.createUniqueFieldName('perimeter', fields)
            fields.append(QgsField(perimeterName, QVariant.Double))
        elif geometryType == QgsWkbTypes.LineGeometry:
            lengthName = vector.createUniqueFieldName('length', fields)
            fields.append(QgsField(lengthName, QVariant.Double))
        else:
            xName = vector.createUniqueFieldName('xcoord', fields)
            fields.append(QgsField(xName, QVariant.Double))
            yName = vector.createUniqueFieldName('ycoord', fields)
            fields.append(QgsField(yName, QVariant.Double))
            if QgsWkbTypes.hasZ(layer.wkbType()):
                export_z = True
                zName = vector.createUniqueFieldName('zcoord', fields)
                fields.append(QgsField(zName, QVariant.Double))
            if QgsWkbTypes.hasM(layer.wkbType()):
                export_m = True
                zName = vector.createUniqueFieldName('mvalue', fields)
                fields.append(QgsField(zName, QVariant.Double))

        writer = self.getOutputFromName(self.OUTPUT).getVectorWriter(fields, layer.wkbType(), layer.crs(),
                                                                     context)

        ellips = None
        crs = None
        coordTransform = None

        # Calculate with:
        # 0 - layer CRS
        # 1 - project CRS
        # 2 - ellipsoidal

        if method == 2:
            ellips = QgsProject.instance().ellipsoid()
            crs = layer.crs().srsid()
        elif method == 1:
            mapCRS = iface.mapCanvas().mapSettings().destinationCrs()
            layCRS = layer.crs()
            coordTransform = QgsCoordinateTransform(layCRS, mapCRS)

        outFeat = QgsFeature()

        outFeat.initAttributes(len(fields))
        outFeat.setFields(fields)

        features = QgsProcessingUtils.getFeatures(layer, context)
        total = 100.0 / layer.featureCount() if layer.featureCount() else 0
        for current, f in enumerate(features):
            inGeom = f.geometry()

            if method == 1:
                inGeom.transform(coordTransform)

            (attr1, attr2) = vector.simpleMeasure(inGeom, method, ellips, crs)

            outFeat.setGeometry(inGeom)
            attrs = f.attributes()
            attrs.append(attr1)
            if attr2 is not None:
                attrs.append(attr2)

            # add point z/m
            if export_z:
                attrs.append(inGeom.geometry().z())
            if export_m:
                attrs.append(inGeom.geometry().m())

            outFeat.setAttributes(attrs)
            writer.addFeature(outFeat, QgsFeatureSink.FastInsert)

            feedback.setProgress(int(current * total))

        del writer
