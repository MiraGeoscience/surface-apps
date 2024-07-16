# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                     '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  All rights reserved.                                                        '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py import Workspace
from geoh5py.objects import Curve, Points

from surface_apps.iso_surfaces.utils import interp_to_grid


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
