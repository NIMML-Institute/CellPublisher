/**
 *    cellpublisher/marker_checkboxes.js: a module to activate the functionality of checkboxes. After activation,
 *                                                                    a click on the checkboxes will show/hide all markers and links of the 
 *                                                                    specified class.
 *
 *	Usage:   cellpublisher.marker_checkboxes.activate_checkboxes( );
 *
 *	Requirements:	
 *	
 *	- 	This module assumes that the checkboxes have a "name" attribute that correspondes to the id of the 
 *	   	DOM element that contains the links to the markers. It also assumes that the "class" property of the
 *		target DOM element can be set to "active" or "inactive"
 *	
 *	- 	The module also assumes that the id of the DOM element containing the form has the id "form".
 *
 *	- 	The module acts on the global variable cellpublisher.markers.markers and requires the markers to be loaded 
 *		as an array in that variable. 
 *
 *	- 	The markers of the array mentioned above should have a data.speciesClass property that corresponds to the
 *		"name" of the checkbox
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
cellpublisher = cellpublisher || {};
cellpublisher.marker_checkboxes = {};

// Create a local synonym for the global markers variable 
cellpublisher.marker_checkboxes._markers = {};

/**
 *	Add behavior to the checkboxes of the DOM element with id "form"
 * 	
 * 	Usage: cellpublisher.marker_checkboxes.activate_checkboxes( );
 *	
 **/  
cellpublisher.marker_checkboxes.activate_checkboxes = function() {
    
    // Initialize the local synonym for the global variable
    cellpublisher.marker_checkboxes._markers = cellpublisher.markers.markers;
    
    // Get all the checkboxes of the form
    var checkBoxes = document.getElementById("form").getElementsByTagName("input");
    
    // for each checkbox...
    for (var i=0; i < checkBoxes.length; i++) {
	var checkBox = checkBoxes[i];
	
	// When clicked, check if it was activated or inactivated and call the appropriate response
	checkBox.onclick = function(e) {
	    var me = cellpublisher.marker_checkboxes._getActivatedObject(e);
	    var activated = me.checked;
	    
	    if (activated) {
		cellpublisher.marker_checkboxes._showAll(me.name);
	    }
	    else {
		cellpublisher.marker_checkboxes._hideAll(me.name);
	    }
	}
    }
}

//////////////////////  AUXILIARY FUNCTIONS /////////////////////////

/**
 *	Cross-Browser compatible method to obtain the source of an event
 * 	
 * 	Usage: cellpublisher.marker_checkboxes._getActivatedObject( e <Event>);
 *	
 **/  	
cellpublisher.marker_checkboxes._getActivatedObject = function(e) {
    var obj;
    
    if(!e) {
	// early version of IE
	obj = window.event.srcElement;
    } else if (e.srcElement) {
	// IE 7 or later
	obj = e.srcElement;
    } else {
	// DOM Level 2 browser
	obj = e.target;
    }
    
    return obj;
}

/**
 *	Hide all the markers and links that fit to the given name
 * 	
 * 	Usage: cellpublisher.marker_checkboxes._hideAll( name <String>);
 *	
 *	Input: 
 *	-	name: a string that corresponds to the speciesClass that will be acted upon
 **/  	
cellpublisher.marker_checkboxes._hideAll = function(name) {
    
    var markers = cellpublisher.marker_checkboxes._markers;
    
    // Search for the DOM element that has the links
    var elem = document.getElementById(name);
    
    // If no DOM element was found, report this to the browser.
    if (!elem) {
	throw new Error("The name of the checkbox corresponds to no ID in the DOM");
	return;
    }
    
    // Mark the links as inactive
    elem.className = "inactive";
    
    // Hide all the markers that have this name as speciesClass
    for (var i = 0; i < markers.length; i++) {
	if (markers[i].data.speciesClass == name) {
	    markers[i].closeInfoWindow();
	    markers[i].hide();
	}
    }
}	

/**
 *	Show all the markers and links that fit to the given name
 * 	
 * 	Usage: cellpublisher.marker_checkboxes._showAll( name <String>);
 *	
 *	Input: 
 *	-	name: a string that corresponds to the speciesClass that will be acted upon
 **/ 
cellpublisher.marker_checkboxes._showAll = function(name) {
    
    var markers = cellpublisher.marker_checkboxes._markers;
    
    // Search for the DOM element that has the links
    var elem = document.getElementById(name);
    
    // If no DOM element was found, report this to the browser.
    if (!elem) {
	throw new Error("The name of the checkbox corresponds to no ID in the DOM");
	return;
    }
    
    // Mark the links as active
    elem.className = "active";
    
    // Show all the markers that have this name as speciesClass
    for (var i = 0; i < markers.length; i++) {
	if (markers[i].data.speciesClass == name) {
	    markers[i].show();
	}
    }
}