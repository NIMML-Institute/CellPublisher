#!/usr/bin/python
#
#    Copyright (C) 2009 Lope A. Florez
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""


"""

__author__ = 'lflorez@gwdg.de'

import os
import unittest

import settingsTest
import wrapperTest
import tiles.tilesTest
import markers.markersTest
import html.htmlTest

if __name__ == "__main__":
    reload(settingsTest)
    reload(wrapperTest)
    reload(tiles.tilesTest)
    reload(markers.markersTest)

    # Save the current directory
    cwd = os.getcwd()
    
    unittest.TextTestRunner(verbosity=2).run(settingsTest.suite())
    unittest.TextTestRunner(verbosity=2).run(wrapperTest.suite())

    os.chdir(os.path.join(cwd,"tiles"))
    unittest.TextTestRunner(verbosity=2).run(tiles.tilesTest.suite())

    os.chdir(os.path.join(cwd,"markers"))
    unittest.TextTestRunner(verbosity=2).run(markers.markersTest.suite())

    os.chdir(os.path.join(cwd,"html"))
    unittest.TextTestRunner(verbosity=2).run(html.htmlTest.suite())
