# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from pathlib import Path
from typing import ClassVar

from geoapps_utils.driver.data import BaseData
from geoh5py.objects import Surface
from pydantic import ConfigDict

from surface_apps import assets_path


class SurfaceNormalsOptions(BaseData):
    """
    Options for surface normals.

    :param surface: Triangulation on which normals will be computed
        at triangle centers.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: ClassVar[str] = "surface_normals"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/surface_normals.ui.json"
    title: ClassVar[str] = "Surface Normals"
    run_command: ClassVar[str] = "surface_apps.surface_normals.driver"

    conda_environment: str = "surface_apps"
    surfaces: list[Surface]
    merge_points: bool = True
    out_name: str = "surface normals"
