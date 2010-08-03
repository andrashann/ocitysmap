# -*- coding: utf-8 -*-

# ocitysmap, city map and street index generator from OpenStreetMap data
# Copyright (C) 2010  David Decotigny
# Copyright (C) 2010  Frédéric Lehobey
# Copyright (C) 2010  Pierre Mauduit
# Copyright (C) 2010  David Mentré
# Copyright (C) 2010  Maxime Petazzoni
# Copyright (C) 2010  Thomas Petazzoni
# Copyright (C) 2010  Gaël Utard

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import locale, os

# The ogr module is now known as osgeo.ogr in recent versions of the
# module, but we want to keep compatibility with older versions
try:
    from osgeo import ogr
except ImportError:
    import ogr


import coords

class ShapeFile:
    """
    This class represents a shapefile (.shp) that can be added to a Mapnik map
    as a layer. It provides a few methods to add some geometry 'features' to
    the shape file.
    """

    def __init__(self, bounding_box, out_filename, layer_name):
        """
        Args:
            bounding_box (BoundingBox): bounding box of the map area.
            out_filename (string): path to the output shape file to generate.
            layer_name (string): layer name for the shape file.
        """

        self._bbox = bounding_box
        self._filepath = out_filename
        self._layer_name = layer_name

        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(out_filename):
            # Delete the detination file first
            driver.DeleteDataSource(out_filename)

        self._ds = driver.CreateDataSource(out_filename)
        self._layer = self._ds.CreateLayer(self._layer_name,
                                           geom_type=ogr.wkbLineString)

    def _add_feature(self, feature):
        f = ogr.Feature(feature_def=self._layer.GetLayerDefn())
        f.SetGeometryDirectly(feature)
        self._layer.CreateFeature(f)
        f.Destroy()

    def add_horiz_line(self, y):
        """Add a new latitude line at the given latitude."""
        line = ogr.Geometry(type = ogr.wkbLineString)
        line.AddPoint_2D(self._bbox.get_top_left()[1], y)
        line.AddPoint_2D(self._bbox.get_bottom_right()[1], y)
        self._add_feature(line)
        return self

    def add_vert_line(self, x):
        """Add a new longitude line at the given longitude."""
        line = ogr.Geometry(type = ogr.wkbLineString)
        line.AddPoint_2D(x, self._bbox.get_top_left()[0])
        line.AddPoint_2D(x, self._bbox.get_bottom_right()[0])
        self._add_feature(line)
        return self

    def add_shade_from_wkt(self, wkt):
        """Add the polygon feature to the shape file."""
        # Prevent the current locale from influencing how the WKT data is
        # parsed by OGR.
        prev_locale = locale.getlocale(locale.LC_ALL)
        locale.setlocale(locale.LC_ALL, "C")

        try:
            poly = ogr.CreateGeometryFromWkt(wkt)
            self._add_feature(poly)
        finally:
            locale.setlocale(locale.LC_ALL, prev_locale)

        return self

    def flush(self):
        """
        Commit the file to disk and prevent any further addition of
        new longitude/latitude lines
        """
        self._ds.Destroy()
        self._ds = None

    def get_layer_name(self):
        """Returns the name of the layer used for this shape file."""
        return self._layer_name

    def get_filepath(self):
        """Returns the path to the destination shape file."""
        return self._filepath

    def __str__(self):
        return "ShapeFile(%s)" % self._filepath


if __name__ == "__main__":
    # Basic unit test
    g = ShapeFile(coords.BoundingBox(44.4883, -1.0901, 44.4778, -1.0637),
                  '/tmp/mygrid.shp', 'test')
    g.add_horiz_line(44.48)
    g.add_vert_line(-1.08)
    g.flush()
