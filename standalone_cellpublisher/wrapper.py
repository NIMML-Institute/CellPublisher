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
Main file of CellPublisher.

Define the settings in settings.py, then run this file using the command:

$ python wrapper.py

"""

__author__ = 'lflorez@gwdg.de'

import os
import argparse
import shutil
import sys
from string import Template
from xml.dom.minidom import parse

from tiles import tiles
from markers import markers, processMarkers
from html import html

from django.utils.encoding import smart_str, smart_unicode

class AlreadyExistsError(Exception):
    """
    A utility Exception that is thrown when a file that has to be created
    from scratch already exists.

    """
    pass

def create_target_folder(pathToSBML,
                         targetDirectoryRoot,
                         includeFileName = True):
    """
    Create an empty folder named after the SBML file in the Results folder.
    (Only if the folder does not already exist).

    If the folder already exists before creation, a AlreadyExists Exception
    is raised.

    Returns the path to the target folder.
    
    """

    if includeFileName:
        # Get the name of the target directory from the SBML file
        sbmlFile = os.path.basename(pathToSBML)
        targetDirectory = os.path.splitext(sbmlFile)[0]
    
        # Check if the directory already exists.
        if os.path.isdir(os.path.join(
                            targetDirectoryRoot,
                            targetDirectory)):
            # Raise an error indicating that the folder already exists
            raise AlreadyExistsError('A folder already exists with name "' +
                                     targetDirectory + '"')

        # Create the directory
        pathToTarget = os.path.join(targetDirectoryRoot,
                              targetDirectory)
        os.mkdir(pathToTarget)

    else:
        pathToTarget = targetDirectoryRoot
        
    # Create the sub-directories for the CSS and JavaScript files
    print "Creating subdirectories in the target folder ..."
    os.mkdir(os.path.join(pathToTarget,"css"))
    os.mkdir(os.path.join(pathToTarget,"cellpublisher"))
    os.mkdir(os.path.join(pathToTarget,"scripts"))
    os.mkdir(os.path.join(pathToTarget,"xml"))
    print " ... Done!"
    
    return os.path.normpath(pathToTarget)    

def create_tiles(pathToTarget, pathToImage):
    """
    Serve as interface for the tiles.generate_tiles function.
    Returns a duple with offset that was needed to frame the image to the next
    available zoom level and the value of this level.
    
    """

    # Create a directory called "tiles" in the target folder
    tilesPath = os.path.join(pathToTarget,"tiles")
    os.mkdir(tilesPath)

    # Run the function that creates the tiles
    print "Creating the different zoom levels..."
    (offset, maxZoom) = tiles.generate_tiles(pathToImage, tilesPath)
    print " ... Done!"
    return (offset, maxZoom)

def create_xml(offset, pathToTarget, pathToSBMLFile, downloadPDBs):
    """Serve as interface for the markers.create_marker_xml function."""

    # Run the function that creates the xml
    print "Creating a file with the position and content of markers"
    markersXML = markers.create_marker_xml(pathToSBMLFile, offset)
    print " ... Done!"

    # Modify the content of the markers based on keywords
    print "Adding links to online databases..."
    markersXML = processMarkers.process_markers(markersXML,
                                                pathToTarget,
                                                downloadPDBs)
    print " ... Done!"

    # Save the xml in the target directory
    targetFileName = os.path.join(pathToTarget,"xml","markers.xml")
    markersFile = open(targetFileName,"w")
    markersFile.write(smart_str(markersXML.toprettyxml()))
    markersFile.close()
                                           

def create_html(pathToTargetFolder, maxZoom, title, author, key, downloadPDBs):
    """Serve as interface for the html.generate_html function."""

    print "Creating the entry HTML page for the diagram..."
    # Initialize the settings
    htmlSettings = dict()
    
    # Add the path where the template of the html file can be found
    htmlSettings["template_path"] = get_template_path()
    
    # Add the path where the index.html file will be saved
    htmlSettings["target_path"] = pathToTargetFolder   

    # Add the title of the page
    htmlSettings["title"] = title

    # Add the author of the diagram
    htmlSettings["author"] = author

    # Add the value of downloadPDBs
    htmlSettings["downloadPDBs"] = downloadPDBs

    # Create a list of scripts that should be included
    scripts = list()
    scripts.append(r"https://maps.googleapis.com/maps/api/js?key=" +
                   r"&amp;v=2&amp;sensor=false&amp;key=" +
                   key)
    scripts.append(r"scripts/markermanager.js")
    scripts.append(r"scripts/downloadurl.js")
    scripts.append(r"cellpublisher/customMap.js")
    scripts.append(r"cellpublisher/markers.js")
    scripts.append(r"cellpublisher/marker_links.js")
    scripts.append(r"cellpublisher/marker_checkboxes.js")
    htmlSettings["scripts"] = scripts

    # Add the maxZoom level of the map
    htmlSettings["maxZoom"] = maxZoom

    # Generate the HTML file
    html.generate_html(htmlSettings)
    print " ... Done!"

def copy_additional_files(pathToTarget):
    """Add the css and JavaScript files to the target folder."""

    print "Copying additional files..."
    # Create a shortcut to os.path.join
    f = os.path.join

    # Copy the css files
    shutil.copy(get_style_path(), f(pathToTarget,"css"))

    # Copy the JavaScript files
    scripts = [
        "customMap.js",
        "markers.js",
        "marker_links.js",
        "marker_checkboxes.js",
        "default.png",
        ]
    for script in scripts:
        shutil.copy(f(get_javascript_path(), script),
                    f(pathToTarget,"cellpublisher"))
    thirdPartyScripts = [
        "markermanager.js",
        "downloadurl.js"
        ]
    for script in thirdPartyScripts:
        shutil.copy(f(get_javascript_path(),"thirdParty",script),
                    f(pathToTarget,"scripts"))
    print " ... Done!"


def get_style_path():
    """
    Return the path where the stylesheet for the resulting HTML
    is located.
    
    """
    path = os.path.join(get_path_of_this_dir(),
                        "HTML and CSS", "css", "style.css")
    return path

def get_template_path():
    """Return the path where the HTML template is located"""
    path = os.path.join(get_path_of_this_dir(),
                        "HTML and CSS", "template.html")
    return path

def get_javascript_path():
    """Return the path where the javascript files located"""
    path = os.path.join(get_path_of_this_dir(),
                        "JavaScript")
    return path

def get_path_of_this_dir():
    """
    Return the absolute path to the directory where file holding the code
    resides (not the path from which the code was called).

    """
    if __name__ == "__main__":
        return os.path.dirname(sys.argv[0])
    else:
        return os.path.dirname(__file__)

def execute(params):
    """
    Executes the functions in the makers, tiles, and html folders in
    the correct order.

    Depends on a 'params' dictionary that has be supplied as input. These
    are the keys of the dictionary:

    apiKey : The Google maps API key
    targetFolder : The resulting files will be saved in this path
    pathToImage : Path to the PNG image exported from CellDesigner
    pathToSBML : Path to the CellDesigner SBML file
    title : Title of the resulting HTML page
    author : Copyright owner of the diagram

    Returns a dictionary that has the output of the contained functions. This
    dictionary has the following keys:

    offset:   A tuple with the x and y displacement needed to surround the 
              diagram with a white border and center it on the canvas
    maxZoom:  The zoom levels present in the diagram (starting from 0)
    

    """

    print "Running the conversion...."
    try:
        pathToTarget = create_target_folder(params['pathToSBML'],
                                            params['targetFolder'],
                                            False)

        (offset, maxZoom) = create_tiles(pathToTarget, params['pathToImage'])

        create_xml(offset, pathToTarget, params['pathToSBML'],
                   params['downloadPDBs'])

        create_html(pathToTarget, maxZoom,
                    params['title'],
                    params['author'],
                    params['apiKey'],
                    params['downloadPDBs'],
                    )
        
        copy_additional_files(pathToTarget)
        
        print "... conversion finished!!!"
        return {'offset':offset, 'maxZoom':maxZoom}
    except:
        print "An error occurred... please check the input files."
        raise
     

if __name__ == "__main__":

    try:
        import settings
        
        if settings.GOOGLE_MAPS_KEY == '':
            message = "Error: the Google maps API key has not been added in"
            message += " the settings module.\n"

            print message
            
        else:    

            params = dict()

            # create argument parser for specifying command line arguments
            parser = argparse.ArgumentParser(description='Specify the paths for the SBML, image, and target folders.')

            # add three arguments where you can specify different paths and default if no commands are entered
            parser.add_argument('-s', '--sbml', help='The path to the CellDesigner SBML file', default=settings.PATH_TO_SBML_FILE, required=False)
            parser.add_argument('-i', '--image', help='The path to the image folder',default=settings.PATH_TO_IMAGE, required=False)
            parser.add_argument('-o', '--output', help='The path to the output folder', default=settings.PATH_TO_TARGET_FOLDER, required=False)
            args = parser.parse_args()
            
            params['pathToSBML'] = args.sbml
            params['targetFolder'] = args.output
            params['pathToImage'] = args.image
            params['title'] = settings.TITLE_OF_HTML
            params['author'] = settings.COPYRIGHT_OWNER
            params['apiKey'] = settings.GOOGLE_MAPS_KEY
            params['downloadPDBs'] = True

            print "Running..."

            if os.path.isdir(params['targetFolder']):
                raise AlreadyExistsError
            else:
                os.mkdir(params['targetFolder'])
            
            execute(params)
            
        print "Done!"

    except AlreadyExistsError:
        print "Error: The output folder specified already exists: " + params['targetFolder']
        
    except ImportError:    
        print "Error: The settings file could not be found."
