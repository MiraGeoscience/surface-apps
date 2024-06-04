# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                     '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  All rights reserved.                                                        '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from curve_apps.contours.params import ContourDetectionParameters
from geoapps_utils.driver.data import BaseData
from geoh5py.data import Data
from geoh5py.objects import Curve, Octree, Points, Surface
from pydantic import BaseModel, ConfigDict

from surface_apps import assets_path


class IsoSurfaceSourceParameters(BaseData):
    """
    Source parameters providing input data to the driver.

    :param objects: A Grid2D, Points, Curve or Surface source object.
    :param data: Data values to create iso-surfaces from.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    objects: Points | Curve | Surface | Octree
    data: Data


class IsoSurfaceDetectionParameters(ContourDetectionParameters):
    """
    Contour specification parameters.

    :param max_distance: Maximum distance for interpolation.
    :param resolution: Resolution of underlying grid.
    """

    max_distance: float = 500.0
    resolution: float = 50.0


class IsoSurfaceOutputParameters(BaseModel):
    """
    Output parameters.

    :param export_as: Name of the output entity.
    :param out_group: Name of the output group.
    """

    out_group: str = "Iso Surfaces"


class IsoSurfaceParameters(BaseData):
    """
    Contour parameters for use with `contours.driver`.

    :param contours: Contouring parameters.
    :param source: Parameters for the source object and data.
    :param output: Output
    """

    name: ClassVar[str] = "iso_surfaces"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/iso_surfaces.ui.json"
    title: ClassVar[str] = "IsoSurface Detection"
    run_command: ClassVar[str] = "surface_apps.iso_surface.driver"

    source: IsoSurfaceSourceParameters
    detection: IsoSurfaceDetectionParameters
    output: IsoSurfaceOutputParameters = IsoSurfaceOutputParameters()
