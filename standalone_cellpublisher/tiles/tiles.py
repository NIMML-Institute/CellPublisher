#!/usr/bin/python
#
#    Copyright (C) 2009 Lope A. Florez, Christoph Lammers
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
tiles.py

A library to create tiles for a custom type Google map from a PNG image, e.g. 
a pathway diagram exported from CellDesigner (http://www.celldesigner.org/).

Requires the Python Imaging Library (PIL) which is freely available at
http://www.pythonware.com/products/pil/

Functions:

- _frame_image: center the image and frame it with a white border
- _create_zoom_levels: do resized versions of the image for every zoom level
- _cut_tiles: cut the images of every zoom level in 256 x 256 px tiles
- generate_tiles: wrapper function - execute all functions in the correct order

Usage:

>>> generate_tiles("path_to_image.png","path_to_target_folder")

Output:

Several tile images in the target folder following the convention:
{Z}_{X}_{Y}.png (e.g. "2_1_0.png" for the image with coordinates (1,0) in
the zoom level 2). In addition, the function returns the offset that was
needed to create the image tiles and the number of zoom levels generated
(starting from 0, so if three zoom level were needed, the function will
return "2").

"""

__author__ = 'lflorez@gwdg.de'

import math
import os

from PIL import Image
import ImageFilter

def _calculate_new_size(size):
    """
    Return the next size of a square canvas that has edges of size 256 x 2^n.

    """
    # Get the size of its longest edge in pixels
    longestEdge = max(size)

    # If the image has only one pixel, return the frame size (256, 256)
    if longestEdge == 1:
        return (256, 256)

    # Calculate the zoom levels needed to fit the image and the size of
    # this zoom level.
    maxZoomLevel = math.ceil(math.log(longestEdge/256.0, 2))
    newSize = (int(256*math.pow(2, maxZoomLevel)),
               int(256*math.pow(2, maxZoomLevel)))

    return newSize

def _calculate_offset(size):
    """
    Return the offset of the image after being framed to the next zoom level.
    The offset is given as a duple of int.

    """
    # Get the new image size
    newSize = _calculate_new_size(size)
        
    # Calculate the offset needed to center the small image in the new frame
    xOffset = int((newSize[0] - size[0]) / 2)
    yOffset = int((newSize[1] - size[1]) / 2)
    
    return (xOffset, yOffset)

def _frame_image(imageObject):
    """
    Frame the image to the right proportion and center it.

    Since every zoom level in a Google map consists of a square array of
    tiles of size 256 x 256 px, the image must be framed to fit the next
    multiple of this size. For example, an image with size 800 x 400 has
    to be framed to a size of 1024 x 1024 (to accomodate to zoom level 2)
    since the next lowest zoom level only allows 512 x 512 px.

    Input:

    An Image object
    
    Output:

    An Image object with the input image centered and framed in white to
    the next largest multiple of 256 x 256 px.

    Usage example:

    >>> tiles._frame_image(image)
        
    """

    # Open the image and determine its size
    im = imageObject
    size = im.size
  
    # Check if the size is already ok
    sizeOk = True  # Assume first that it is ok
    for coord in size:
        # Divide by 256 and take the logarithm on base 2. The resulting number
        # should be an integer if the image has the right size
        factor = math.log(coord/256.0, 2)
        # if the factor is not an integer...
        if factor != math.floor(factor):  
            sizeOk = False
        
    # Return the image as it is if the size is Ok
    if sizeOk:
        return im

    # Get the offset and the new size
    offset = _calculate_offset(size)
    newSize = _calculate_new_size(size)
        
    # Create an empty white image that will span the maximum zoom level
    newImage = Image.new("RGB", newSize, "white")
        
    # Define the region where the small image will be inserted in the new one
    region = (int(offset[0]),
              offset[1],
              int(offset[0]) + size[0],
              int(offset[1]) + size[1]
              )
    
    # Paste the image into that region and return it
    newImage.paste(im, region)
    return newImage

def _create_zoom_levels(framedImage):
    """
    Create several resized versions of the main image, one for each zoom level.

    Input:

    An Image (object) with size (2^n x 256) x (2^n x 256)

    Output:

    A list with (n+1) Image objects, ordered from small to big. The first Image
    is a resized version of the original Image scaled to 256 x 256 px. Each
    subsequent Image doubles the size (e.g. the next one is 512 x 512 px) until
    the size of the original Image is reached.

    Usage example:

    >>> tiles._frame_image(image)

    """

    # Initialize the list that will be sent as output
    output = list()

    # Determine the maximum zoom level that needs to be created
    maxSize = framedImage.size
    maxZoomLevel = int(math.log(maxSize[0]/256, 2))

    # Append the scaled versions of the image, corresponding to
    # the lower zoom levels.
    for i in range(0, maxZoomLevel):
        newSize = (256 * pow(2, i),
                   256 * pow(2, i))
        scaledImage = framedImage.resize(newSize, Image.ANTIALIAS)
        output.append(scaledImage)

    # Append the unscaled image in the end
    output.append(framedImage)
    return output

def _cut_tiles(zoomLevelImages):
    """
    Cut the images of every zoom level into several tiles of size 256 x 256.

    Input:

    A list of "n" Image objects, each of them representing a zoom level of the
    custop map.

    Output:

    A nested list with three levels with the following structure:

    Level 1: zoom level {Z}
    Level 2: {Y} coordinate
    Level 3: {X} coordinate

    In words, it is a list of zoom levels. Each zoom level is itself a list,
    whose elements are rows of the image. Each row of the image is itself
    a list, whose elements are the individual tile Images.

    This allows to go through all the images like this:

    for z in output:
        for y in z:
            for x in y:
                do_something_with_tile(x,y,z)
    
    Usage example:

    >>> tiles._cut_tiles(listOfImageObjects)
    
    """

    # Initialize the output
    output = list()
    
    for z, im in enumerate(zoomLevelImages): # for every zoom level...
        zoomLevelList = list()
        # Determine the number of rows are needed at this zoom level
        numRows = int(pow(2,z))
        for y in range(0, numRows):  # for every row...
            rowLevelList = list()       
            for x in range(0, numRows):    # for every column
                # Set the area that corresponds to the coordinates x and y
                box = (256 * x, 256 * y,
                       256 * (x + 1), 256 * (y + 1))
                # Create the tile that corresponds to this coordinates
                rowLevelList.append(im.crop(box))
            zoomLevelList.append(rowLevelList)
        output.append(zoomLevelList)
        
    return output    

def generate_tiles(pathToImage, pathToTargetFolder):
    """
    Run the module functions in order and save the images in the target folder.

    Input:

    A path to the image (in PNG format) for which tiles have to be created and
    a path to the folder where all the images will be saved.

    Output:

    Several images in the target folder, following the convention
    {Z}_{X}_{Y}.png, where {Z} is the zoom level, and {X}, {Y} the respective
    x and y tile coordinates at that zoom level.

    In addition the function returns a duple with the following format:
    ((x-offset, y-offset), zoom-levels)
    x-offset, y-offset: the offset needed (as integer) to frame the image
    zoom-levels: the number of zoom levels needed, starting from zero

    Usage example:

    >>> (offset, zoomLevels) = generate_tiles("path_to_image",
                                              "path_to_target_folder")

    """

    # Open the image
    im = Image.open(pathToImage)
    # First call, frame the image to the right proportions
    framedIm = _frame_image(im)
    # Second call, resize the image into several zoom levels
    images = _create_zoom_levels(framedIm)
    # Third call, cut each zoom level into individual tiles
    result = _cut_tiles(images)
        
    # Save all the tiles with the correct name
    for z, zPic in enumerate(result):
        for y, yPic in enumerate(zPic):
            for x, xPic in enumerate(yPic):
                tileName = ''.join([str(z),'_',str(x),'_',str(y),'.png'])
                xPic.save(os.path.join(pathToTargetFolder,tileName))

    offset = _calculate_offset(im.size)
    maxZoom = len(result)-1
    return (offset, maxZoom)
