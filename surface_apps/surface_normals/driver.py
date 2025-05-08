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
from geoh5py.shared.utils import fetch_active_workspace

from surface_apps.surface_normals.options import SurfaceNormalsOptions
from surface_apps.surface_normals.utils import to_points


logger = logging.getLogger(__name__)


class SurfaceNormalsDriver(BaseDriver):
    """
    Driver for computing surface normals.

    :param options: Application options
    """

    _params_class = SurfaceNormalsOptions

    def run(self):
        with fetch_active_workspace(self.params.geoh5, mode="r+"):
            for surface in self.params.surfaces:
                normals = compute_normals(surface)
                surface.add_data(
                    {
                        "x": {"values": normals[:, 0], "association": "CELL"},
                        "y": {"values": normals[:, 1], "association": "CELL"},
                        "z": {"values": normals[:, 2], "association": "CELL"},
                    }
                )

            prop_group = {
                "name": "Normals",
                "property_group_type": GroupTypeEnum.VECTOR,
            }
            if self.params.merge_points:
                to_points(
                    self.params.surfaces,
                    name="centers",
                    children=["x", "y", "z"],
                    property_group=prop_group,
                )
            else:
                for surface in self.params.surfaces:
                    to_points(
                        [surface],
                        name=f"{surface.name} centers",
                        children=["x", "y", "z"],
                        property_group=prop_group,
                    )

        return prop_group


if __name__ == "__main__":
    file = Path(sys.argv[1]).resolve()
    driver = SurfaceNormalsDriver.start(file)
