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
tilesTest.py

A module to test the functionality of html.py

"""

__author__ = 'lflorez@gwdg.de'

import filecmp
import os
import shutil
import tempfile
import unittest

import html

class TestCreateScriptTag(unittest.TestCase):
    """
    Test the _create_script_tag function. It should return a string with
    a script element, that contains the given src argument, and the given
    indentation.

    """

    def testWithNoIndentation(self):
        """
        Test the _create_script_tag function with input that does not have any
        indentation.

        """
        sources = ["utils.js",
                   "http://maps.google.com/maps?\
file=api&amp;v=2&amp;sensor=false&amp;key=ABQIAAAAdv_U95xs-4ol4uJZ4Zf62BQ1OHO\
bilvMXQEfVwyQQiIHA0XYZWkkkLsKl1w8ppIP7QsEZTRRndEgg",
                   "./javascript/utils.js",
                   ]
        tags = [
            r'<script src="utils.js" type="text/javascript"></script>',
            r'<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;sensor=false&amp;key=ABQIAAAAdv_U95xs-4ol4uJZ4Zf62BQ1OHObilvMXQEfVwyQQiIHA0XYZWkkkLsKl1w8ppIP7QsEZTRRndEgg" type="text/javascript"></script>',
            r'<script src="./javascript/utils.js" type="text/javascript"></script>',
            ]

        for src, tag in zip(sources, tags):
            result = html._create_script_tag(src)
            self.assertEqual(result, tag,
                    "The faulty script tag is: " + str(result) +
                    ", instead it should be " + tag)

    def testWithIndentation(self):
        """
        Test the _create_script_tag with two arguments: src and indentation.

        """
        sources = [
            "utils.js",
            "./javascript/test.js",
            "http://path.to.script/script.js",
            ]
        indentation = [
            3,
            2,
            5,
            ]
        tags = [
            '\t\t\t' + r'<script src="utils.js" type="text/javascript"></script>',
            '\t\t' + r'<script src="./javascript/test.js" type="text/javascript"></script>',
            '\t\t\t\t\t' + r'<script src="http://path.to.script/script.js" type="text/javascript"></script>',
            ]
        for src, indent, tag in zip(sources, indentation, tags):
            result = html._create_script_tag(src, indent)
            self.assertEqual(result, tag,
                             "The faulty script tag is: " + str(result))

class TestGenerateHTML(unittest.TestCase):
    """
    Test the generate_html function. It should be able to save the html in
    the location specified in the settings, and incorporate all the aspects
    that are included in these settings.

    """

    def setUp(self):
        """
        Create a temporary file directory to serve as input for the
        function.

        """
        # Save the name of the temporary directory in a variable
        self.tempDir = tempfile.mkdtemp()
                
    def tearDown(self):
        """
        Delete the temporary directory that was created.

        """
        # Delete the temporary folder
        shutil.rmtree(self.tempDir)

    def testWithOneScript(self):
        """ Test the generate_html function with the simplest settings. """
        # Define the path to the test html files
        pathToTemplate = os.path.join(".","templates",
                                      "testTemplate.html")
        pathToExpectedResults = os.path.join(".","testInput","test1.html")
        # Set up the settings for the generate_html function
        settings = dict()
        settings["template_path"] = pathToTemplate
        settings["target_path"] = self.tempDir
        settings["title"] = "Pathway"
        settings["scripts"] = ["utils.js"]
        settings["maxZoom"] = 5
        settings["author"] = "Owner"
        # Run the function and evaluate the results
        html.generate_html(settings)
        comparison = filecmp.cmp(pathToExpectedResults,
                                 os.path.join(self.tempDir, "index.html"))
        self.assert_(comparison,
                     "The template is not parsed correctly, since it doesn't" +
                     " match the hand-made result.")

    def testWithSeveralScripts(self):
        """ Test the generate_html function with extra scripts. """
        # Define the path to the test html files
        pathToTemplate = os.path.join(".","templates",
                                      "testTemplate.html")
        pathToExpectedResults = os.path.join(".","testInput","test2.html")
        # Set up the settings for the generate_html function
        settings = dict()
        settings["template_path"] = pathToTemplate
        settings["target_path"] = self.tempDir
        settings["title"] = "Pathway"
        settings["maxZoom"] = 5
        settings["author"] = "Owner"
        settings["scripts"] = ["utils.js",
                               "./cellpublisher/maps.js",
                               "tree.js",
                               ]
        # Run the function and evaluate the results
        html.generate_html(settings)
        comparison = filecmp.cmp(pathToExpectedResults,
                                 os.path.join(self.tempDir, "index.html"))
        self.assert_(comparison,
                     "The template is not parsed correctly, since it doesn't" +
                     " match the hand-made result.")


### Creation of the testing suite ###
       
def suite():

    tests = [
        TestCreateScriptTag,
        TestGenerateHTML,
        ]

    testList = list()
    for test in tests:
        sub_suite = unittest.TestLoader().loadTestsFromTestCase(test)
        testList.append(sub_suite)
     
    suite = unittest.TestSuite(testList)
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

