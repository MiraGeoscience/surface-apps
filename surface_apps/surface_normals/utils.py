# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of surface-apps package.                                  '
#                                                                              '
#  surface-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).                 '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from __future__ import annotations

import numpy as np
from geoh5py.data import Data, DataAssociationEnum
from geoh5py.objects import Points


def find_common_data(
    objects: list[Points], names: list[str] | None = None
) -> list[str]:
    """
    Collect all data that exist on all provided objects.

    :param objects: List of object to collect data from.
    :param names: List of data children to collect.  If not provided,
        the merge will be performed on all data children that exist on
        every object.
    :return: List of data children names.  If names is provided, order
        will be maintained.
    """
    children = []
    for obj in objects:
        children.append({k.name for k in obj.children if isinstance(k, Data)})

    out = list(set.intersection(*children))
    if names:
        out = [k for k in names if k in out]

    return out


def to_points(
    objects: list[Points],
    name: str,
    children: list[str] | None = None,
    property_group: dict | None = None,
) -> Points:
    """
    Merge multiple points derived objects and data into a single point set.

    :param objects: List of objects to collect data from.
    :param name: Name of the merged point set.
    :param children: Names of data children to merge.  If not provided,
        the merge will be performed on all data children that exists on
        every object.
    :param property_group: dictionary of kwargs to construct an optional
        property group that stores the resulting data.

    :return: A points object that is the union of all objects locations
        that contains merged data and optional property group.
    """

    children = find_common_data(objects, names=children)

    kwargs = {}
    vertices = []
    for child in children:
        locs = []
        vals = []
        for obj in objects:
            data = obj.get_data(child)[0]
            is_vertex = data.association == DataAssociationEnum.VERTEX
            locs.append(obj.vertices if is_vertex else obj.centroids)  # type: ignore
            vals.append(data.values)
        kwargs[child] = {"values": np.hstack(vals)}
        vertices.append(np.vstack(locs))

    if not len(np.unique([len(k) for k in vertices])) == 1:
        raise ValueError(
            "Data stored on different objects must have "
            "the same data association type to be merged"
            "into a single points set."
        )

    points = Points.create(
        objects[0].workspace,
        name=name,
        vertices=vertices[0],
    )
    properties = points.add_data(kwargs)

    if property_group:
        points.create_property_group(
            properties=properties,
            **property_group,
        )

    return points
