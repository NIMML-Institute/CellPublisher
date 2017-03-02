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
wrapperTest.py

A module to test the functionality of wrapper.py

"""

__author__ = 'lflorez@gwdg.de'

import filecmp
import os
import shutil
import tempfile
import unittest

import wrapper
import settings

class TestCreateDirectory(unittest.TestCase):
    """
    The module should be able to create an empty directory in the right place.

    """
    def testDetectFolderAlreadyExists(self):
        """
        The module should throw an error if the target folder already exists.

        """
        skipRemoval = False
        try:
            os.makedirs("../../../Results/test")
        except:
            skipRemoval = True
        self.assertRaises(wrapper.AlreadyExistsError,
                          wrapper.create_target_folder,
                          settings.PATH_TO_SBML_FILE,
                          settings.PATH_TO_TARGET_FOLDER)
        if not skipRemoval:
            os.rmdir("../../../Results/test")

    def testFolderIsCreated(self):
        """
        The module should create a folder in the specified path.

        """
        folderExists = os.path.isdir("../../../Results/test")
        if folderExists:
            self.assertRaises(wrapper.AlreadyExistsError,
                              wrapper.create_target_folder,
                              settings.PATH_TO_SBML_FILE,
                              settings.PATH_TO_TARGET_FOLDER)
        else:
            result = wrapper.create_target_folder(  
                            settings.PATH_TO_TARGET_FOLDER
                            )
            self.assert_(os.path.isdir("../../../Results/test"),
                         "Test if the directory is created")
            os.rmdir("../../../Results/test")
            
class TestCreateXML(unittest.TestCase):
    """
    The wrapper module should be able to call the appropriate function
    in the xml subfolder.

    """
    def setUp(self):
        """ Run the function with the path of a temporary folder as input. """
        # Create a temporary directory.
        self.pathToTempFolder = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.pathToTempFolder, "xml"))
        
        # Run the function
        wrapper.create_xml((1496, 2221),
                           self.pathToTempFolder,
                           settings.PATH_TO_SBML_FILE)

    def tearDown(self):
        """ Delete the temporary folder. """
        shutil.rmtree(self.pathToTempFolder)

    def testCreatedAndPrecalculatedOutputAreTheSame(self):
        """
        When creating the xml from the test file, the markers xml should be
        the same as the ones in the test output from the markers.py module.
        
        """
        # Define the paths where the test xml and function output reside
        pathToCreatedOutput = os.path.join(self.pathToTempFolder,
                                           "xml",
                                           "markers.xml")
        pathToPrecalculatedOutput = os.path.normpath(
                                    "./markers/testOutput/test/markers.xml")

        # Compare the resulting files in the two folders        
        filesAreEqual = filecmp.cmp(pathToCreatedOutput,
                                    pathToPrecalculatedOutput)
        self.assert_(filesAreEqual,
                "The precalculated and executed files should be the same.")

class TestCreateHTML(unittest.TestCase):
    """
    The wrapper module should be able to call the appropriate function in the
    html folder.

    """

    def setUp(self):
        """ Run the function with the path of a temporary folder as input. """
        # Create a temporary directory.
        self.pathToTempFolder = tempfile.mkdtemp()
        
    def tearDown(self):
        """ Delete the temporary folder. """
        shutil.rmtree(self.pathToTempFolder)

    def testWithGoldStandard(self):
        """
        Test the create_html function with an HTML file that was created
        before.

        """
        # Run the function (maxZoom for the test image is 5)
        wrapper.create_html(self.pathToTempFolder, 5,
                            settings.TITLE_OF_HTML,
                            settings.COPYRIGHT_OWNER,
                            settings.GOOGLE_MAPS_KEY
                            )
        file1 = os.path.join(self.pathToTempFolder, "index.html")
        file2 = os.path.join(".", "html", "testOutput", "index.html")
        comparison = filecmp.cmp(file1, file2)
        self.assert_(comparison,
                     "The create_html function does not reproduce the " +
                     "content in the folder 'html/testOutput'") 

class TestCopyAdditionalFiles(unittest.TestCase):
    """
    The module should be able to copy the css and JavaScript files to the
    target folder.

    """

    def setUp(self):
        """ Run the function with the path of a temporary folder as input. """
        # Create a temporary directory.
        self.pathToTempFolder = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.pathToTempFolder,"css"))
        os.mkdir(os.path.join(self.pathToTempFolder,"cellpublisher"))
        os.mkdir(os.path.join(self.pathToTempFolder,"scripts"))
        
    def tearDown(self):
        """ Delete the temporary folder. """
        shutil.rmtree(self.pathToTempFolder)
    
    def testPresenceOfTheAdditionalFiles(self):
        """
        Test the copy_additional_files function with a handmade list
        of files that should be present.

        """
        wrapper.copy_additional_files(self.pathToTempFolder)
        listOfFiles = [
            os.path.join("css","style.css"),
            os.path.join("cellpublisher","customMap.js"),
            os.path.join("cellpublisher","markers.js"),
            os.path.join("cellpublisher","marker_links.js"),
            os.path.join("cellpublisher","marker_checkboxes.js"),
            os.path.join("scripts","markermanager.js"),
            ]
        for file_ in listOfFiles:
            fullPath = os.path.join(self.pathToTempFolder, file_)
            self.assert_(os.path.exists(fullPath),
                         "The following file has not been copied: " +
                         fullPath)
        
def suite():

    tests = [
        TestCreateDirectory,
        TestCreateXML,
        TestCreateHTML,
        TestCopyAdditionalFiles,
        ]

    testList = list()
    for test in tests:
        sub_suite = unittest.TestLoader().loadTestsFromTestCase(test)
        testList.append(sub_suite)
     
    suite = unittest.TestSuite(testList)
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner().run(suite())

