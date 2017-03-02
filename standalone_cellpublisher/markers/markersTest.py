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
markersTest.py

Unit tests for the markers.py library

"""

__author__ = 'lflorez@gwdg.de'

import os
import unittest
from xml.dom.minidom import parse, parseString

import markers

class TestTypesetConverter(unittest.TestCase):
    """
    Test the function _correct_typesetting. The function should be able to
    convert all subscript and superscript to the right html code.

    """
    def testNonEndingSuperscript(self):
        """Test the conversion of a superscript without ending _endsuper_"""
        string = "Ca_super_2+"
        newString = markers._correct_typesetting(string)
        self.assertEqual(newString, "Ca<sup>2+</sup>")

    def testEndingSuperscript(self):
        """Test the conversion of a superscript with ending _endsuper_"""
        string = "p_super_53_endsuper__active"
        newString = markers._correct_typesetting(string)
        self.assertEqual(newString, "p<sup>53</sup>_active")

    def testNonEndingSubscript(self):
        """Test the conversion of a subscript without ending _endsub_"""
        string = "CO_sub_2"
        newString = markers._correct_typesetting(string)
        self.assertEqual(newString, "CO<sub>2</sub>")

    def testEndingSubscript(self):
        """Test the conversion of a subscript with ending _endsub_"""
        string = "H_sub_2_endsub_O"
        newString = markers._correct_typesetting(string)
        self.assertEqual(newString, "H<sub>2</sub>O")

    def testLineBreaks(self):
        """Test the conversion of a line break coded as _br_"""
        string = "Line_br_break"
        newString = markers._correct_typesetting(string)
        self.assertEqual(newString, "Line<br/>break")

    def testGreekLetters(self):
        """Test the conversion of several greek letters to correct HTML 4.0"""
        string = "1_alpha,2_beta,3_gamma,4_delta,5_epsilon,6_zeta,7_kappa,"
        newString = markers._correct_typesetting(string)
        expectedResult = "1&alpha;,"
        expectedResult += "2&beta;,"
        expectedResult += "3&gamma;,"
        expectedResult += "4&delta;,"
        expectedResult += "5&epsilon;,"
        expectedResult += "6&zeta;,"
        expectedResult += "7&kappa;,"
        self.assertEqual(newString, expectedResult)


class TestSBMLParser(unittest.TestCase):
    """
    Test the _parse_SBML function of the module. It should be able to read
    a mock SBML file correctly and return the data as a list of _Species_Info
    objects.

    """
    def setUp(self):

        ### Setup the SBML ###
        pathToTestSBML = os.path.join(".",
                                      "testInput",
                                      "testSBML.xml")
        self.sbml = parse(pathToTestSBML)

        # Read in the notes
        notes = self.sbml.getElementsByTagName("celldesigner:notes")
        
        ### Setup the _MarkInfo list ###
        self.species = list()


        ### Create all the species, ordering by name of the species

        # Create the 5th species
        s = markers._MarkInfo()
        s.species_id = "s5"
        s.alias_id = "csa1"
        s.name = "Complex 1"
        s.x = 525
        s.y = 223
        s.speciesClass = "COMPLEX" 
        self.species.append(s)

        # Create the 3rd species
        s = markers._MarkInfo()
        s.species_id = "s3"
        s.alias_id = "sa3"
        s.name = "Gene 1"
        s.x = 119
        s.y = 262
        s.speciesClass = "GENE"
        self.species.append(s)

        # Create the 7th species
        s = markers._MarkInfo()
        s.species_id = "s7"
        s.alias_id = "sa6"
        s.name = "Ion 1"
        s.x = 488
        s.y = 279
        s.speciesClass = "ION"
        s.speciesNotes = notes[1]
        s.complexSpecies = "csa1"
        self.species.append(s)

        # Create the 2nd species
        s = markers._MarkInfo()
        s.species_id = "s2"
        s.alias_id = "sa2"
        s.name = "Protein 2"
        s.x = 508
        s.y = 66
        s.speciesClass = "PROTEIN"
        s.entityNotes = notes[2]
        self.species.append(s)

        # Create the 6th species
        s = markers._MarkInfo()
        s.species_id = "s6"
        s.alias_id = "sa5"
        s.name = "Protein 2"
        s.x = 505
        s.y = 216
        s.speciesClass = "PROTEIN"
        s.speciesNotes = notes[0]
        s.entityNotes = notes[2]
        s.complexSpecies = "csa1"
        self.species.append(s)

        # Create the 1st species
        s = markers._MarkInfo()
        s.species_id = "s1"
        s.alias_id = "sa1"
        s.name = "Protein_sub_1"
        s.x = 301
        s.y = 66
        s.speciesClass = "PROTEIN"
        self.species.append(s)

        # Create the 4th species
        s = markers._MarkInfo()
        s.species_id = "s4"
        s.alias_id = "sa4"
        s.name = "RNA 1"
        s.x = 294
        s.y = 263
        s.speciesClass = "RNA" 
        self.species.append(s)
                 
    def testStandardSpeciesNotes(self):
        """Check if the default value of speciesNotes is None"""
        self.assert_(self.species[0].speciesNotes is None)
            
    def testStandardEntityNotes(self):
        """Check if the default value of entityNotes is None"""
        self.assert_(self.species[0].entityNotes is None)

    def testStandardComplexSpecies(self):
        """Check if the default value of includedSpecies is None"""
        self.assert_(self.species[0].complexSpecies is None)

    def testSBMLParser(self):
        """Check if the mock SBML file can be parsed correctly"""
        result = markers._parse_SBML(self.sbml)
        self.assertEqual(self.species, result)

class TestXMLMarkersCreation(unittest.TestCase):

    def setUp(self):
        pathToInputFile = os.path.join(".",
                                       "testInput",
                                       "testSBML.xml")
        pathToTestOutput = os.path.join(".",
                                        "testInput",
                                        "testXMLOutput.xml")
        offset = (212, 312) # 212 + 600 + 212 = 1024
                            # 312 + 400 + 312 = 1024
        self.output = markers.create_marker_xml(pathToInputFile, offset)
        self.expectedOutput = file(pathToTestOutput).read()
        
    def testCreateMarkerXML(self):
        """
        Test the creation of the marker xml based on the testSBML.xml file.

        The marker xml file should be sorted by the name of the species.

        """
        self.assertEqual(self.output.toprettyxml(), self.expectedOutput,
                    "The SBML input should be converted to the mock output")

class TestWithGoldStandard(unittest.TestCase):
    """
    This test does not adhere completely to the "Test-driven development"
    paradigm, since the test was designed after the code was written and run.

    When all the previous tests passed, the create_marker_xml function was
    used to create an xml file for the test input of CellPublisher. This
    TestCase is then used to check that everything works as it did in after
    all previous tests passed.

    """

    def testWithGoldStandard(self):
        """
        Test that the CellDesigner test file is correctly read and converted
        to the xml needed for the markers.

        """
        pathToTestInput = os.path.join("testInput",
                                       "test.xml")
        pathToTestOutput = os.path.join("testOutput",
                                        "test",
                                        "markers.xml")
        testOutputXML = parse(pathToTestOutput)
        offset = (1496, 2221) # 1496 + 5200 + 1496 = 8192
                              # 2221 + 3750 + 2221 = 8192
        outputDoc = markers.create_marker_xml(pathToTestInput, offset)
        self.assertEqual(testOutputXML.normalize(), outputDoc.normalize(),
                         "The run with the gold standard should produce the " +
                         "precalculated output")
        
### Creation of the testing suite ###
       
def suite():

    tests = [
        TestTypesetConverter,
        TestSBMLParser,
        TestXMLMarkersCreation,
        TestWithGoldStandard,
        ]

    testList = list()
    for test in tests:
        sub_suite = unittest.TestLoader().loadTestsFromTestCase(test)
        testList.append(sub_suite)
     
    suite = unittest.TestSuite(testList)
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())
