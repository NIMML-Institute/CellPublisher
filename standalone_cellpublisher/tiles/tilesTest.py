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

A module to test the functionality of tiles.py

"""

__author__ = 'lflorez@gwdg.de'

import filecmp
import math
import os
import shutil
import tempfile
import unittest

import Image

import tiles

class TestSizeUtilityFunctions(unittest.TestCase):
    """
    Test the _calculate_new_size and _calculate_offset functions.
    They should be able to return the next size canvas that can frame
    the given image size, and the place where this image should be pasted.

    """

    def testCalculateNewSizeWithDifferentInputs(self):
        """
        Test _calculate_new_size with exact, small, large, medium sizes.

        """
        sizeNewSizePairs = [
            ((256, 256), (256, 256)),
            ((400, 400), (512, 512)),
            ((1024, 20), (1024, 1024)),
            ((700, 512), (1024, 1024)),
            ((1, 1), (256, 256)),
            ((2000, 4000), (4096, 4096)),
            ((2048, 2), (2048, 2048)),
            ]
        for size, newSize in sizeNewSizePairs:
            calculatedSize = tiles._calculate_new_size(size)
            self.assertEqual(newSize, calculatedSize,
                             "The entered size " + str(size) +
                             " should be converted to " + str(newSize) +
                             " instead of " + str(calculatedSize) + ".")

    def testCalculateOffset(self):
        """
        Test _calculate_offset with exact, small, large, medium sizes.

        """
        sizeOffsetPairs = [
            ((256, 256), (0, 0)),
            ((400, 400), (56, 56)),
            ((1024, 20), (0, 502)),
            ((700, 512), (162, 256)),
            ((1, 1), (127, 127)),
            ((2000, 4000), (1048, 48)),
            ((2048, 2), (0, 1023)),
            ]
        for size, offset in sizeOffsetPairs:
            calculatedOffset = tiles._calculate_offset(size)
            self.assertEqual(offset, calculatedOffset,
                             "The entered size " + str(size) +
                             " should get offset " + str(offset) +
                             " instead of " + str(calculatedOffset) + ".")
        

class TestFrameImage(unittest.TestCase):
    """
    Test the _frame_image function. It should be able to detect if an
    image should be framed and frame it accordingly.

    """

    def _create_images(self, sizeInput, sizeOutput, offset):
        """
        Utility function to create test images. Creates a blue image with
        sizeInput, a white image with sizeOutput, moves the first image
        by the given offset, and returns the images that have to be compared.

        """
        # Create the input
        mockInput = Image.new("RGB", sizeInput, "blue")
        # Create the corresponding output
        mockOutput = Image.new("RGB", sizeOutput, "white")
        mockOutput.paste(mockInput, offset)
        # Run the function with the mock input
        realOutput = tiles._frame_image(mockInput)
        return (mockOutput, realOutput)

    def testCorrectlySizedImage(self):
        """ Test with a mock image that already has a correct size. """
        mockImage = Image.new("RGB", (512,512))
        returnedImage = tiles._frame_image(mockImage)
        self.assertEqual(mockImage.tostring(), returnedImage.tostring(),
                         "Mock image and product image should be the same")

    def testImageWithDifferentSizes(self):
        """ Test different image sizes to see if they are correctly framed """
        sizes = [ (600, 900), (600, 901),
                  (601, 900), (601, 901),
                ]
        sizeOutput = (1024, 1024)
        offsets = [ (212, 62), (212, 61),  # 212 + 600 + 212 = 1024
                    (211, 62), (211, 61),
                  ]
      
        for size, offset in zip(sizes, offsets):
            images = self._create_images(size, sizeOutput, offset)
            self.assertEqual(images[0].tostring(), images[1].tostring(),
                         "Input with size" + str(size) +
                         " should be framed to mock output.")

class TestCreateZoomLevels(unittest.TestCase):
    """
    Test the _create_zoom_levels function. It should be able to create
    different zoom levels of the same image for different sizes.

    """

    def testWithWhiteImage(self):
        """
        Test that a white image of size 4096 is returned as five images
        of different sizes.

        """
       
        mockInput = Image.new("RGB", (4096, 4096), "white")
        realResult = tiles._create_zoom_levels(mockInput)
        self.assertEqual(len(realResult), 5,
                         "Output and Mock lists should be the same length")
        for i in range(5):
            # Create an image of border size 256 x 2^i 
            border = 256*math.pow(2,i)
            im = Image.new("RGB", (border, border), "white")
            # Compare it with the one resulting from the function
            self.assertEqual(
                    im.tostring(),
                    realResult[i].tostring(),
                    "The function should resize an image of size 4096 x 4096")

    def testCorrectResize(self):
        """
        Test if the re-scaling is working properly.

        """
        # Create a mock image of size 1024 x 1024
        mockImage = Image.new("RGB", (1024, 1024), "white")
        smallBox = Image.new("RGB", (256, 256), "blue")
        mockImage.paste(smallBox, (0, 256))
        mockImage.paste(smallBox, (256, 512))
        mockImage.paste(smallBox, (512, 0))
        mockImage.paste(smallBox, (768, 768))
        
        # Create a version reduced to half the size
        mockImage2 = mockImage.resize((512, 512), Image.ANTIALIAS)

        # Create a version reduced four-fold
        mockImage3 = mockImage.resize((256, 256), Image.ANTIALIAS)
        
        # Use the function
        output = tiles._create_zoom_levels(mockImage)
        
        # Test the resulting output
        self.assertEqual(output[0].tostring(), mockImage3.tostring(),
                    "Should resize to the lowest level")
        self.assertEqual(output[1].tostring(), mockImage2.tostring(),
                    "Should resize to the middle level")
        self.assertEqual(output[2].tostring(), mockImage.tostring(),
                    "Should not resize the highest level")

class TestCutTiles(unittest.TestCase):
    """
    Test the function _cut_tiles. It should be able to cut the images
    of different sizes to the appropriate image tiles.
    
    """

    def testWithChessBoard(self):
        """
        Create a list of colorful chess boards with 1, 4, and 16 cells and
        try the function out.
        
        """
        # Color of the cells
        colors = ["red","green","blue","white",
                  "blue", "red", "white", "green",
                  "white","blue","green","red",
                  "green","white","red","blue"]

        # Images of the cells
        cells = [Image.new("RGB", (256, 256), color)
                          for color in colors]

        # Create the big chess board
        bigChessBoard = Image.new("RGB", (1024, 1024))
        # Paste in the colored squares, in the same configuration
        # as above
        i = 0   # Counter for the elements in the colors list
        for yOffset in range(0, 1024, 256):
            for xOffset in range(0, 1024, 256):  
                bigChessBoard.paste(cells[i], (xOffset, yOffset))
                i += 1
                
        # Create the medium chess board
        mediumChessBoard = bigChessBoard.crop((0, 0, 512, 512))

        # Create the small chessboard
        smallChessBoard = cells[0]

        # Create the input
        mockInput = [smallChessBoard, mediumChessBoard, bigChessBoard]

        # Run the function
        result = tiles._cut_tiles(mockInput)

        # Compare the result of the small chess board (it should be unchanged)
        self.assertEqual(result[0][0][0].tostring(),
                         smallChessBoard.tostring(),
                         "The small chess board should remain the same.")

        # Compare the result of the medium chess board
        ## Make a list with the expected result:
        expectedResult = [Image.new("RGB", (256, 256), "red"),
                          Image.new("RGB", (256, 256), "green"),
                          Image.new("RGB", (256, 256), "blue"),
                          Image.new("RGB", (256, 256), "red")
                         ]
        # Make a one to one comparison
        i = 0  # Counter for the elements in the list expectedResult
        for line in result[1]:
            for column in line:
                self.assertEqual(column.tostring(),
                                 expectedResult[i].tostring(),
                            "The middle chess board should remain the same.")
                i += 1

        # Compare the result of the large chess board
        i = 0 # Counter for the colors list
        for line in result[2]:
            for column in line:
                # Create a mock image
                tempIm = Image.new("RGB", (256, 256), colors[i])
                self.assertEqual(column.tostring(),tempIm.tostring(),
                            "The large chess board should remain the same.")
                i += 1
        
class TestGenerateTiles(unittest.TestCase):
    """
    Test the generate_tiles function. It should be able to read an image from
    a file path, process the image and save it in the target path.

    """

    def setUp(self):
        """
        Create a temporary file and directory to serve as input for the
        function.

        """
        # Create a temp variable
        self.tempFileVariable = tempfile.mkstemp('.png')
        # Save the name of the file
        self.tempFile = self.tempFileVariable[1]
        # Save the name of the temporary directory in a variable
        self.tempDir = tempfile.mkdtemp()

    def tearDown(self):
        """
        Delete the temporary files and folders that were created.

        """
        # Close the temporary file
        os.close(self.tempFileVariable[0])
        # Delete the temporary file
        os.remove(self.tempFile)
        # Delete the temporary folder
        shutil.rmtree(self.tempDir)

    def testWithImageWithoutNeedForProcessing(self):
        """
        Test with a white image of size (256, 256). It only needs to be
        renamed an saved in a different folder.

        """
        # Create the image
        im = Image.new("RGB", (256, 256), "blue")

        # Save the created image in the tempFile
        im.save(self.tempFile)
                
        # Run the function
        tiles.generate_tiles(self.tempFile, self.tempDir)

        # Evaluate if the image is in the tempFolder
        target = Image.open(os.path.join(self.tempDir,"0_0_0.png"))
        self.assertEqual(target.tostring(), im.tostring(),
                    "The processed image should be the same as the original.")

    def testWithCustomMadeImage(self):
        """
        Test with an image of size (400, 300), that has to be framed, zoomed,
        cut, and saved properly.
        """

        # Create the image (it will have four colored sections)
        im = Image.new("RGB", (400, 300))
        sections = list()
        for color in ["blue", "red", "green", "yellow"]:
            sections.append(Image.new("RGB", (200, 150), color))
        im.paste(sections[0], (0, 0))
        im.paste(sections[1], (200, 0))
        im.paste(sections[2], (0, 150))
        im.paste(sections[3], (200, 150))
        im.save(self.tempFile)
                
        # Create the images that we hope to obtain
        expectedResults = list()

        ## Create a dummy image first (properly framed)
        ## that will be resized and cropped
        dummyImage = Image.new("RGB", (512, 512), "white")
        dummyImage.paste(im, (56 ,106)) # 56 + 400 + 56 = 512
                                        # 106 + 300 + 106 = 512
        
        ## Create the (256, 256) image (smallest image)
        smallestImage = dummyImage.resize((256, 256), Image.ANTIALIAS)
        expectedResults.append(smallestImage)

        ## Create the four tiles of the next zoom level by croping the dummy
        ## image
        for x in [0, 256]:
            for y in [0, 256]:
                box = (x, y, x + 256, y + 256)
                expectedResults.append(dummyImage.crop(box))

        
        # Use the function in the tiles module
        tiles.generate_tiles(self.tempFile, self.tempDir)

        # Check if the exported files are properly named
        outputFileNames = os.listdir(self.tempDir)
        expectedFileNames = ["0_0_0.png",
                             "1_0_0.png",
                             "1_0_1.png",
                             "1_1_0.png",
                             "1_1_1.png"
                            ]
        self.assertEqual(outputFileNames, expectedFileNames,
                         "The files should be named {Z}_{X}_{Y}.png")

        # Check if these files contain the right images
        ## enumerate is used, since the images in the expectedResults
        ## list are in the same order than the expected images in the
        ## expectedFileNames list. This means, that the third file name
        ## ("1_0_1.png") has index "2" in the expectedFileNames list and
        ## is saved in expectedResults[2]
        for i, fileName in enumerate(expectedFileNames):
            tempImage = Image.open(os.path.join(self.tempDir,fileName))
            self.assertEqual(tempImage.tostring(),
                             expectedResults[i].tostring(),
                             "The tile file should have the correct data")
            
    def testDifferentOffsetOutputs(self):
        """
        Test with simple images, that need different offsets, to check the
        return value of the function.

        """
        sizeOffsetPairs = [
            ((256, 256), ((0, 0), 0)),
            ((512, 512), ((0, 0), 1)),
            ((400, 300), ((56, 106), 1)),
            ((1200, 80), ((424, 984), 3)),
            ((200, 100), ((28, 78), 0)),
            ((5200, 5200), ((1496, 1496), 5)),
            ((333, 715), ((345, 154), 2)),
                ]
                    
        for size, offset in sizeOffsetPairs:
            im = Image.new("RGB", size, "white")
            im.save(self.tempFile)
            calculatedOffset = tiles.generate_tiles(self.tempFile,
                                                    self.tempDir)
            self.assertEqual(offset, calculatedOffset,
                             "Real offset and calculated offset should be " +
                             "the same: " + str(offset) + " != " +
                             str(calculatedOffset))
            


class TestWithGoldStandard(unittest.TestCase):
    """
    This test does not adhere completely to the "Test-driven development"
    paradigm, since the test was designed after the code was written and run.

    When all the previous tests passed, the generate_tiles function was used
    to create tiles for the test input of CellPublisher. This TestCase is
    then used to check that everything works as it did in after all previous
    tests passed.

    """

    def testWithGoldStandard(self):
        """
        Test that the CellPublisher test file is correctly converted to tiles.

        """
        # Create a temporary directory for the output
        tempDir = tempfile.mkdtemp()

        # Run the generate_tiles function
        pathToTestImage = os.path.join("testInput","test.png")
        tiles.generate_tiles(pathToTestImage,tempDir)
        
        # Compare the created output with the precalculated one
        comparison = filecmp.dircmp(tempDir,
                                    os.path.join("testOutput", "test"))
        self.assert_(not comparison.left_only,
                     "There should be no extra file in the output.")
        self.assert_(not comparison.right_only,
                     "There should be no extra file in the test input.")

        # Delete the temporary directory
        shutil.rmtree(tempDir)

### Creation of the testing suite ###
       
def suite():

    tests = [
        TestSizeUtilityFunctions,
        TestFrameImage,
        TestCreateZoomLevels,
        TestCutTiles,
        TestGenerateTiles,
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

