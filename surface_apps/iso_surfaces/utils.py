# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                     '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  All rights reserved.                                                        '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import logging
import warnings

import numpy as np
from geoapps_utils.numerical import weighted_average
from geoapps_utils.transformations import rotate_xyz
from geoh5py.objects import BlockModel, ObjectBase
from scipy.interpolate import interp1d
from skimage.measure import marching_cubes
from tqdm import tqdm


def entity_to_grid(
    entity: ObjectBase,
    values: np.ndarray,
    resolution: float,
    max_distance: float,
):
    """
    Extracts grid and values from a geoh5py object.

    :param entity: geoh5py object with locations data.
    :param values: Data to be reshaped or interpolated to grid ordering.

    :returns: Tuple of grid and values.
    """

    if getattr(entity, "locations", None) is None:
        raise ValueError("Input 'entity' must have a vertices or centroids set.")

    if isinstance(entity, BlockModel):
        grid, values = block_model_to_grid(entity, values)
    else:
        grid, values = interp_to_grid(entity, values, resolution, max_distance)

    return grid, values


def block_model_to_grid(
    model: BlockModel, values: np.ndarray
) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Convert block model cell delimiters arrays to centroids based grid.

    :param model: BlockModel object.
    :param values: Data to be reshaped to grid ordering.
    """

    if model.shape is None:
        raise ValueError("BlockModel must have a shape attribute.")

    values = values.reshape(
        (model.shape[2], model.shape[0], model.shape[1]), order="F"
    ).transpose((1, 2, 0))

    grid = []
    for i in ["u", "v", "z"]:
        cell_delimiters = getattr(model, i + "_cell_delimiters")
        dx = cell_delimiters[1:] - cell_delimiters[:-1]
        grid.append(cell_delimiters[:-1] + dx / 2)

    return grid, values


def interp_to_grid(
    entity: ObjectBase, values: np.ndarray, resolution, max_distance
) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Interpolate values into a regular grid bounding all finite data points.

    :param entity: Geoh5py object with locations data.
    :param values: Data to be interpolated to grid.
    :param resolution: Grid resolution
    :param max_distance: Maximum distance used in weighted average.

    :returns: Tuple of grid and nearest neighbor interpolated values. The
        resulting grid bounds all the points in entity for which the data
        is not nan.
    """

    grid = []
    is_finite = np.isfinite(values)
    locations = entity.locations[is_finite, :]
    finite_values = values[is_finite]
    for i in np.arange(3):
        grid += [
            np.arange(
                locations[:, i].min(),
                locations[:, i].max() + resolution,
                resolution,
            )
        ]

    y, x, z = np.meshgrid(grid[1], grid[0], grid[2])
    average_values = weighted_average(
        locations,
        np.c_[x.flatten(), y.flatten(), z.flatten()],
        [finite_values],
        threshold=resolution / 2.0,
        n=8,
        max_distance=max_distance,
    )
    average_values = average_values[0].reshape(x.shape)

    return grid, average_values


def extract_iso_surfaces(
    entity: ObjectBase, grid: list[np.ndarray], levels: list[float], values: np.ndarray
) -> list[list[np.ndarray]]:

    surfaces = []
    skip = []
    for level in tqdm(levels):
        try:
            if level < np.nanmin(values) or level > np.nanmax(values):
                skip += [level]
                continue
            verts, faces, _, _ = marching_cubes(values, level=level)
            verts, faces = remove_nan(verts, faces)

            vertices = []
            for i in np.arange(3):
                interp = interp1d(
                    np.arange(grid[i].shape[0]), grid[i], fill_value="extrapolate"
                )
                vertices += [interp(verts[:, i])]

            if isinstance(entity, BlockModel):
                vertices = rotate_xyz(np.vstack(vertices).T, [0, 0, 0], entity.rotation)
                vertices[:, 0] += entity.origin["x"]  # type: ignore
                vertices[:, 1] += entity.origin["y"]  # type: ignore
                vertices[:, 2] += entity.origin["z"]  # type: ignore

            else:
                vertices = np.vstack(vertices).T  # type: ignore

        except RuntimeError as _:  # noqa
            logging.exception("Caught a RuntimeError in marching cubes algorithm.")
            skip += [level]

        surfaces += [[vertices, faces]]

    if any(skip):
        warnings.warn(f"The following levels were out of bound and ignored: {skip}")

    return surfaces


def remove_nan(verts: np.ndarray, faces: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Remove all vertices and cells with nan.

    :param verts: Vertices array.
    :param faces: Faces array.

    :returns: vertices and faces without nans.
    """

    nan_verts = np.any(np.isnan(verts), axis=1)
    rem_cells = np.any(nan_verts[faces], axis=1)

    active = np.arange(nan_verts.shape[0])
    active[nan_verts] = nan_verts.shape[0]
    _, inv_map = np.unique(active, return_inverse=True)

    verts = verts[~nan_verts, :]
    faces = faces[~rem_cells, :]
    faces = inv_map[faces].astype("uint32")

    return verts, faces
