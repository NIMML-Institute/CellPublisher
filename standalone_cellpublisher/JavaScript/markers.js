/**
 *    cellpublisher/markers.js: a module to populate a Google map with markers, based on an xml file
 *
 *	Usage:   cellpublisher.markers.createMarkers(
 *					{xml: <String>, 
 *					map: <GMap2 object>, 
 *					maxZoom: <Number>}
 *				 );
 *
 *		This module creates a global function called createMarkers(settings) in the namespace 
 *		cellpublisher.markers.
 *	 	
 *		After execution of this function, it creates the following variables in the cellpublisher.markers 
 *		namespace:
 *		-	markers (Array): an array with all the markers created. 
 *		-	mm (MarkerManager object): the instance of MarkerManager that contains all the markers
 *		-	markersLoaded (Boolean): initializes to "false", but then becomes "true" 
 *							   when the script has added all markers to the map.
 *		
 *		The input to the function is an object with the following properties:
 *		-	xml (String): A path to the xml file that contains marker information 
 *					(see below for the structure of this xml)
 *		-	map (Object): A GMap2 object (or extended GMap object, e.g. with a custom map)
 *		-	maxZoom (Number): The maximum zoom level of the map
 *		
 *		The xml input should have the following format:
 *		
 *		<markers>
 *			<marker id="..." name="..." x="..." y="...">
 *	 			<notes>
 *					HTML in the markers infowindow.
 *				</notes>
 *				...
 *			</marker>
 *			...
 *		</markers>
 *		
 *		The "notes" node is optional. If none is supplied, the info window will contain just the 
 *		"name" attribute of the marker. If one or more "notes" nodes are present, they will all 
 *		appear together in the info window.
 *		
 *		Appart from the Google maps API, the script relies on the open source MarkerManager. These modules 
 *		should be loaded in the host document. The MarkerManager script can can be downloaded here:
 *
 *		http://gmaps-utility-library-dev.googlecode.com/svn/tags/markermanager/1.1/src/markermanager.js
 *
 */

/**
 *    Copyright (C) 2009 Lope A. Florez, Christoph Lammers
 *
 *    This program is free software: you can redistribute it and/or modify
 *    it under the terms of the GNU General Public License as published by
 *    the Free Software Foundation, either version 3 of the License, or
 *    (at your option) any later version.
 *
 *    This program is distributed in the hope that it will be useful,
 *    but WITHOUT ANY WARRANTY; without even the implied warranty of
 *    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *    GNU General Public License for more details.
 *
 *    You should have received a copy of the GNU General Public License
 *    along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

// Create the namespace for the function  
var cellpublisher;
if (!cellpublisher) cellpublisher = {};
cellpublisher.markers = {};

// Create the global variables under the namespace cellpublisher.markers
cellpublisher.markers.markersLoaded = false;
cellpublisher.markers.markers = [];
cellpublisher.markers.mm = {};
cellpublisher.markers.settings = {};

/**
 *	Create an array of markers and initialize them on the map.
 * 	
 * 	Usage: cellpublisher.markers.createMarkers({
 *					xml: <String>, 
 *					map: <GMap2 object>, 
 *					maxZoom: <Number>}
 *				 );
 *	
 *	xml: A path to the xml that will be used to position the markers	
 *	map: An instance of GMap2 
 *	maxZoom: Maximum Zoom level at which markers should be seen
 *
**/  
cellpublisher.markers.createMarkers = function(settings) {
    
    // Read in the input parameters
    cellpublisher.markers.settings = settings;
    
    if (!cellpublisher.markers.settings.minZoom) {
        cellpublisher.markers.settings.minZoom = 3;
    }

    // Initialize necessary objects of the Google Maps API
    cellpublisher.markers.mm = cellpublisher.markers.settings.mm;
    // var proj = new GMercatorProjection(18);
    
    // Download the xml file and process it
    downloadUrl(cellpublisher.markers.settings.xml, function(doc){
	
	// parse the xml to a DOM structure
	var xml = xmlParse(doc);
	
	// parse this xml DOM structure to a JavaScript array of marker objects
	var mrks = cellpublisher.markers._parseMarkersXML(xml);
        
        // new icon to reduce the default icon size
        var new_icon = {
            url: "//maps.gstatic.com/intl/en_us/mapfiles/marker.png",
            scaledSize: new google.maps.Size(15,25),
            anchor: new google.maps.Point(8, 25)
        };

        var opt = { 
            map: cellpublisher.markers.settings.map,
            icon: new_icon,
            draggable: false,
            clickable: true,
            dragCrossMove: true
        }

	for (var i=0; i < mrks.length; i++) {
	    
	    var point = new google.maps.Point(mrks[i].x, mrks[i].y);
	    
	    //Project them to latitude, longitude coordinates
	    opt.position = cellpublisher.markers.fromPixelToLatLng(point);

	    //Create a new google.maps.Marker (with added properties)
	    var marker = new google.maps.Marker(opt);
	    marker.data = mrks[i];
	    // marker.show();
	    marker.i = i;
	    marker.coord = opt.position;
	    
            // Add it to the marker manager
	    cellpublisher.markers.mm.addMarker(marker, cellpublisher.markers.settings.minZoom);

	    // Open the info window on click
	    cellpublisher.markers._registerMarker(marker);
	    
	    // Add the marker to the global "markers" array
	    cellpublisher.markers.markers.push(marker);	
	}

		// Destroys and releases the memory of the JSmol applet when the info window
		// is closed or the user clicks on another marker. This is vital - the canvas
		// will not be removed properly if this is not called.
		google.maps.event.addListener(cellpublisher.infoWindow, "closeclick", function() {
			if (window.applet0 != null) {
				Jmol._destroy(window.applet0);
				window.applet0 = null;
			}
		});
	
	

	// All the markers in the xml file have been processed, thus change the state of the
	// "markersLoaded" variable
	cellpublisher.markers.markersLoaded = true;
    });
}

//////////////////////  AUXILIARY FUNCTIONS /////////////////////////

/**
 *	Returns an array of marker objects. Each object has the following properties:
 *		- x  (Number) ->  X-coordinate of the marker
 *		- y  (Number) ->  Y-coordinate of the marker
 *		- id  (String) ->  id of the marker	
 *		- speciesClass (String) -> class of the marker (e.g. "PROTEIN")
 *		- name (String) ->  name of the marker
 *		- notes (null or Array)  ->  array with all the notes for the marker		
 *	
 *	The input to the function is a parsed XML object, e.g. one returned by the GXml function   
 * 		
 **/  
cellpublisher.markers._parseMarkersXML = function(xml) {
    
    // Initialize the result
    var speciesMarkers = [];
    
    var markers = xml.getElementsByTagName("marker");
    
    // for each "marker" element...
    for (var i = 0; i < markers.length; i++) {
	
	// Initialize the object
	var markerObject = {};
	
	// Read the properties of the object
	markerObject.id =   markers[i].getAttribute("id");
	markerObject.name = markers[i].getAttribute("name");
	markerObject.x =    markers[i].getAttribute("x");
	markerObject.y =    markers[i].getAttribute("y");
	markerObject.speciesClass = markers[i].getAttribute("class");
	
	// Get the notes of the marker, if any
	markerObject.notes = [];
	
	var notes = markers[i].getElementsByTagName("notes");
	
	// Search for CDATA sections within these nodes and add each of those to the 
	// "markerObject.notes" array
	for (var j = 0; j < notes.length; j++) {
	    var content = notes[j].childNodes;
	    for (var k = 0; k < content.length; k++) {
		if (content[k].nodeType == 4) { // The node is a CDATA section
		    markerObject.notes[j] = content[k].nodeValue;		
		}
	    }
	}
	
	// Add the marker to the result
	speciesMarkers.push(markerObject);
    }
    
    return speciesMarkers;
}


/**
 *	Make the info window appear when the user clicks the marker
 *			
 *	Input: a GMarker with the following added properties:
 *		- coord (GLatLng): The coordinates of the marker that will be added
 *		- data.name: The name of the marker (will appear first in the info window)
 *		- data.notes: The extra content of the info window
 *	
 **/  
cellpublisher.markers._registerMarker = function(marker) {
    // When the marker is clicked...
    google.maps.event.addListener(marker, "click", function() { 	

		// if the user clicks from one marker to another, make sure to destroy the applet from memory
		if (window.applet0 != null) {
			Jmol._destroy(window.applet0);
			window.applet0 = null;
		}
			
		// get the notes for the marker (links, pdb num, etc.)
		var markerNotes = marker.data.notes.toString();	
		var pdbNum = "";
			
		if (marker.data.notes.toString().match(/structureId=\w+"/)) {
			pdbNum = marker.data.notes.toString().match(/structureId=\w+"/)[0].match(/\w+/g)[1];

			var Info = {
				width: 300,
				height: 250,
				debug: false,
				color: "black",
				disableJ2SLoadMonitor: true,
				disableInitialConsole: true,
				addSelectionOptions: false,
				serverURL: "http://chemapps.stolaf.edu/jmol/jsmol/php/jsmol.php",
				use: "HTML5 Java",
				j2sPath: "../JSmol/j2s", 
				script: "load =" + pdbNum + "; set platformSpeed 1; select all; spin on; spacefill off; wireframe off;cartoon;color cartoon chain;select ligand;wireframe 40;spacefill 120;select all;model 0;"
            }
		
			// this creates the applet, but the Google Maps Info Window doesn't allow for Javascript to be ran
			// when setting the content, so we have to render the canvas manually after opening the window
			var applet = Jmol.getApplet("applet0", Info);
			var appletHtml = Jmol.getAppletHtml(applet);
			
			cellpublisher.infoWindow.setContent("<h1>" + marker.data.name + "</h1> <div id=\"marknotes\" style=\"max-width:300px;max-height:700px\">" + markerNotes + appletHtml + "</div>");
		}
		else {
			// default for normal pathway markers without a pdb number
			cellpublisher.infoWindow.setContent("<h1>" + marker.data.name + "</h1> <div id=\"marknotes\" style=\"max-width:300px;max-height:700px\">" + markerNotes + "</div>");
		}
        cellpublisher.infoWindow.open(cellpublisher.markers.settings.map, marker);
		
		// now render the canvas, IMPORTANT!
		if (window.applet0 != null) {
			window.applet0._cover(false);
		}
    });
}

cellpublisher.markers.fromPixelToLatLng = function (pixel) {
    var numTiles = 1 << cellpublisher.markers.settings.maxZoom;

    var proj = cellpublisher.markers.settings.map.getProjection();
    var point = new google.maps.Point(pixel.x / numTiles, pixel.y / numTiles);

    return proj.fromPointToLatLng(point);
}