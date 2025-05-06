# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

import numpy as np
from geoh5py.objects import Surface


def normal_from_triangle(triangle: np.ndarray) -> np.ndarray:
    """Compute the normal vector from a triangle defined by three vertices."""
    v1 = triangle[1] - triangle[0]
    v2 = triangle[2] - triangle[0]
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)
    if norm == 0:
        return np.zeros(3)
    return normal / norm


def compute_normals(surface: Surface) -> np.ndarray:
    """Compute normals for each triangle in a surface."""
    normals = []
    for cell in surface.cells:
        triangle = surface.vertices[cell, :]
        normals.append(triangle)

    return np.hstack(normals)
