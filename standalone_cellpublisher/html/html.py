#!/usr/bin/python
#
#    Copyright (C) 2009 Lope A. Florez, Christoph Lammers
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
html.py

A library to create an html file where all the JavaScripts needed for
CellPublisher will reside. It consists of a function that creates
html <script> tags that are independent of CellPublisher, and a wrapper
function that receives all the configuration.

Functions:

- _create_script_tag: create a <script src="..."></script> line
- generate_html: save the resulting html in the given path

Usage:

>>> generate_html(settingsDict)

Output:

An HTML file saved in the target folder, that is based on the input settings.
For a detailed explanation of the settings, please refer to the documentation
of the generate_html function.

"""

__author__ = 'lflorez@gwdg.de'

from string import Template
import os
import codecs

def _create_script_tag(src, indentation=0):
    """
    Return a string with a script tag, that points to "src" and has the
    indentation level "indentation" (with tabs).

    """
    indent = '\t' * indentation 
    begin = r'<script src="'
    end = r'" type="text/javascript"></script>'
    return ''.join([indent, begin, src, end])

def generate_html(settings):
    """
    Generate an html file in the target path, based on the input settings. 

    The settings are entered as a dict, with the following convention:

    - "template_path" -> string : the path where the HTML template resides
    - "target_path" -> string :   the path where the HTML should be saved when 
                                  it is ready.
    - "title" -> string :         title of the html page
    - "scripts" -> list(string):  a list of "src" arguments that should be
                                  loaded as JavaSripts in the header of the
                                  HTML
    - "maxZoom" -> number:        The number of zoom levels in the diagram
    - "author" -> string:         The copyright owner of the diagrams
    - "downloadPDBs" -> boolean:  Decide whether or not to include support for
                                  the JSmol, that has to be installed
                                  in a folder called JSmol right above
                                  the target folder
                                     
    """
    # Save the settings into handy local variables
    templatePath = settings["template_path"]
    targetPath = settings["target_path"]
    title = settings["title"]
    scripts = settings["scripts"]
    maxZoom = settings["maxZoom"]
    author = settings["author"]
    downloadPDBs = settings["downloadPDBs"]
    
    # Create the output file
    out = codecs.open(os.path.join(targetPath,"index.html"),
                      encoding='utf-8',  # To support non-ASCII characters
                      mode="w")

    # Create the scripts section
    scriptTags = list()
    for script in scripts:
        scriptTags.append(_create_script_tag(script))
    # Add a script line for the Jmol applet if downloadPDBs = True
    if downloadPDBs:
        scriptTags.append(_create_script_tag("../JSmol/JSmol.min.js"))
    scriptsSection = '\n\t\t'.join(scriptTags)

    # Read in the template
    template_html = Template(file(templatePath).read())
    
    # Substitute the contents
    d = dict(title=title,
             scripts=scriptsSection,
             maxZoom=maxZoom,
             author=author)
    replaced_text = template_html.safe_substitute(d)
    out.write(replaced_text)
         
    # Save the output file
    out.close()
    
