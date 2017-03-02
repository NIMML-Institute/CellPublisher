/**
 *    cellpublisher/marker_links.js: a module to add links to the markers in a Google map
 *
 *	Usage:   cellpublisher.marker_links.create_side_bar();
 *
 *	Requirements:	
 *	
 *	- 	The module acts on the global variable cellpublisher.markers.markers and requires the markers to be loaded 
 *		as an array in that variable. It also requires the global variable cellpublisher.markers.markersLoaded
 *
 *	- 	The "div" where the links are should have an id of "side_bar".
 *	
 *	-	There should be a "UL" called "OTHER_list" where all the links add that do not match and speciesClass. In
 *		addition, for each speciesClass with links, there should be a "ul" with id "(speciesClass)_list".
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
cellpublisher.marker_links = {}; 

// Create a "private" variable for the module
cellpublisher.marker_links._timer = {};


/**
 *	Add links to the markers of a Google map, after all the markers have been loaded
 * 	
 * 	Usage: cellpublisher.marker_links.create_side_bar( );
 *	
 **/  
cellpublisher.marker_links.create_side_bar = function() {
    
    // Indicate that the markers are loading
    var pElement = document.createElement("p");
    pElement.id = "loading";
    pElement.innerHTML = "Loading the markers...";
    document.getElementById("side_bar").appendChild(pElement);	
    
    // Delay the execution of the code until all the markers have loaded (the test occurs in the _init function)
    cellpublisher.marker_links._timer = setInterval(cellpublisher.marker_links._init, 50);
    
}

//////////////////////  AUXILIARY FUNCTIONS /////////////////////////

/**
 *	Trigger a click event on the marker with index "i"
 *	
 **/  
cellpublisher.marker_links._clickLink = function(i) {
    google.maps.event.trigger(cellpublisher.markers.markers[i], "click");
}

/**
 *	Add the link to the corresponding unordered list ("ul"). If a link with that name already exists, create a new "ul" to 
 * 	accomodate all the links with the same name.
 *	
 **/  
cellpublisher.marker_links._addToSideBar = function(marker) {
    
    // Get the DOM element where the link will be added
    var tag = document.getElementById(marker.data.speciesClass + "_list");
    
    // Default to "OTHER_list" if no suitable DOM element is found
    if (!tag) {
	tag = document.getElementById("OTHER_list");
    }
    
    // Add the content of the link
    var liElem = document.createElement("li");
    var aElem = document.createElement("a");
    
    aElem.innerHTML = marker.data.name;
    aElem.href = "javascript:cellpublisher.marker_links._clickLink(" + marker.i + ");";
    liElem.appendChild(aElem);
    
    /////
    // Decide where to append the element. This proceeds in three stages. First, a "ul" that matches the name of 
    // the marker is searched (this would mean that there were other markers already by that name in the list). 
    // If no list is found, try to search for a "li" element with the same name. In that case, move that link to a new "ul" and
    // append the new link to the newly created "ul". If no link with that name is present (yet) just add the link to the root.
    /////
    
    // Stage 1: Check if there is already a list with links with that name:
    summaryLi = document.getElementById("summary_" + marker.data.name);
    
    if (!summaryLi) {	// There is no summary element. Proceed to the next stages 
	// Stage 2: check if a marker with that name already exists
	var elementExists = false;
	var allLiElementsOfTag = tag.getElementsByTagName("li");
	
	// Check link after link until you find a link with the same name... (in reverse order for efficiency)
	for (var i=allLiElementsOfTag.length-1; i>=0 ; i--) {
	    var liName = allLiElementsOfTag[i].getElementsByTagName("a")[0].innerHTML;
	    if (liName == marker.data.name) { 
		// A link with the same name exists. Thus, create a new summary list and
		// append both links to this list.
		elementExists = true;
		var newLiElement = document.createElement("li");
		newLiElement.innerHTML = marker.data.name + "(...)";
		
		var ulElement = document.createElement("ul");
		ulElement.id = "summary_" + marker.data.name;
		
		ulElement.appendChild(allLiElementsOfTag[i]);
		ulElement.appendChild(liElem);
		newLiElement.appendChild(ulElement);
		tag.appendChild(newLiElement);
		return;
	    }
	}
	
	// Quality control: by this time, all the names have been searched and none matched the new name. Thus,
	// an element with the same name cannot exist.
	if (elementExists) {
	    throw new Error("Error in the marker_links module...");
	}
	
	// Stage 3: Since no summary link exists and no other link has the same name, just append the link to the
	// root of the DOM element
	tag.appendChild(liElem);
	
    } else {  // Continuation of Stage 1: a summary list has been found, just add the link to it.
	summaryLi.appendChild(liElem);
    }
}

/**
 *	Test if the markers have been loaded and call the function to add each individual marker
 * 	
 **/  
cellpublisher.marker_links._init = function() {
    
    // Make a local copy of the variable
    var markers = cellpublisher.markers.markers;
    
    // Do nothing, unless the markers have loaded.
    if(cellpublisher.markers.markersLoaded) {
	// Stop wating for the markers to load
	clearInterval(cellpublisher.marker_links._timer);
	
	// Clear the notice that the links are loading
	var pElement = document.getElementById("loading");
	if (pElement) {
	    var pElementParent = pElement.parentNode;
	    pElementParent.removeChild(pElement);
	}
	
	// Call the _addToSideBar function on each individual marker
	for (var i=0; i< markers.length; i++) {
	    cellpublisher.marker_links._addToSideBar(markers[i]);
	}
    } 
}