#!/usr/bin/python
#
#    Copyright (C) 2009 Christoph Lammers, Lope A. Florez
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
markers.py

Functions to read an SBML file of CellDesigner (http://www.celldesigner.org/)
and extract information about all the species involved, including position
in the diagram, name of the species, and notes.

Class:

- _MarkInfo: a class to temporarily store the parameters of a species

Functions:

- _correct_typesetting: convert CellDesigner's super- and subscript to HTML
- _parse_SBML: extract the required info from the CellDesigner file
- create_marker_xml: return a DOM with the xml of the markers file

Usage:

>>> markers = create_marker_xml("path_to_sbml_file"[, offset=(0,0)])

The offset is added to every x and y coordinate in the SBML file.

Output:

An xml DOM with a document root named markers, containing a marker element
for each species in the diagram. The markers are sorted by the attribute
"name" of the markers. The other attributes are documented in the
markers_xml function.

"""

__author__ = 'lflorez@gwdg.de'

#import pdb
import re
from xml.dom.minidom import parse, getDOMImplementation
from processMarkers import process_markers

class _MarkInfo():
    """
    Convenience class with no methods, used to store the parameters for the
    species after extraction from the xml. Is used primarily by the
    _parseSBML function.

    The class makes strong use of dynamic typing. The attribute list can be
    extended at will.

    The following attributes have default values:

    - entityNotes: meant to store <celldesigner:notes> node objects for
                   the entity (e.g. "Protein notes"), defaults to None
    - speciesNotes: meant to store <celldesigner:notes> node objects for
                    the species, defaults to None
    - complexSpecies: meant for the id of the complexSpeciesAlias in which
                      the species is in, defaults to None
    
    """
    def __init__(self):
        self.entityNotes = None
        self.speciesNotes = None
        self.complexSpecies = None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

def _correct_typesetting(string):
    """
    Convert between CellDesigner's superscript and subscript format and native
    html, with the <sup></sup> and <sub></sub> tags.

    Parameter:

    - string: the string that has to be converted
    
    """

    def _simple_replace(string, pattern, newText):
        """Replaces a continuous string of characters for another."""
        query = re.compile(pattern)
        query_result = query.search(string)
        if query_result:
            string = re.sub(query,
                        newText,
                        string)
        return string

    # Find supercase sections without an _endsuper_ marker
    query = re.compile(r"_super_([a-zA-Z0-9+-]*)$")
    query_result = query.search(string)
    if query_result:
        string = re.sub(query,
                        "<sup>"+query_result.group(1)+"</sup>",
                        string)

    # Find supercase sections with an _endsuper_ marker
    query = re.compile(r"_super_(.*)_endsuper_")
    query_result = query.search(string)
    if query_result:
        string = re.sub(query,
                        "<sup>"+query_result.group(1)+"</sup>",
                        string)

    # Find lowercase sections without an _endsub_ marker
    query = re.compile(r"_sub_([a-zA-Z0-9+-]*)$")
    query_result = query.search(string)
    if query_result:
        string = re.sub(query,
                        "<sub>"+query_result.group(1)+"</sub>",
                        string)

    # Find lowercase sections without an _endsub_ marker
    query = re.compile(r"_sub_(.*)_endsub_")
    query_result = query.search(string)
    if query_result:
        string = re.sub(query,
                        "<sub>"+query_result.group(1)+"</sub>",
                        string)


    # Find line breaks marked as _br_
    string = _simple_replace(string, r"_br_", r"<br/>")

    # Find greek letters ...
    letters = ["alpha", "beta", "gamma", "delta", "epsilon",
               "zeta", "eta", "theta", "iota", "kappa", "lambda",
               "mu", "nu", "xi", "omicron", "pi", "rho", "sigma",
               "tau", "upsilon", "phi", "chi", "psi", "omega", ]
    
    # ... that start and end with a leading _
    for letter in letters:
        string = _simple_replace(string,
                                 "_" + letter + "_",
                                 "&" + letter + ";")

    # ... that only start with a leading _
    for letter in letters:
        string = _simple_replace(string,
                                 "_" + letter,
                                 "&" + letter + ";")
    return string

def _valid_notes(speciesNotes):
    if speciesNotes is None:
	return False

    # Check that the note has a <body>
    bodyNodes = speciesNotes.getElementsByTagName("body")
    if bodyNodes is None:
        # skip the node because it doesn't have an HTML body
	return False;

    htmlBody = bodyNodes[0]
    if not htmlBody.hasChildNodes():
        # skip the node because it doesn't have a content in the
        # HTML body
	return False

    return True


def _parse_SBML(xml):
    """
    Return a list of _MarkInfo objects with the info in the SBML file.

    Parameter:

    - xml: an xml document object of the SBML file

    Output:

    A list of _MarkInfo objects, one for every species and
    celldesigner_species (the latter are used in CellDesigner to denominate
    species inside of a complex).

    See the documentation of the _MarkInfo class for more information on
    the attributes of the objects.

    """

    ### STEP 0: Initialize the result ###

    result = list()

    ### STEP 1: Create some auxiliary dictionaries ###

    def _create_dict(elementTags, xml):
        """
        An auxiliary function that creates a dictionary with all the nodes with
        a tag in the list elementTags, where the key is the "id" parameter
        of the node.

        Parameters:

        - elementTags: a list of tag names
        - xml: an xml node that contains the nodes to extract
        
        """
        answer = dict()        
        for tag in elementTags:
            nodes = xml.getElementsByTagName(tag)
            for node in nodes:
                nodeId = node.getAttribute("id")
                answer[nodeId] = node
        return answer

    
    speciesDict = _create_dict([
        "species",
        "celldesigner:species",
        ], xml)
    aliasDict = _create_dict([
        "celldesigner:speciesAlias",
        "celldesigner:complexSpeciesAlias",
        ], xml)
    entityDict = _create_dict([
        "celldesigner:protein",
        "celldesigner:gene",
        "celldesigner:RNA",
        "celldesigner:AntisenseRNA",
        ], xml)

    reactionDict = _create_dict([
	"reaction",
	], xml)
    
    ### STEP 2: Use the aliasNode dictionary to create all _MarkInfo ###
    ###         objects for species nodes                            ###

    for aliasId, aliasNode in aliasDict.iteritems():
        spInf = _MarkInfo()

        # Get the alias
        spInf.alias_id = aliasId
                
        # Get the id from the alias node
        spInf.species_id = aliasNode.getAttribute("species")

        # Get the species node from the dict (for convenience)
        speciesNode = speciesDict[spInf.species_id]
        
        # Get the name from the species node
        spInf.name = speciesNode.getAttribute("name")

        # Get the class from the species node
        classNode = speciesNode.getElementsByTagName("celldesigner:class")[0]
        spInf.speciesClass = classNode.firstChild.nodeValue

        # Get the coordinates from the alias node
        bounds = aliasNode.getElementsByTagName("celldesigner:bounds")[0]
        x = bounds.getAttribute("x")
        y = bounds.getAttribute("y")
        w = bounds.getAttribute("w")
        h = bounds.getAttribute("h")

        # The markers of the complexes should be in the upper right...
        if spInf.speciesClass == "COMPLEX":
            spInf.x = int(round(float(x)+float(w))) - 5
            spInf.y = int(round(float(y))) + 5
        # But the markers from the remaining species should be a bit offset...
        else:
            spInf.x = int(round(float(x) + 0.8 * float(w)))
            spInf.y = int(round(float(y) + 0.2 * float(h)))

        # Get the entity node (if present) from the species node
        # (for convenience)

        def _get_node_from_tag(tag, entityDict, node):
            """
            Auxiliary function to obtain a node from the entityDict given
            the celldesigner tag name of the reference.

            Parameters:

            - tag: the reference tag (e.g. "celldesigner:rnaReference")
            - entityDict
            - node: the species node that contains the reference tag

            """
            tagNode = node.getElementsByTagName(tag)[0]
            entityId = tagNode.firstChild.nodeValue
            return entityDict[entityId]

        if spInf.speciesClass == "PROTEIN":
            entityNode = _get_node_from_tag(
                "celldesigner:proteinReference",
                entityDict,
                speciesNode)
        elif spInf.speciesClass == "GENE":
            entityNode = _get_node_from_tag(
                "celldesigner:geneReference",
                entityDict,
                speciesNode)
        elif spInf.speciesClass == "RNA":
            entityNode = _get_node_from_tag(
                "celldesigner:rnaReference",
                entityDict,
                speciesNode)
        elif spInf.speciesClass == "ANTISENSE_RNA":
            entityNode = _get_node_from_tag(
                "celldesigner:antisensernaReference",
                entityDict,
                speciesNode)
        else:
            entityNode = None

        # Get the entity notes from the entity node
        if entityNode is not None:
            notes = entityNode.getElementsByTagName("celldesigner:notes")
            if notes:
                spInf.entityNotes = notes[0]

        # Get the species notes from the species node
        notes = speciesNode.getElementsByTagName("notes")
        if notes:
            spInf.speciesNotes = notes[0]
	else:
	    notes = speciesNode.getElementsByTagName("celldesigner:notes")
            if notes:
                spInf.speciesNotes = notes[0]

        # Get the complex the species is in (if any) from the alias node
        if aliasNode.hasAttribute("complexSpeciesAlias"):
            spInf.complexSpecies = aliasNode.getAttribute(
                "complexSpeciesAlias")

        # Append the _MarkInfo object to the list
	# only for those modes with annotations
	# filter out those not
	if _valid_notes(spInf.speciesNotes):
	    result.append(spInf)

    ### STEP 3: Use the aliasNode dictionary to create all _MarkInfo   ###
    ###         objects for reaction nodes                             ###

    for reactionId, reactionNode in reactionDict.iteritems():
        spInf = _MarkInfo()

        # Get the name from the rection node
        spInf.name = reactionId
	#Node.getAttribute("metaid")

        # Get the id from the rectionId
        spInf.species_id = reactionId

        # Set the class to "REACTION"
        spInf.speciesClass = "REACTION"

	spInf.x = 0
	spInf.y = 0

	# get Sepcies for the Reaction    
        nodes = reactionNode.getElementsByTagName("celldesigner:baseReactant");
	if len(nodes) < 2:
	    count = 0
	    for tag in ["celldesigner:baseReactant", "celldesigner:baseProduct",]:
	        nodes = reactionNode.getElementsByTagName(tag)
	        for node in nodes:
		    #pdb.set_trace()
		    bounds = aliasDict[node.getAttribute("alias")].getElementsByTagName("celldesigner:bounds")[0]
		    spInf.x += int(round(float(bounds.getAttribute("x")) + 0.5 * float(bounds.getAttribute("w"))))
		    spInf.y += int(round(float(bounds.getAttribute("y")) + 0.5 * float(bounds.getAttribute("h"))))
		    count += 1

	    spInf.x /= count
	    spInf.y /= count
	else:      
	    bounds1 = aliasDict[nodes[0] .getAttribute("alias")].getElementsByTagName("celldesigner:bounds")[0]
            bounds2 = aliasDict[nodes[1] .getAttribute("alias")].getElementsByTagName("celldesigner:bounds")[0]

	    nodes = reactionNode.getElementsByTagName("celldesigner:baseProduct");    
	    bounds3 = aliasDict[nodes[len(nodes) - 1] .getAttribute("alias")].getElementsByTagName("celldesigner:bounds")[0]           

            x1 = float(bounds1.getAttribute("x")) + 0.5 * float(bounds1.getAttribute("w"))
            y1 = float(bounds1.getAttribute("y")) + 0.5 * float(bounds1.getAttribute("h"))
            x2 = float(bounds2.getAttribute("x")) + 0.5 * float(bounds2.getAttribute("w"))
            y2 = float(bounds2.getAttribute("y")) + 0.5 * float(bounds2.getAttribute("h"))
            x3 = float(bounds3.getAttribute("x")) + 0.5 * float(bounds3.getAttribute("w"))
            y3 = float(bounds3.getAttribute("y")) + 0.5 * float(bounds3.getAttribute("h"))          

            ratiosList = reactionNode.getElementsByTagName("celldesigner:editPoints")[0].childNodes[0].nodeValue.split()
            
            if (len(ratiosList) == 2):
	        ratios = ratiosList[len(ratiosList) - 1].split(",")
	        ratioX = float(ratios[0])
	        ratioY = float(ratios[1])

	        edit1X = x1 + (x2 - x1) * ratioX + (x3 - x1) * ratioY
	        edit1Y = y1 + (y2 - y1) * ratioX + (y3 - y1) * ratioY
	      
                if abs(edit1X - x3) > abs(edit1Y - y3):
		    if edit1X > x3:
                        x3 += 0.5 * float(bounds3.getAttribute("w"))
                    else:
			x3 -= 0.5 * float(bounds3.getAttribute("w"))
                else:
	            if edit1Y > y3:
                        y3 += 0.5 * float(bounds3.getAttribute("h"))
                    else:
			y3 -= 0.5 * float(bounds3.getAttribute("h"))
		
                ratios = ratiosList[0].split(",")
	        ratioX = float(ratios[0])
	        ratioY = float(ratios[1])

	        edit2X = edit1X + (x3 - edit1X) * ratioX - (y3 - edit1Y) * ratioY
	        edit2Y = edit1Y + (y3 - edit1Y) * ratioX + (x3 - edit1X) * ratioY
	
                spInf.x = int(round((edit1X + edit2X)/2))
           	spInf.y = int(round((edit1Y + edit2Y)/2))
 	    else:
                ratios = ratiosList[len(ratiosList) - 1].split(",")
	        ratioX = float(ratios[0])
	        ratioY = float(ratios[1])

	        edit1X = x1 + (x2 - x1) * ratioX + (x3 - x1) * ratioY
	        edit1Y = y1 + (y2 - y1) * ratioX + (y3 - y1) * ratioY

		spInf.x = (edit1X + x3)/2
		spInf.y = (edit1Y + y3)/2

                if abs(edit1X - x3) > abs(edit1Y - y3):
		    if edit1X > x3:
                        spInf.x += 0.25 * float(bounds3.getAttribute("w"))
                    else:
			spInf.x -= 0.25 * float(bounds3.getAttribute("w"))
                else:
	            if edit1Y > y3:
                        spInf.y += 0.25 * float(bounds3.getAttribute("h"))
                    else:
			spInf.y -= 0.25 * float(bounds3.getAttribute("h"))		
			 
                spInf.x = int(round(spInf.x))
                spInf.y = int(round(spInf.y))
 
        # Get the reaction notes from the reaction node
        notes = reactionNode.getElementsByTagName("notes")
        if notes:
            spInf.speciesNotes = notes[0]
	    
        # Append the _MarkInfo object to the list
        # only for those modes with annotations
        # filter out those not
        if _valid_notes(spInf.speciesNotes):
	    result.append(spInf)
 
   ### STEP 4: Sort the result by name and return the list
    
    result.sort(lambda x, y: cmp(x.name, y.name))

    return result
    

def create_marker_xml(pathToSBMLFile, offset=(0,0)):
    """
    Create an XML DOM with a marker element for each species in the SBML file.

    Parameters:

    - pathToSBMLFile: path where the CellDesigner file resides
    - offset (optional, default (0,0)): a duple with the offset to be added
                                        to every coordinate extracted from
                                        the SBML file

    Output:

    An xml document with the following this structure:
    
    <markers>
        <marker id="{1}" name="{2}" class="{3}" x="{4}" y="{5}">
            <notes>...</notes>
        </marker>
        ...
    </markers>

    {1} = id of the speciesAlias
    {2} = name of the species
    {3} = CellDesigner class of the species (e.g. PROTEIN)
    {4} = x coordinate of the right end of the species, corrected by the
          first number in the offset
    {5} = y coordinate of the top end of the species, corrected with the
          second number in the offset

    """
    # Create the empty xml document
    dom = getDOMImplementation()
    doc = dom.createDocument(None,"markers",None)
    top_element = doc.documentElement

    # Parse the input file using the _parse_SBML auxiliary function
    parsedFile = _parse_SBML(parse(pathToSBMLFile))

    # Auxiliary function to create attributes
    def _createAttribute(doc, attributeName, attributeValue, markerNode):
        att = doc.createAttribute(attributeName)
        markerNode.setAttributeNode(att)
        markerNode.setAttribute(attributeName, attributeValue)

    # Auxiliary function to append notes
    def _append_notes(doc, markerNode, speciesNotes):
        if speciesNotes is not None:
            # Check that the note has a <body>
            bodyNodes = speciesNotes.getElementsByTagName("body")
            if bodyNodes is None:
                # skip the node because it doesn't have an HTML body
                return
            htmlBody = bodyNodes[0]
            if not htmlBody.hasChildNodes():
                # skip the node because it doesn't have a content in the
                # HTML body
                return

            # Append the "notes" element to the "marker"
            notesNode = doc.createElement("notes")
            markerNode.appendChild(notesNode)
            # Extract the content of the textHTML
            text = ''.join([node.toxml() for node in htmlBody.childNodes])
            # Replace the line breaks to <br/>
            text = re.sub(r"\n+",r"<br/>\n",text)
            # Put the content in a CDATASection in the note
            cDATASection = doc.createCDATASection(text)
            notesNode.appendChild(cDATASection)
    
    # Create a marker for each species in the input file
    for species in parsedFile:
        # Create the element node
        markerNode = doc.createElement("marker")
        top_element.appendChild(markerNode)

        # Create and set the attributes
        _createAttribute(doc, "id", species.species_id, markerNode)
        _createAttribute(doc, "name", _correct_typesetting(species.name),
                         markerNode)
        _createAttribute(doc, "class", species.speciesClass, markerNode)
        _createAttribute(doc, "x", str(species.x + offset[0]), markerNode)
        _createAttribute(doc, "y", str(species.y + offset[1]), markerNode)

        # Add notes, if any
        _append_notes(doc, markerNode, species.speciesNotes)
        _append_notes(doc, markerNode, species.entityNotes)
        

    return doc
