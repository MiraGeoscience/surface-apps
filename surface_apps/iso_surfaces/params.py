# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import numpy as np
from geoapps_utils.base import Options
from geoh5py.data import Data
from geoh5py.groups import UIJsonGroup
from geoh5py.objects import BlockModel, Points, Surface
from geoh5py.objects.cell_object import CellObject
from geoh5py.objects.grid_object import GridObject
from geoh5py.ui_json.utils import str2list
from pydantic import BaseModel, ConfigDict, field_validator

from surface_apps import assets_path


class IsoSurfaceSourceParameters(BaseModel):
    """
    Source parameters providing input data to the driver.

    :param objects: A Grid2D, Points, Curve or Surface source object.
    :param data: Data values to create iso-surfaces from.
    :param horizon: Clipping surface to restrict interpolation from
        bleeding into the air.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    objects: Points | CellObject | GridObject
    data: Data
    horizon: Surface | None = None

    @field_validator("objects", mode="before")
    @classmethod
    def no_single_layer_grids(cls, value):
        """Ensure a grid has more than a single layer in any dimension."""

        if isinstance(value, BlockModel):
            n_cells = [len(getattr(value, f"{k}_cell_delimiters")) - 1 for k in "uvz"]
            if any(n == 1 for n in n_cells):
                raise ValueError(
                    "Grid source cannot be a single layer in any dimension."
                )

        return value


class IsoSurfaceDetectionParameters(BaseModel):
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
            if val == "":
                fixed_contours = None
            else:
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


class IsoSurfaceParameters(Options):
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

    conda_environment: str = "surface_apps"
    source: IsoSurfaceSourceParameters
    detection: IsoSurfaceDetectionParameters
    out_group: UIJsonGroup | None = None
