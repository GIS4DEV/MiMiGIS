
"""
/***************************************************************************
 MinimalGIS
                                 A QGIS plugin
 This plugin contains minimal GIS tools for teaching introductory GIS.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-01-29
        copyright            : (C) 2021 by Maja Cannavo and Joseph Holler
        email                : mcannavo@middlebury.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Maja Cannavo and Joseph Holler'
__date__ = '2021-02-01'
__copyright__ = '(C) 2021 by Maja Cannavo and Joseph Holler'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
from qgis import processing
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                        QgsProcessingException,
                        QgsProcessingParameters,
                        QgsProcessingAlgorithm,
                        QgsProcessingMultiStepFeedback,
                        QgsProcessingParameterString,
                        QgsProcessingParameterField,
                        QgsProcessingParameterFeatureSink,
                        QgsExpression,
                        QgsFeature,
                        QgsCoordinateReferenceSystem,
                        QgsProcessingParameterFeatureSource,
                        QgsProcessingUtils)

# the path of the Minimal GIS plugin folder
minimal_gis_path = os.path.dirname(__file__)


class DirectionDistanceAlgorithm(QgsProcessingAlgorithm):
    # This is the class that contains all the information for our algorithm.
    # It extends the QgsProcessingAlgorithm class.

    # allow easier access to input
    INPUT = 'INPUT'

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'dirdist'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return 'Direction and Distance'

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        # leave as empty string because we don't need groups
        return ''

    def shortHelpString(self):
        """
        Returns a localized short help string for the algorithm.
        """
        return self.tr('Calculates the distance and direction from an origin to a set of  input features.\n\
            Input layer:\nLayer of features for which to calculate the direction and distance from the origin.\n\
            Prefix:\nAlgorithm creates two new fields, one with suffix \'Dist\' for Distance\
            and one with suffix \'Dir\' for Direction. Enter a prefix to use for the field names,\
            such that you will not create duplicate fields in your output.\n\
            Output:\nNew layer with direction and distance fields.\n\
            Algorithm authors: Maja Cannavo and Joseph Holler')

    def helpUrl(self):
        return 'https://github.com/GIS4DEV/QGISmiddleburyAlgs'

    def createInstance(self):
        return DirectionDistanceAlgorithm()

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def icon(self):
        """
        Returns a QIcon object corresponding to the algorithm.
        """
        return QIcon(os.path.join(minimal_gis_path, 'icons', 'compassRose.svg'))

    def initAlgorithm(self, config=None):
        """
        Defines the inputs and outputs of the algorithm.
        """

        # input layer
        self.addParameter(
            # because we use QgsProcessingParameterFeatureSource as input,
            # we will get the checkbox for "Selected Features Only" in the dialog
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Input Layer'),
                # type is vector
                [QgsProcessing.TypeVectorAnyGeometry])
            )

        # origin
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'ORIGIN',
                'Origin',
                # type is vector
                [QgsProcessing.TypeVectorAnyGeometry])
            )

        # prefix
        self.addParameter(
            QgsProcessingParameterString(
                'PREFIX',
                'Prefix',
                defaultValue='origin')
            )

        # output
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                'OUTPUT',
                self.tr('Output')
                )
            )

    def processAlgorithm(self, parameters, context, feedback):

        # Retrieve the input layer
        inputLayer = self.parameterAsLayer(parameters, self.INPUT, context)

        # If source was not found, throw an exception to indicate that the algorithm
        # encountered a fatal error. The exception text can be any string, but in this
        # case we use the pre-built invalidSourceError method to return a standard
        # helper text for when a source cannot be evaluated
        if inputLayer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        # get names for distance and direction fields
        dir_fieldname = parameters['PREFIX'] + 'Dir'
        dist_fieldname = parameters['PREFIX'] + 'Dist'

        # we want to stop the algorithm as soon as possible if the user cancels
        if feedback.isCanceled():
            return {}

        # centroids
        centroids_result = processing.run('native:centroids',
            {'ALL_PARTS': False,
            'INPUT': parameters['ORIGIN'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Centroids computed.')

        # get mean coordinates from input layer
        meanCoords_result = processing.run('native:meancoordinates',
            {'INPUT': centroids_result['OUTPUT'],
            'UID': None,
            'WEIGHT': None,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Mean coordinates computed.')

        # reproject origin
        reprojectOrigin_result = processing.run('native:reprojectlayer',
            {'INPUT': meanCoords_result['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3395'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Origin reprojected.')

        # add geometry info
        addGeomInfo_result = processing.run("qgis:exportaddgeometrycolumns",
            {'INPUT':reprojectOrigin_result['OUTPUT'],
            'CALC_METHOD':0, # use layer CRS
            'OUTPUT':QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        # report progress
        feedback.setProgressText('Geometry info added.')

        # get x and y coordinates from our new layer, which should have just one feature
        addGeomInfo_layer = QgsProcessingUtils.mapLayerFromString(addGeomInfo_result['OUTPUT'], context)
        feat = addGeomInfo_layer.getFeature(1) # QGIS uses one-based indexing for features in a layer

        # the x- and y-coordinate fields should be the third and fourth, respectively
        # QGIS uses zero-based indexing for attributes of a feature
        xCoord = feat.attributes()[2]
        yCoord = feat.attributes()[3]

        # construct SQL query as string
        sql_query = 'Select *, st_distance(st_transform(st_centroid(geometry), 4326),\
            (select st_transform(geometry, 4326) from input2), true) as '\
            + dist_fieldname + ' from input1'

        # report the SQL query to the user before running the Execute SQL tool
        feedback.setProgressText('\nSQL Query:\n\n' + sql_query + '\n')

        # execute SQL
        executeSQL_result = processing.run('qgis:executesql',
            {'INPUT_DATASOURCES': [inputLayer, meanCoords_result['OUTPUT']],
            'INPUT_GEOMETRY_CRS': None,
            'INPUT_GEOMETRY_FIELD': '',
            'INPUT_GEOMETRY_TYPE': None,
            'INPUT_QUERY': sql_query,
            'INPUT_UID_FIELD': '',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('SQL executed.')

        # add autoincremental field
        addAutoincremental_result = processing.run('native:addautoincrementalfield',
            {'FIELD_NAME': 'originAUTO',
            'GROUP_FIELDS': None,
            'INPUT': executeSQL_result['OUTPUT'],
            'SORT_ASCENDING': True,
            'SORT_EXPRESSION': '',
            'SORT_NULLS_FIRST': False,
            'START': 0,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Autoincremental field added.')

        # reproject layer to EPSG:3395
        reprojectLayer_result = processing.run('native:reprojectlayer',
            {'INPUT': addAutoincremental_result['OUTPUT'],
            'TARGET_CRS': QgsCoordinateReferenceSystem('EPSG:3395'),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Layer reprojected.')

        # construct field calculator formula
        fieldCalc_formula = 'degrees(azimuth(make_point(' + str(xCoord) + ', ' + str(yCoord) + '), centroid($geometry)))'

        # Field calculator
        fieldCalc_result = processing.run('qgis:fieldcalculator',
            {'FIELD_LENGTH': 10,
            'FIELD_NAME': dir_fieldname,
            'FIELD_PRECISION': 6,
            'FIELD_TYPE': 0,
            'FORMULA': fieldCalc_formula,
            'INPUT': reprojectLayer_result['OUTPUT'],
            'NEW_FIELD': True,
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Direction calculated using Field Calc.')

        # Join attributes by field value
        joinByFieldVal_result = processing.run('native:joinattributestable',
            {'DISCARD_NONMATCHING': False,
            'FIELD': 'originAUTO',
            'FIELDS_TO_COPY': dir_fieldname,
            'FIELD_2': 'originAUTO',
            'INPUT': addAutoincremental_result['OUTPUT'],
            'INPUT_2': fieldCalc_result['OUTPUT'],
            'METHOD': 1,
            'PREFIX': QgsExpression('').evaluate(),
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        if feedback.isCanceled():
            return {}

        # report progress
        feedback.setProgressText('Layers joined.')

        # Drop field
        dropField_result = processing.run('qgis:deletecolumn',
            {'COLUMN': 'originAUTO',
            'INPUT': joinByFieldVal_result['OUTPUT'],
            'OUTPUT': parameters['OUTPUT']},
            context=context,
            feedback=feedback,
            is_child_algorithm=True)

        # report progress
        feedback.setProgressText('Final result generated.')

        # return final output
        return {'OUTPUT': dropField_result['OUTPUT']}
