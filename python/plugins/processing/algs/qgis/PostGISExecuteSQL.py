# -*- coding: utf-8 -*-

"""
***************************************************************************
    PostGISExecuteSQL.py
    ---------------------
    Date                 : October 2012
    Copyright            : (C) 2012 by Victor Olaya and Carterix Geomatics
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
from builtins import str

__author__ = 'Victor Olaya, Carterix Geomatics'
__date__ = 'October 2012'
__copyright__ = '(C) 2012, Victor Olaya, Carterix Geomatics'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import (QgsApplication,
                       QgsProcessingParameterString)
from processing.algs.qgis.QgisAlgorithm import QgisAlgorithm
from processing.core.GeoAlgorithmExecutionException import GeoAlgorithmExecutionException
from processing.tools import postgis


class PostGISExecuteSQL(QgisAlgorithm):

    DATABASE = 'DATABASE'
    SQL = 'SQL'

    def group(self):
        return self.tr('Database')

    def __init__(self):
        super().__init__()

        db_param = QgsProcessingParameterString(
            self.DATABASE,
            self.tr('Database (connection name)'))
        db_param.setMetadata({
            'widget_wrapper': {
                'class': 'processing.gui.wrappers_postgis.ConnectionWidgetWrapper'}})
        self.addParameter(db_param)
        self.addParameter(QgsProcessingParameterString(self.SQL, self.tr('SQL query')))

    def name(self):
        return 'postgisexecutesql'

    def displayName(self):
        return self.tr('PostGIS execute SQL')

    def processAlgorithm(self, parameters, context, feedback):
        connection = self.parameterAsString(parameters, self.DATABASE, context)
        db = postgis.GeoDB.from_name(connection)

        sql = self.parameterAsString(parameters, self.SQL, context).replace('\n', ' ')
        try:
            db._exec_sql_and_commit(str(sql))
        except postgis.DbError as e:
            raise GeoAlgorithmExecutionException(
                self.tr('Error executing SQL:\n{0}').format(str(e)))
        return {}
