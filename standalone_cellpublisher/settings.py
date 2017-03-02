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
settings.py

CellPublisher settings file.

Change this file to tweak the results of the CellPublisher program.

"""

__author__ = 'meiyongguo@hotmail.com'


import os.path

# Path to the folder where the output of CD2maps will be saved.
# You can use relative paths as in '../other_folder'.
# Use forward slashes '/' even under Windows.
# If you need to specify an absolute path, use the os.path module.
PATH_TO_TARGET_FOLDER = '../Results'

# Path to the image file exported from CellDesigner.
PATH_TO_IMAGE = '../CellDesigner_files/test.png'

# Path to the CellDesigner file from which the previous image was created
PATH_TO_SBML_FILE = '../CellDesigner_files/test.xml'

# Enter here the Google maps key for your server. You can get a key at
# http://code.google.com/intl/en/apis/maps/signup.html
GOOGLE_MAPS_KEY = 'AIzaSyBbgwWaNZv1aQsWvTDQrGGRGavskjwWeLQ'

# Title of the HTML page
TITLE_OF_HTML = 'MIEP Online CellPublisher Model' 

# The text in the lower right of the map that will indicate the copyright
# owner of the map images that will be displayed
COPYRIGHT_OWNER = 'MIEP Project'  
