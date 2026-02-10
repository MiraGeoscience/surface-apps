# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2025-2026 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Surface

from surface_apps.surface_normals.driver import Driver as SurfaceNormalsDriver
from surface_apps.surface_normals.options import SurfaceNormalsOptions


def create_surface(workspace: Workspace):
    h = np.sqrt(2)
    alpha = np.deg2rad(30)
    vertices = np.array(
        [
            [-h * np.cos(alpha), -h * np.sin(alpha), 0],
            [h * np.sin(alpha), -h * np.cos(alpha), 0],
            [h * np.cos(alpha), h * np.sin(alpha), 0],
            [-h * np.sin(alpha), h * np.cos(alpha), 0],
            [0, 0, -1],
            [0, 0, 1],
        ]
    )
    cells = np.array(
        [
            [1, 2, 5],
            [0, 1, 5],
            [3, 0, 5],
            [2, 3, 5],
            [1, 4, 2],
            [0, 4, 1],
            [3, 4, 0],
            [2, 4, 3],
        ]
    )

    surf = Surface.create(workspace, name="diamond", vertices=vertices, cells=cells)
    return surf


def test_surface_normals(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        surf = create_surface(ws)

    opts = SurfaceNormalsOptions(geoh5=ws, surfaces=[surf])
    opts.write_ui_json(tmp_path / "test.ui.json")
    normals = SurfaceNormalsDriver.start(tmp_path / "test.ui.json")

    with Workspace(tmp_path / "test.geoh5") as ws:
        pts = ws.get_entity("diamond surface normals")[0]
        pg = pts.fetch_property_group("Normals")

        normals = np.column_stack([ws.get_entity(k)[0].values for k in pg.properties])
        h = np.sqrt(2)
        beta = np.deg2rad(15)
        validation = (
            np.array(
                [
                    [h * np.cos(beta), -h * np.sin(beta), h],
                    [-h * np.sin(beta), -h * np.cos(beta), h],
                    [-h * np.cos(beta), h * np.sin(beta), h],
                    [h * np.sin(beta), h * np.cos(beta), h],
                    [h * np.cos(beta), -h * np.sin(beta), -h],
                    [-h * np.sin(beta), -h * np.cos(beta), -h],
                    [-h * np.cos(beta), h * np.sin(beta), -h],
                    [h * np.sin(beta), h * np.cos(beta), -h],
                ]
            )
            / 2
        )

        assert np.allclose(normals, validation)
