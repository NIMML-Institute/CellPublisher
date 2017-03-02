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
processMarkersTest.py

Unit tests for processMarkers.py

"""

__author__ = 'lflorez@gwdg.de'

import unittest
from xml.dom.minidom import parseString

import processMarkers

class TestReplaceLinks(unittest.TestCase):
    """
    Test the replacement of identifiers for links to the specified entity
    in the corresponding database.

    """

    def setUp(self):

        ### Crete a dummy xml file ###
        self.xml = """<?xml version="1.0" ?>
        <markers>
            <marker class="SIMPLE_MOLECULE" id="s34" name="2-oxoglutarate" x="1717" y="401">
		<notes>
<![CDATA[PubChem: 51
]]>		</notes>
            </marker>
            <marker class="PROTEIN" id="s7" name="AlaR" x="1700" y="1250">
		<notes>
<![CDATA[
Uniprot: P42411
PMID: 11157946
PMID: 18974048
]]>		</notes>
            </marker>
        </markers>
"""
        ### Process the file with the function ###
        self.processedXml = processMarkers.process_markers(
                                    parseString(self.xml))
        print "Original version: \n"
        print self.xml
        print "\n\n Processed version:"
        print self.processedXml.toxml()
        

    def testPubMed(self):
        """Check if PubMed links are created successfully"""

        # Get the content of the second "notes" element
        notes2 = self.processedXml.getElementsByTagName("notes")[1].toxml()

        # Write the link that should be there
	link = r'PubMed: <a href="http://www.ncbi.nlm.nih.gov/pubmed/11157946">11157946</a>'

        # Check if the link is contained in the notes
        link_place = notes2.find(link)

        self.assertNotEqual(link_place, -1,
                            "The PubMed link was not parsed correctly!")

    def testUniprot(self):
        """Check if Uniprot links are created successfully"""

        # Get the content of the second "notes" element
        notes2 = self.processedXml.getElementsByTagName("notes")[1].toxml()

        # Write the link that should be there
        link = r'Uniprot: <a href="http://www.uniprot.org/uniprot/P42411">'
        link += 'P42411</a>'

        # Check if the link is contained in the notes
        link_place = notes2.find(link)

        self.assertNotEqual(link_place, -1,
                            "The UniProt link was not parsed correctly!")

    def testPubChem(self):
        """Check if PubChem calls result in a link and the image"""

        # Get the content of the second "notes" element
        notes2 = self.processedXml.getElementsByTagName("notes")[0].toxml()

        # Write the link that should be there
        link = r'PubChem: <a href="http://pubchem.ncbi.nlm.nih.gov/'
        link += r'summary/summary.cgi?cid=51">51</a>'
        link += r'<img width="300px" src="http://pubchem.ncbi.nlm.nih.gov'
        link += '/image/imgsrv.fcgi?t=l&cid=51"> <br/>'

        # Check if the link is contained in the notes
        link_place = notes2.find(link)

        self.assertNotEqual(link_place, -1,
                            "The PubChem link was not parsed correctly!")

### Creation of the testing suite ###
       
def suite():

    tests = [
        TestReplaceLinks,
        ]

    testList = list()
    for test in tests:
        sub_suite = unittest.TestLoader().loadTestsFromTestCase(test)
        testList.append(sub_suite)
     
    suite = unittest.TestSuite(testList)
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
