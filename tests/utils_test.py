# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


import numpy as np
import pytest
from geoh5py import Workspace
from geoh5py.objects import Curve, Points, Surface

from surface_apps.iso_surfaces.utils import interp_to_grid
from surface_apps.surface_normals.utils import find_common_data, to_points


def get_points(workspace):
    x = np.linspace(0, 10, 11)
    y = np.linspace(0, 10, 11)
    z = np.linspace(-8, 2, 11)
    x_grid, y_grid, z_grid = np.meshgrid(x, y, z)
    vertices = np.c_[x_grid.flatten(), y_grid.flatten(), z_grid.flatten()]
    points = Points.create(workspace, name="my points", vertices=vertices)

    return points


def get_curve(workspace):
    pts = get_points(workspace)
    locs = pts.vertices
    cells = np.c_[np.arange(len(locs) - 1), np.arange(1, len(locs))]
    cell_distances = np.linalg.norm(locs[cells[:, 1]] - locs[cells[:, 0]], axis=1)
    too_far = cell_distances > 2
    cells = cells[~too_far]
    curve = Curve.create(
        workspace,
        name="my curve",
        vertices=locs,
        cells=cells,
    )

    return curve


def test_interp_points_to_grid(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    pts = get_points(ws)
    values = np.zeros(pts.n_vertices)

    right_side = pts.vertices[:, 0] > 5
    values[right_side] = 1

    above_zero = pts.vertices[:, 2] > 0
    values[above_zero] = np.nan

    data = pts.add_data({"data": {"values": values}})
    grid, gridded_data = interp_to_grid(pts, data, resolution=0.5, max_distance=1)
    y_grid, x_grid, z_grid = np.meshgrid(grid[1], grid[0], grid[2])
    pts = Points.create(
        ws,
        name="my grid",
        vertices=np.c_[x_grid.flatten(), y_grid.flatten(), z_grid.flatten()],
    )
    pts.add_data({"my grid data": {"values": gridded_data.flatten()}})

    assert all(gridded_data[x_grid > 6] == 1)
    assert all(gridded_data[x_grid < 4] == 0)
    assert grid[2].max() == 0


def test_interp_curve_vertex_data_to_grid(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    crv = get_curve(ws)
    values = np.zeros(crv.n_vertices)

    right_side = crv.vertices[:, 0] > 5
    values[right_side] = 1

    above_zero = crv.vertices[:, 2] > 0
    values[above_zero] = np.nan

    data = crv.add_data({"vertex data": {"values": values, "association": "VERTEX"}})
    grid, gridded_data = interp_to_grid(crv, data, resolution=0.5, max_distance=1)
    y_grid, x_grid, z_grid = np.meshgrid(grid[1], grid[0], grid[2])
    pts = Points.create(
        ws,
        name="my grid",
        vertices=np.c_[x_grid.flatten(), y_grid.flatten(), z_grid.flatten()],
    )
    pts.add_data({"my grid data": {"values": gridded_data.flatten()}})

    assert all(gridded_data[x_grid > 6] == 1)
    assert all(gridded_data[x_grid < 4] == 0)
    assert grid[2].max() == 0


def test_interp_curve_cell_data_to_grid(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    crv = get_curve(ws)
    values = np.zeros(crv.n_cells)

    right_side = crv.vertices[crv.cells[:, 1], 0] > 5
    values[right_side] = 1

    above_zero = crv.vertices[crv.cells[:, 1], 2] > 0
    values[above_zero] = np.nan

    data = crv.add_data({"cell data": {"values": values, "association": "CELL"}})
    grid, gridded_data = interp_to_grid(crv, data, resolution=0.5, max_distance=1)
    y_grid, x_grid, z_grid = np.meshgrid(grid[1], grid[0], grid[2])
    pts = Points.create(
        ws,
        name="my other grid",
        vertices=np.c_[x_grid.flatten(), y_grid.flatten(), z_grid.flatten()],
    )
    pts.add_data({"my other grid data": {"values": gridded_data.flatten()}})

    assert all(gridded_data[x_grid > 6] == 1)
    assert all(gridded_data[x_grid < 4] == 0)
    assert grid[2].max() == -0.5


def create_objects(workspace, bad_association=False):
    vertices = np.array([[30, 0, 0]])
    pts = Points.create(workspace, name="my points", vertices=vertices)
    pts.add_data(
        {"test": {"values": np.array([1])}, "other": {"values": np.array([2])}}
    )
    vertices = np.array(
        [
            [10, 0, 0],
            [20, 0, 0],
        ]
    )
    crv = Curve.create(workspace, name="my curve", vertices=vertices)
    vals = [2] if bad_association else [2, 2]
    assoc = "CELL" if bad_association else "VERTEX"
    crv.add_data(
        {
            "test": {"values": np.array([1, 1]), "association": "VERTEX"},
            "other": {"values": np.array(vals), "association": assoc},
        }
    )
    vertices = np.array(
        [
            [0, 0, 0],
            [5, 0, 0],
            [5, 5, 0],
        ]
    )
    cells = np.array([[0, 1, 2]])
    surf = Surface.create(workspace, name="my surface", vertices=vertices, cells=cells)
    surf.add_data(
        {
            "test": {"values": np.array([1]), "association": "CELL"},
            "other": {"values": np.array([2]), "association": "CELL"},
            "nope": {"values": np.array([3]), "association": "CELL"},
        }
    )
    return pts, crv, surf


def test_find_common_data(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        points, curve, surface = create_objects(ws)
        names = find_common_data([points, curve, surface])
        assert len(names) == 2
        assert all(k in names for k in ["test", "other"])
        names = find_common_data([points, curve, surface], names=["test"])
        assert names == ["test"]


def test_to_points(tmp_path):
    with Workspace(tmp_path / "test.geoh5") as ws:
        points, curve, surface = create_objects(ws)

        pts = to_points([points, curve, surface], name="merged")
        assert pts.get_data("test")
        assert pts.get_data("other")
        assert not pts.get_data("nope")
        assert len(pts.vertices) == 4

        pts = to_points([points, curve, surface], name="merged", children=["test"])
        assert len(pts.vertices) == 4
        assert not pts.get_data("other")
        assert not pts.get_data("nope")

        pts = to_points(
            objects=[points, curve, surface],
            name="merged",
            property_group={"name": "my group"},
        )
        assert pts.property_groups is not None
        assert pts.property_groups[0].name == "my group"

        points, curve, surface = create_objects(ws, bad_association=True)
        with pytest.raises(ValueError, match="Data stored on different"):
            pts = to_points([points, curve], name="merged")
