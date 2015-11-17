#    Copyright 2015 Geoscience Australia
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from __future__ import absolute_import, division, print_function

import numpy
import contextlib
import netCDF4 as nc4

from ..core import Coordinate, Variable, StorageUnitBase
from ..indexing import Range, range_to_index, normalize_index


class NetCDF4StorageUnit(StorageUnitBase):
    def __init__(self, filepath, variables=None, coordinates=None):
        """
        :param variables: variables in the SU
        :param coordinates: coordinates in the SU
        """
        self._filepath = filepath
        if variables and coordinates:
            self.coordinates = coordinates
            self.variables = variables
        else:
            self.coordinates = {}
            self.variables = {}
            with contextlib.closing(self._open_dataset()) as ncds:
                for name, var in ncds.variables.items():
                    dims = var.dimensions
                    if len(dims) == 1 and name == dims[0]:
                        self.coordinates[name] = Coordinate(var.dtype, var[0], var[-1], var.shape[0])
                    else:
                        ndv = (getattr(var, '_FillValue', None) or
                               getattr(var, 'missing_value', None) or
                               getattr(var, 'fill_value', None))
                        self.variables[name] = Variable(var.dtype, ndv, var.dimensions)

    def _open_dataset(self):
        return nc4.Dataset(self._filepath, mode='r', clobber=False, diskless=False, persist=False, format='NETCDF4')

    def get_coord(self, dim, index=None):
        coord = self.coordinates[dim]
        index = normalize_index(coord, index)

        if isinstance(index, slice):
            with contextlib.closing(self._open_dataset()) as ncds:
                return ncds[dim][index], index

        if isinstance(index, Range):
            with contextlib.closing(self._open_dataset()) as ncds:
                data = ncds[dim][:]
                index = range_to_index(data, index)
                return data[index], index

    def _fill_data(self, name, index, dest):
        with contextlib.closing(self._open_dataset()) as ncds:
            numpy.copyto(dest, ncds[name][index])