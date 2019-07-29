# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    calculus.datatypes.matrix.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    *NOT FULLY IMPLEMENTED.*
    *TO BE VALIDATED.*

"""

class Matrix(object):
     """Simple matrix data type.

     Of course there are much more advanced matrix data types for Python (for
     instance, the C{ndarray} data type of Numeric Python) and this implementation
     does not want to compete with them. The only role of this data type is to
     provide a convenient interface for the matrices returned by the C{Graph}
     object (for instance, allow indexing with tuples in the case of adjacency
     matrices and so on).
     """
     def __init__(self, data=None):
         """Initializes a matrix.

         @param data: the elements of the matrix as a list of lists, or C{None} to
         create a 0x0 matrix.
         """
         self._nrow, self._ncol, self._data = 0, 0, []
         self.data = data

     def Fill(self, value, *args):
         """Create a matrix filled with the given value

         @param value: the value to be used
         @keyword shape: the shape of the matrix. Can be a single integer,
           two integers or a tuple. If a single integer is
           given here, the matrix is assumed to be square-shaped.
         """
         if len(args) < 1:
             raise TypeError("expected an integer or a tuple")
         if len(args) == 1:
             if hasattr(args[0], "__len__"):
                 height, width = int(args[0][0]), int(args[0][1])
             else:
                 height, width = int(args[0]), int(args[0])
         else:
             height, width = int(args[0]), int(args[1])
         mtrx = [[value]*width for _ in xrange(height)]

         return Matrix(mtrx)

     def Zero(self, *args):
         """Create a matrix filled with zeros.

          @keyword shape: the shape of the matrix. Can be a single integer,
           two integers or a tuple. If a single integer is
           given here, the matrix is assumed to be square-shaped.
         """
         result = Matrix.Fill(0, *args)
         return result

     def Identity(cls, *args):
         """Create an identity matrix.

         @keyword shape: the shape of the matrix. Can be a single integer,
           two integers or a tuple. If a single integer is
           given here, the matrix is assumed to be square-shaped.
         """
         result = cls.Fill(0, *args)
         for i in range(min(result.shape)):
             result._data[i][i] = 1
         return result

     def _set_data(self, data=None):
         """Set the data stored in the matrix"""
         if data is not None:
             self._data = [list(row) for row in data]
             self._nrow = len(self._data)
             if self._nrow > 0:
                 self._ncol = max(len(row) for row in self._data)
             else:
                 self._ncol = 0
             for row in self._data:
                 if len(row) < self._ncol:
                     row.extend([0]*(self._ncol-len(row)))

     def _get_data(self):
         """Return the data stored in the matrix as a list of lists"""
         return [list(row) for row in self._data]

     data = property(_get_data, _set_data)

     @property
     def shape(self):
         """Return the shape of the matrix as a tuple"""
         return self._nrow, self._ncol

     def __add__(self, other):
         """Add the given value to the matrix.

         @param other: either a scalar or a matrix. Scalars will
           be added to each element of the matrix. Matrices will
           be added together elementwise.
         @return: the result matrix
         """
         if isinstance(other, Matrix):
             if self.shape != other.shape:
                 raise ValueError("matrix shapes do not match")
             return self.__class__([
                 [a+b for a, b in zip(row_a, row_b)]
                 for row_a, row_b in zip(self, other)
             ])
         else:
             return self.__class__([
                 [item+other for item in row] for row in self])

     def __eq__(self, other):
         """Check whether a given matrix is equal to another one"""
         return isinstance(other, Matrix) and \
                 self._nrow == other._nrow and \
                 self._ncol == other._ncol and \
                 self._data == other._data

     def __getitem__(self, i):
         """Return a single item, a row or a column of the matrix

         @param i: if a single integer, returns the M{i}th row as a list. If a
           slice, returns the corresponding rows as another L{Matrix} object. If
           a 2-tuple, the first element of the tuple is used to select a row and
           the second is used to select a column.
         """
         if isinstance(i, int):
             return list(self._data[i])
         elif isinstance(i, slice):
             return self.__class__(self._data[i])
         elif isinstance(i, tuple):
             try:
                 first = i[0]
             except IndexError:
                 first = slice(None)
             try:
                 second = i[1]
             except IndexError:
                 second = slice(None)
             if type(first) == slice and type(second) == slice:
                 return self.__class__(row[second] for row in self._data[first])
             elif type(first) == slice:
                 return [row[second] for row in self._data[first]]
             else:
                 return self._data[first][second]
         else:
             raise IndexError("invalid matrix index")

     def __hash__(self):
         """Return a hash value for a matrix."""
         return hash(self._nrow, self._ncol, self._data)

     def __iadd__(self, other):
         """In-place addition of a matrix or scalar."""
         if isinstance(other, Matrix):
             if self.shape != other.shape:
                 raise ValueError("matrix shapes do not match")
             for row_a, row_b in zip(self._data, other):
                 for i in range(len(row_a)):
                     row_a[i] += row_b[i]
         else:
             for row in self._data:
                 for i in range(len(row)):
                     row[i] += other
         return self

     def __isub__(self, other):
         """In-place subtraction of a matrix or scalar."""
         if isinstance(other, Matrix):
             if self.shape != other.shape:
                 raise ValueError("matrix shapes do not match")
             for row_a, row_b in zip(self._data, other):
                 for i in range(len(row_a)):
                     row_a[i] -= row_b[i]
         else:
             for row in self._data:
                 for i in range(len(row)):
                     row[i] -= other
         return self

     def __ne__(self, other):
          """Check whether a given matrix is not equal to another one."""
         return not self == other

     def __setitem__(self, i, value):
         """Set a single item, a row or a column of the matrix

         @param i: if a single integer, sets the M{i}th row as a list. If a
           slice, sets the corresponding rows from another L{Matrix} object.
           If a 2-tuple, the first element of the tuple is used to select a row
           and the second is used to select a column.
         @param value: the new value
         """
         if isinstance(i, int):
             # Setting a row
             if len(value) != len(self._data[i]):
                 raise ValueError("new value must have %d items" % self._ncol)
             self._data[i] = list(value)
         elif isinstance(i, slice):
             # Setting multiple rows
             if len(value) != len(self._data[i]):
                 raise ValueError("new value must have %d items" % self._ncol)
             if any(len(row) != self._ncol for row in value):
                 raise ValueError("rows of new value must have %d items" % \
                         self._ncol)
             self._data[i] = [list(row) for row in value]
         elif isinstance(i, tuple):
             try:
                 first = i[0]
             except IndexError:
                 first = slice(None)
             try:
                 second = i[1]
             except IndexError:
                 second = slice(None)
             if type(first) == slice and type(second) == slice:
                 # Setting a submatrix
                 # TODO
                 raise NotImplementedError
             elif type(first) == slice:
                 # Setting a submatrix
                 raise NotImplementedError
             else:
                 # Setting a single element
                 self._data[first][second] = value
         else:
             raise IndexError("invalid matrix index")

     def __sub__(self, other):
         """Subtract the given value from the matrix.

         @param other: either a scalar or a matrix. Scalars will
           be subtracted from each element of the matrix. Matrices will
           be subtracted together elementwise.
         @return: the result matrix
         """
         if isinstance(other, Matrix):
             if self.shape != other.shape:
                 raise ValueError("matrix shapes do not match")
             return self.__class__([
                 [a-b for a, b in zip(row_a, row_b)]
                 for row_a, row_b in zip(self, other)
              ])
         else:
             return self.__class__([
                 [item-other for item in row] for row in self])

     def __repr__(self):
         class_name = self.__class__.__name__
         rows = ("[%s]" % ", ".join(repr(item) for item in row) for row in self)
         return "%s([%s])" % (class_name, ", ".join(rows))

     def __str__(self):
         rows = ("[%s]" % ", ".join(repr(item) for item in row) for row in self)
         return "[%s]" % "\n ".join(rows)

     def __iter__(self):
         """Support for iteration.

         This is actually implemented as a generator, so there is no need for a
         separate iterator class. The generator returns I{copies} of the rows in
         the matrix as lists to avoid messing around with the internals. Feel
         free to do anything with the copies, the changes won't be reflected in
         the original matrix."""
         return (list(row) for row in self._data)

     def min(self, dim=None):
         """Return the minimum of the matrix along the given dimension

         @param dim: the dimension. 0 means determining the column minimums, 1 means
           determining the row minimums. If C{None}, the global minimum is
           returned.
         """
         if dim == 1:
              return [min(row) for row in self._data]
         if dim == 0:
              return [min(row[idx] for row in self._data) \
                          for idx in xrange(self._ncol)]
         return min(min(row) for row in self._data)

     def max(self, dim=None):
         """Return the maximum of the matrix along the given dimension

          @param dim: the dimension. 0 means determining the column maximums, 1 means
           determining the row maximums. If C{None}, the global maximum is
           returned.
         """
         if dim == 1:
             return [max(row) for row in self._data]
         if dim == 0:
             return [max(row[idx] for row in self._data) \
                          for idx in xrange(self._ncol)]
         return max(max(row) for row in self._data)
