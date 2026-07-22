.. _edge_detection:

Iso Surfaces
============

With this application, users can create surfaces of equal values from 3D data in a semi-automated
fashion. The application uses a `marching cubes <https://scikit-image.org/docs/stable/auto_examples/edges/plot_marching_cubes.html>`__
algorithm from the open-source scikit-image package. The algorithm works by 'marching' across the volume,
identifying iso-valued regions and adding them to an output triangulation (surface).  Surfaces are exported to
`Geoscience ANALYST <https://mirageoscience.com/mining-industry-software/geoscience-analyst/>`__
for viewing and editing.

.. figure:: ./images/iso_surfaces/iso_surface_landing.png
            :align: center
            :width: 100%

New user? Visit the `Getting Started <getting_started>`_ page.

Application
-----------

The following sections provide details on the different parameters exposed in the user-interface (``iso_surface.ui.json``).

.. figure:: ./images/iso_surfaces/iso_surfaces_ui.png
            :align: center
            :width: 300

Data Selection
^^^^^^^^^^^^^^

 - **Object**: Select the target data object from the dropdown list.  Objects should be
    distributed in 3D and may be of type Points, Curve, Surface, Octree, or BlockModel.
 - **Data**: Select the data attribute to use for iso-surface detection.  Can be any
    FloatData children of the selected *Object*.


Contour Parameters
^^^^^^^^^^^^^^^^^^^^

List of parameters controlling the detection and filtering of iso-surfaces.  The iso-surface
levels can be provided as either a min/max/spacing interval or a fixed list.

 - **Interval min**: Interval minimum.
 - **Interval max**: Interval maximum.
 - **Interval spacing**: Interval spacing.
 - **Contours**: These are fixed iso-surface levels outside of any provided interval ranges
 - **Max interpolation distance**: Maximum distance between points for interpolation into base grid.
 - **Base grid resolution**: Resolution of the grid used by scikit-image to create the contours.

Output Preferences
^^^^^^^^^^^^^^^^^^

 - **Group**: Results are stored in a ``Container Group`` using the name provided here.
    Each level will result in a separate surface stored under the group.


Need help? Contact us at support@mirageoscience.com
