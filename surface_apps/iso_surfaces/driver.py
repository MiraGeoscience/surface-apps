# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                     '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  All rights reserved.                                                        '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import sys
import logging
import warnings
import numpy as np
from tqdm import tqdm
from scipy.interpolate import interp1d
from skimage.measure import marching_cubes

from geoh5py.ui_json import InputFile
from geoh5py.objects import Surface, BlockModel, ObjectBase
from geoh5py.shared.utils import fetch_active_workspace
from geoapps_utils.formatters import string_name
from geoapps_utils.numerical import weighted_average
from geoapps_utils.transformations import rotate_xyz
from surface_apps.iso_surfaces.params import IsoSurfaceParameters
from surface_apps.driver import BaseSurfaceDriver


logger = logging.getLogger(__name__)

class IsoSurfacesDriver(BaseSurfaceDriver):
    """
    Driver for the detection of iso-surfaces within geoh5py objects.

    :param parameters: Application parameters.
    """

    _parameter_class = IsoSurfaceParameters

    def __init__(self, parameters: IsoSurfaceParameters | InputFile):
        super().__init__(parameters)

    def make_surfaces(self):
        """Make surface objects from iso-surfaces detected in source data."""

        with fetch_active_workspace(self.params.geoh5, mode="r+"):
            logger.info("Generating iso-surfaces ...")
            levels = self.params.detection.contours

            if len(levels) >= 1:

                surfaces = self.iso_surface(
                    self.params.source.objects,
                    self.params.source.data.values,
                    levels,
                    resolution=self.params.detection.resolution,
                    max_distance=self.params.detection.max_distance,
                )

                results = []
                for surface, level in zip(surfaces, levels):
                    if len(surface[0]) > 0 and len(surface[1]) > 0:
                        results += [
                            Surface.create(
                                self.params.geoh5,
                                name=string_name(self.params.source.data.name + f"_{level:.2e}"),
                                vertices=surface[0],
                                cells=surface[1],
                                parent=self.out_group,
                            )
                        ]


    @staticmethod
    def iso_surface(
        entity: ObjectBase,
        values: np.ndarray,
        levels: list,
        resolution: float = 100,
        max_distance: float = np.inf,
    ):
        """
        Generate 3D iso surface from an entity vertices or centroids and values.

        Parameters
        ----------
        entity: geoh5py.objects
            Any entity with 'vertices' or 'centroids' attribute.

        values: numpy.ndarray
            Array of values to create iso-surfaces from.

        levels: list of floats
            List of iso values

        max_distance: float, default=numpy.inf
            Maximum distance from input data to generate iso surface.
            Only used for input entities other than BlockModel.

        resolution: int, default=100
            Grid size used to generate the iso surface.
            Only used for input entities other than BlockModel.

        Returns
        -------
        surfaces: list of numpy.ndarrays
            List of surfaces (one per levels) defined by
            vertices and cell indices.
            [(vertices, cells)_level_1, ..., (vertices, cells)_level_n]
        """
        if getattr(entity, "locations", None) is not None:
            locations = entity.locations
        else:
            raise ValueError("Input 'entity' must have 'vertices' or 'centroids'.")

        if isinstance(entity, BlockModel):
            if entity.shape is None:
                raise ValueError("BlockModel must have a shape attribute.")

            values = values.reshape(
                (entity.shape[2], entity.shape[0], entity.shape[1]), order="F"
            ).transpose((1, 2, 0))

            grid = []
            for i in ["u", "v", "z"]:
                cell_delimiters = getattr(entity, i + "_cell_delimiters")
                dx = cell_delimiters[1:] - cell_delimiters[:-1]
                grid.append(cell_delimiters[:-1] + dx / 2)

        else:
            print("Interpolating the model onto a regular grid...")
            grid = []
            for i in np.arange(3):
                grid += [
                    np.arange(
                        locations[:, i].min(),
                        locations[:, i].max() + resolution,
                        resolution,
                    )
                ]

            y, x, z = np.meshgrid(grid[1], grid[0], grid[2])
            values = weighted_average(
                locations,
                np.c_[x.flatten(), y.flatten(), z.flatten()],
                [values],
                threshold=resolution / 2.0,
                n=8,
                max_distance=max_distance,
            )
            values = values[0].reshape(x.shape)

        lower, upper = np.nanmin(values), np.nanmax(values)
        surfaces = []
        print("Running marching cubes on levels.")
        skip = []
        for level in tqdm(levels):
            try:
                if level < lower or level > upper:
                    skip += [level]
                    continue
                verts, faces, _, _ = marching_cubes(values, level=level)

                # Remove all vertices and cells with nan
                nan_verts = np.any(np.isnan(verts), axis=1)
                rem_cells = np.any(nan_verts[faces], axis=1)

                active = np.arange(nan_verts.shape[0])
                active[nan_verts] = nan_verts.shape[0]
                _, inv_map = np.unique(active, return_inverse=True)

                verts = verts[~nan_verts, :]
                faces = faces[~rem_cells, :]
                faces = inv_map[faces].astype("uint32")

                vertices = []
                for i in np.arange(3):
                    interp = interp1d(
                        np.arange(grid[i].shape[0]), grid[i], fill_value="extrapolate"
                    )
                    vertices += [interp(verts[:, i])]

                if isinstance(entity, BlockModel):
                    vertices = rotate_xyz(
                        np.vstack(vertices).T, [0, 0, 0], entity.rotation
                    )
                    vertices[:, 0] += entity.origin["x"]
                    vertices[:, 1] += entity.origin["y"]
                    vertices[:, 2] += entity.origin["z"]

                else:
                    vertices = np.vstack(vertices).T
            except RuntimeError:
                vertices, faces = [], []

            surfaces += [[vertices, faces]]

        if any(skip):
            warnings.warn(f"The following levels were out of bound and ignored: {skip}")
        return surfaces


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)
    driver = IsoSurfacesDriver(ifile)
    driver.run()
