/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/gui/qgsmaptoolcapture.h                                          *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/






class QgsMapToolCapture : QgsMapToolAdvancedDigitizing
{

%TypeHeaderCode
#include "qgsmaptoolcapture.h"
%End
  public:
    QgsMapToolCapture( QgsMapCanvas *canvas, QgsAdvancedDigitizingDockWidget *cadDockWidget, CaptureMode mode = CaptureNone );
%Docstring
constructor
%End

    virtual ~QgsMapToolCapture();

    virtual void activate();
    virtual void deactivate();

    int addCurve( QgsCurve *c );
%Docstring
Adds a whole curve (e.g. circularstring) to the captured geometry. Curve must be in map CRS
 :rtype: int
%End

    const QgsCompoundCurve *captureCurve() const;
%Docstring
 Get the capture curve

 :return: Capture curve
 :rtype: QgsCompoundCurve
%End

    virtual void cadCanvasMoveEvent( QgsMapMouseEvent *e );

    virtual void keyPressEvent( QKeyEvent *e );
%Docstring
 Intercept key events like Esc or Del to delete the last point
 \param e key event
%End

    virtual bool eventFilter( QObject *obj, QEvent *e );

    void deleteTempRubberBand();
%Docstring
 Clean a temporary rubberband
%End

  protected:

    int nextPoint( const QgsPoint &mapPoint, QgsPoint &layerPoint );
%Docstring
 :rtype: int
%End

    int nextPoint( QPoint p, QgsPoint &layerPoint, QgsPoint &mapPoint );
%Docstring
 :rtype: int
%End

    int fetchLayerPoint( const QgsPointLocator::Match &match, QgsPoint &layerPoint );
%Docstring
 :rtype: int
%End

    int addVertex( const QgsPointXY &point );
%Docstring
 :rtype: int
%End

    int addVertex( const QgsPointXY &mapPoint, const QgsPointLocator::Match &match );
%Docstring
 Variant to supply more information in the case of snapping
 \param mapPoint The vertex to add in map coordinates
 \param match Data about the snapping match. Can be an invalid match, if point not snapped.
.. versionadded:: 2.14
 :rtype: int
%End

    void undo();
%Docstring
Removes the last vertex from mRubberBand and mCaptureList
%End

    void startCapturing();
%Docstring
 Start capturing
%End

    bool isCapturing() const;
%Docstring
 Are we currently capturing?

 :return: Is the tool in capture mode?
 :rtype: bool
%End

    void stopCapturing();
%Docstring
 Stop capturing
%End

    int size();
%Docstring
 Number of points digitized

 :return: Number of points
 :rtype: int
%End

    QList<QgsPointXY> points();
%Docstring
 List of digitized points
 :return: List of points
 :rtype: list of QgsPointXY
%End

    void setPoints( const QList<QgsPointXY> &pointList );
%Docstring
 Set the points on which to work

 \param pointList A list of points
%End

    void closePolygon();
%Docstring
 Close an open polygon
%End

};

/************************************************************************
 * This file has been generated automatically from                      *
 *                                                                      *
 * src/gui/qgsmaptoolcapture.h                                          *
 *                                                                      *
 * Do not edit manually ! Edit header and run scripts/sipify.pl again   *
 ************************************************************************/
