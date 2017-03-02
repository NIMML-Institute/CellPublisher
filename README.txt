SUMMARY
======

CellPublisher makes CellDesigner diagrams navigable in a web browser.
For more information on usage and getting started: Check out standalone_cellpublisher/UserGuide.docx

USAGE
======

python wrapper.py

OR with optional parameters
--sbml: path to CellDesigner file
--image: path to tile image file
--output: path to folder containing output for server

EXAMPLE: python wrapper.py --sbml <fileName> --image <filName> --output <outputPath>
	 python wrapper.py -s <fileName> -i <filName> -o <outputPath>

CONTENTS
=========

standalone_cellpublisher/
-------------------------
Contains source code (HTML/CSS, Javascript, Python) used to create a dynamic web application for CellPublisher.
It utilizes the Google Maps API and Django to create a navigable diagram that can be ran in your browser with a simple Python server.

web_interface/
-------------------------
Contains files used for hosting CellPublisher on a remote web server (not currently used).

JSmol/
-------------------------
JavaScript-Based Molecular Viewer libraries for displaying interactive 3D models.
JSmol renders 3D proteins with native HTML5/CSS3 whereas Jmol uses Java applets, which have been recently phased out.

CellDesigner_files/
-------------------------
Contains test files for creating a CellPublisher model. Used when parameters aren't specified for invoking wrapper.py.