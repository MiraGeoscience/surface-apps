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

import numpy as np
from geoapps_utils.driver.driver import BaseDriver
from geoapps_utils.utils.transformations import (
    compute_normals,
)
from geoh5py.groups.property_group_type import GroupTypeEnum
from geoh5py.objects import Points
from geoh5py.shared.utils import fetch_active_workspace

from surface_apps.surface_normals.options import SurfaceNormalsOptions


logger = logging.getLogger(__name__)


class SurfaceNormalsDriver(BaseDriver):
    """
    Driver for computing surface normals.

    :param options: Application options
    """

    _params_class = SurfaceNormalsOptions

    def run(self):
        with fetch_active_workspace(self.params.geoh5, mode="r+") as geoh5:
            normals = []
            for surface in self.params.surfaces:
                normals.append(compute_normals(surface))

            if self.params.merge_points:
                points = Points.create(
                    geoh5,
                    name="centers",
                    vertices=np.row_stack([k.centroids for k in self.params.surfaces]),
                )
                x, y, z = points.add_data(
                    {
                        "x": {"values": np.row_stack(normals)[:, 0]},
                        "y": {"values": np.row_stack(normals)[:, 1]},
                        "z": {"values": np.row_stack(normals)[:, 2]},
                    }
                )
            else:
                for i, surface in enumerate(self.params.surfaces):
                    points = Points.create(
                        geoh5,
                        name=f"{surface.name} centers",
                        vertices=surface.centroids,
                    )
                    x, y, z = points.add_data(
                        {
                            "x": {"values": normals[i][:, 0]},
                            "y": {"values": normals[i][:, 1]},
                            "z": {"values": normals[i][:, 2]},
                        }
                    )

        prop_group = points.create_property_group(
            name="Normals",
            properties=[x, y, z],
            property_group_type=GroupTypeEnum.VECTOR,
        )

        return prop_group


if __name__ == "__main__":
    file = Path(sys.argv[1]).resolve()
    driver = SurfaceNormalsDriver.start(file)
