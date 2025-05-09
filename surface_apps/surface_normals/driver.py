# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import logging
import sys
from pathlib import Path

from geoapps_utils.driver.driver import BaseDriver
from geoapps_utils.utils.transformations import (
    compute_normals,
)
from geoh5py.groups.property_group_type import GroupTypeEnum
from geoh5py.shared.conversion.base import CellObjectConversion
from geoh5py.shared.merging.cell import SurfaceMerger
from geoh5py.shared.utils import fetch_active_workspace

from surface_apps.surface_normals.options import SurfaceNormalsOptions


logger = logging.getLogger(__name__)


class Driver(BaseDriver):
    """
    Driver for computing surface normals.

    :param options: Application options
    """

    _params_class = SurfaceNormalsOptions

    def run(self):
        with fetch_active_workspace(self.params.geoh5, mode="r+") as geoh5:
            for surface in self.params.surfaces:
                normals = compute_normals(surface)
                surface.add_data(
                    {
                        "x": {"values": normals[:, 0], "association": "CELL"},
                        "y": {"values": normals[:, 1], "association": "CELL"},
                        "z": {"values": normals[:, 2], "association": "CELL"},
                    }
                )

            merge_points = self.params.merge_points and len(self.params.surfaces) > 1
            if merge_points:
                surface = SurfaceMerger.merge_objects(
                    geoh5, self.params.surfaces, name="merged"
                )

            points = []
            surfaces = [surface] if merge_points else self.params.surfaces
            for surface in surfaces:
                points.append(
                    CellObjectConversion.to_points(
                        surface, name=f"{surface.name} {self.params.out_name}"
                    )
                )

            for pts in points:
                properties = [pts.get_data(k)[0] for k in "xyz"]
                prop_group = pts.create_property_group(
                    name="Normals",
                    property_group_type=GroupTypeEnum.VECTOR,
                    properties=properties,
                )
                self.update_monitoring_directory(pts)

        return prop_group


if __name__ == "__main__":
    file = Path(sys.argv[1]).resolve()
    driver = Driver.start(file)
