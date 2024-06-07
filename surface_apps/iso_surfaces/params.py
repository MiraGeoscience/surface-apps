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

import numpy as np
from geoapps_utils.driver.data import BaseData
from geoh5py.data import Data
from geoh5py.objects import Curve, Octree, Points, Surface
from geoh5py.ui_json.utils import str2list
from pydantic import BaseModel, ConfigDict, field_validator

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


class IsoSurfaceDetectionParameters(BaseData):
    """
    Contour specification parameters.

    :param interval_min: Minimum value for contours.
    :param interval_max: Maximum value for contours.
    :param interval_spacing: Step size for contours.
    :param fixed_contours: String defining list of fixed contours.
    :param max_distance: Maximum distance for interpolation.
    :param resolution: Resolution of underlying grid.
    """

    interval_min: float | None = None
    interval_max: float | None = None
    interval_spacing: float | None = None
    fixed_contours: list[float] | None = None
    max_distance: float = 500.0
    resolution: float = 50.0

    @field_validator("fixed_contours", mode="before")
    @classmethod
    def fixed_contour_input_to_list_of_floats(cls, val):
        """Parse fixed contour string into list of floats."""

        if isinstance(val, list):
            if not all(isinstance(k, float) for k in val):
                raise ValueError("List of fixed contours must contain only floats.")
            fixed_contours = val

        elif isinstance(val, str):
            fixed_contours = str2list(val)

        elif val is None:
            fixed_contours = None

        else:
            raise ValueError(
                "Fixed contours must be a list of floats, "
                "a string containing comma separated numeric characters, "
                "or None."
            )

        return fixed_contours

    @property
    def has_intervals(self) -> bool:
        """True if interval min, max and spacing are defined."""

        has_min_max = None not in [self.interval_min, self.interval_max]
        has_spacing = self.interval_spacing not in [0, None]

        return has_min_max and has_spacing

    @property
    def intervals(self) -> list[float]:
        """Returns arange of requested contour intervals."""

        if self.has_intervals:
            intervals = np.arange(
                self.interval_min,
                self.interval_max + self.interval_spacing / 2,  # type: ignore
                self.interval_spacing,
            ).tolist()
        else:
            intervals = []

        return intervals

    @property
    def contours(self) -> list[float]:
        """
        Returns a list of requested contours merging interval and fixed values.
        """
        contours = self.intervals + (self.fixed_contours or [])
        contours.sort()
        return contours


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
