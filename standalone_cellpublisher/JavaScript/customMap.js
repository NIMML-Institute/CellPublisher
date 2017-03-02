/**
 *    cellpublisher/customMap.js: a module to create a custom made Google map type
 *
 *		This module creates a global function cellpublisher.createCustomMap(settings).
 *	 	The function returns a GMap2 object, that contains the Google map with the custom
 *		made map as the only active map type, with mouse wheel scrolling enabled, and with
 *		a little overview window.
 *	 
 *		This module requires a "tiles" directory, where the tiles for each zoom level are stored.
 *		Each tile should have the format {Z}_{X}_{Y}.png, where {Z} is the zoom level, {x} is the
 *		"x" tile coordinate and {Y} the "y" tile coordinate.
 *
 **/

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

// Create a namespace for the function 
var cellpublisher;
if (!cellpublisher) cellpublisher = {};
cellpublisher.customMap = {};

// Create the infowindow
if (!cellpublisher.infoWindow) {
    cellpublisher.infoWindow = new google.maps.InfoWindow();
}

/**
 *	Returns a GMap2 object that contains only the customGoogleMap and navigation controls.
 *	
 *	The input to the function is the settings object that should contain the following parameters:
 *		-	copyright_owner: A string with the owner of the images that will be displayed
 *		- 	maxZoom: The maximum zoom level that is available
 *		- 	div: name of the <div> where the map will reside	 
 *
 *	If any of the parameters are missing, the function throws an error.
 * 		
 **/  
cellpublisher.customMap.createCustomMap = function(settings) {  
    
    /***************************************
     *
     *	Check if all the parameters are present
     *
     ****************************************/
    if (!settings) {
	throw new Error("The createCustomMap needs a settings object...");
    }
    
    with(settings) {
	if (!copyright_owner || !maxZoom || !div) 
	    throw new Error("The createCustomMap function misses some settings...");
    }
    
    /***************************************
     *
     *        STEP 1: Configure and create the 
     *                      custom map type.
     *
     *         Every custom layer has a copyright 
     *         notice for its images, tiles of images
     *         for each zoom level, and a projection.
     *
     ***************************************/
    
    // Set the boundaries of the copyright notice and the text concerning the copyright owner of the images
    copyright = document.createElement("div");
    copyright.id = "map-copyright";
    copyright.style.fontSize = "11px";
    copyright.style.fontFamily = "Arial, sans-serif";
    copyright.style.margin = "0 2px 2px 0";
    copyright.style.whiteSpace = "nowrap";
    copyright.innerHTML = "Copyright: " + settings.copyright_owner;

    
    // Create the tile layers based on the images in the "tiles" folder
    var NetWorkMapType = new google.maps.ImageMapType({
        getTileUrl: function(tile, zoom) {
            var numTiles = 1 << map.getZoom();

            // We do not repeat in y directions since the markers are not repeated.
            if (tile.y < 0 || numTiles <= tile.y) {
                return "cellpublisher/default.png";
            }

            // Repeat in x direction
            var x = tile.x;
            
            while (x < 0) {
                x += numTiles;
            }
            
            while (numTiles <= x) {
                x -= numTiles;
            }
            
            return "tiles/" + zoom + "_" + x + "_" + tile.y +".png"; 
        },
        tileSize: new google.maps.Size(256, 256),
        opacity: 1.0,
        maxZoom: settings.maxZoom,
        minZoom: 0,
        isPng: true,
        name: 'Network'
    });
    
    /***************************************
     *
     *        STEP 2: Create a  Google Map,
     *                       add the new map type to it, 
     *                       remove the typical types 
     *                       (e.g. Satellite), and activate 
     *                       the navigation controls.
     *
     ***************************************/   
    
    var mapOptions = {
        zoom: 3,
        center: new google.maps.LatLng(0, 0),
        mapTypeControl: false,
        streetViewControl: false
    };

    var map = new google.maps.Map(document.getElementById(settings.div), mapOptions);
    map.mapTypes.set('NetWork', NetWorkMapType);
    map.setMapTypeId('NetWork');
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(copyright);

    return map;
}
