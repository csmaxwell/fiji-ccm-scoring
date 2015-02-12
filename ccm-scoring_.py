"""
CCM Scoring Plugin
Author: Colin S. Maxwell

This plugin takes a grid of coordinates that mark out sub-images on
a larger image (e.g. wells of a 96-well plate) and crops the larger
image on those coordinates then displays the sub-images and records
a subjective score for each image. See README.org for usage.

"""


###########################################################################
#####                       Begin HTML.py                             #####
###########################################################################
##### This is included to allow for easy creation of an HTML report   #####
##### of the thumbnails                                               #####
###########################################################################

#--- LICENSE ------------------------------------------------------------------

# Copyright Philippe Lagadec - see http://www.decalage.info/contact for contact info
#
# This module provides a few classes to easily generate HTML tables and lists.
#
# This software is governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software.  You can  use,
# modify and/or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".
#
# A copy of the CeCILL license is also provided in these attached files:
# Licence_CeCILL_V2-en.html and Licence_CeCILL_V2-fr.html
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.
#
# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and,  more generally, to use and operate it in the
# same conditions as regards security.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

#--- CONSTANTS -----------------------------------------------------------------

# Table style to get thin black lines in Mozilla/Firefox instead of 3D borders
TABLE_STYLE_THINBORDER = "border: 1px solid #000000; border-collapse: collapse;"
#TABLE_STYLE_THINBORDER = "border: 1px solid #000000;"


#=== CLASSES ===================================================================

class TableCell (object):
    """
    a TableCell object is used to create a cell in a HTML table. (TD or TH)

    Attributes:
    - text: text in the cell (may contain HTML tags). May be any object which
            can be converted to a string using str().
    - header: bool, false for a normal data cell (TD), true for a header cell (TH)
    - bgcolor: str, background color
    - width: str, width
    - align: str, horizontal alignement (left, center, right, justify or char)
    - char: str, alignment character, decimal point if not specified
    - charoff: str, see HTML specs
    - valign: str, vertical alignment (top|middle|bottom|baseline)
    - style: str, CSS style
    - attribs: dict, additional attributes for the TD/TH tag

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.6
    """

    def __init__(self, text="", bgcolor=None, header=False, width=None,
                align=None, char=None, charoff=None, valign=None, style=None,
                attribs=None):
        """TableCell constructor"""
        self.text    = text
        self.bgcolor = bgcolor
        self.header  = header
        self.width   = width
        self.align   = align
        self.char    = char
        self.charoff = charoff
        self.valign  = valign
        self.style   = style
        self.attribs = attribs
        if attribs==None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table cell as a string"""
        attribs_str = ""
        if self.bgcolor: self.attribs['bgcolor'] = self.bgcolor
        if self.width:   self.attribs['width']   = self.width
        if self.align:   self.attribs['align']   = self.align
        if self.char:    self.attribs['char']    = self.char
        if self.charoff: self.attribs['charoff'] = self.charoff
        if self.valign:  self.attribs['valign']  = self.valign
        if self.style:   self.attribs['style']   = self.style
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.text:
            text = str(self.text)
        else:
            # An empty cell should at least contain a non-breaking space
            text = '&nbsp;'
        if self.header:
            return '  <TH%s>%s</TH>\n' % (attribs_str, text)
        else:
            return '  <TD%s>%s</TD>\n' % (attribs_str, text)

#-------------------------------------------------------------------------------

class TableRow (object):
    """
    a TableRow object is used to create a row in a HTML table. (TR tag)

    Attributes:
    - cells: list, tuple or any iterable, containing one string or TableCell
             object for each cell
    - header: bool, true for a header row (TH), false for a normal data row (TD)
    - bgcolor: str, background color
    - col_align, col_valign, col_char, col_charoff, col_styles: see Table class
    - attribs: dict, additional attributes for the TR tag

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.5
    """

    def __init__(self, cells=None, bgcolor=None, header=False, attribs=None,
                col_align=None, col_valign=None, col_char=None,
                col_charoff=None, col_styles=None):
        """TableCell constructor"""
        self.bgcolor     = bgcolor
        self.cells       = cells
        self.header      = header
        self.col_align   = col_align
        self.col_valign  = col_valign
        self.col_char    = col_char
        self.col_charoff = col_charoff
        self.col_styles  = col_styles
        self.attribs     = attribs
        if attribs==None:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the table row as a string"""
        attribs_str = ""
        if self.bgcolor: self.attribs['bgcolor'] = self.bgcolor
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = ' <TR%s>\n' % attribs_str
        for cell in self.cells:
            col = self.cells.index(cell)    # cell column index
            if not isinstance(cell, TableCell):
                cell = TableCell(cell, header=self.header)
            # apply column alignment if specified:
            if self.col_align and cell.align==None:
                cell.align = self.col_align[col]
            if self.col_char and cell.char==None:
                cell.char = self.col_char[col]
            if self.col_charoff and cell.charoff==None:
                cell.charoff = self.col_charoff[col]
            if self.col_valign and cell.valign==None:
                cell.valign = self.col_valign[col]
            # apply column style if specified:
            if self.col_styles and cell.style==None:
                cell.style = self.col_styles[col]
            result += str(cell)
        result += ' </TR>\n'
        return result

#-------------------------------------------------------------------------------

class Table (object):
    """
    a Table object is used to create a HTML table. (TABLE tag)

    Attributes:
    - rows: list, tuple or any iterable, containing one iterable or TableRow
            object for each row
    - header_row: list, tuple or any iterable, containing the header row (optional)
    - border: str or int, border width
    - style: str, table style in CSS syntax (thin black borders by default)
    - width: str, width of the table on the page
    - attribs: dict, additional attributes for the TABLE tag
    - col_width: list or tuple defining width for each column
    - col_align: list or tuple defining horizontal alignment for each column
    - col_char: list or tuple defining alignment character for each column
    - col_charoff: list or tuple defining charoff attribute for each column
    - col_valign: list or tuple defining vertical alignment for each column
    - col_styles: list or tuple of HTML styles for each column

    Reference: http://www.w3.org/TR/html4/struct/tables.html#h-11.2.1
    """

    def __init__(self, rows=None, border='1', style=None, width=None,
                cellspacing=None, cellpadding=4, attribs=None, header_row=None,
                col_width=None, col_align=None, col_valign=None,
                col_char=None, col_charoff=None, col_styles=None):
        """TableCell constructor"""
        self.border = border
        self.style = style
        # style for thin borders by default
        if style == None: self.style = TABLE_STYLE_THINBORDER
        self.width       = width
        self.cellspacing = cellspacing
        self.cellpadding = cellpadding
        self.header_row  = header_row
        self.rows        = rows
        if not rows: self.rows = []
        self.attribs     = attribs
        if not attribs: self.attribs = {}
        self.col_width   = col_width
        self.col_align   = col_align
        self.col_char    = col_char
        self.col_charoff = col_charoff
        self.col_valign  = col_valign
        self.col_styles  = col_styles

    def __str__(self):
        """return the HTML code for the table as a string"""
        attribs_str = ""
        if self.border: self.attribs['border'] = self.border
        if self.style:  self.attribs['style'] = self.style
        if self.width:  self.attribs['width'] = self.width
        if self.cellspacing:  self.attribs['cellspacing'] = self.cellspacing
        if self.cellpadding:  self.attribs['cellpadding'] = self.cellpadding
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        result = '<TABLE%s>\n' % attribs_str
        # insert column tags and attributes if specified:
        if self.col_width:
            for width in self.col_width:
                result += '  <COL width="%s">\n' % width
        if self.header_row:
            if not isinstance(self.header_row, TableRow):
                result += str(TableRow(self.header_row, header=True))
            else:
                result += str(self.header_row)
        # Then all data rows:
        for row in self.rows:
            if not isinstance(row, TableRow):
                row = TableRow(row)
            # apply column alignments  and styles to each row if specified:
            # (Mozilla bug workaround)
            if self.col_align and not row.col_align:
                row.col_align = self.col_align
            if self.col_char and not row.col_char:
                row.col_char = self.col_char
            if self.col_charoff and not row.col_charoff:
                row.col_charoff = self.col_charoff
            if self.col_valign and not row.col_valign:
                row.col_valign = self.col_valign
            if self.col_styles and not row.col_styles:
                row.col_styles = self.col_styles
            result += str(row)
        result += '</TABLE>'
        return result


#-------------------------------------------------------------------------------

class List (object):
    """
    a List object is used to create an ordered or unordered list in HTML.
    (UL/OL tag)

    Attributes:
    - lines: list, tuple or any iterable, containing one string for each line
    - ordered: bool, choice between an ordered (OL) or unordered list (UL)
    - attribs: dict, additional attributes for the OL/UL tag

    Reference: http://www.w3.org/TR/html4/struct/lists.html
    """

    def __init__(self, lines=None, ordered=False, start=None, attribs=None):
        """List constructor"""
        if lines:
            self.lines = lines
        else:
            self.lines = []
        self.ordered = ordered
        self.start = start
        if attribs:
            self.attribs = attribs
        else:
            self.attribs = {}

    def __str__(self):
        """return the HTML code for the list as a string"""
        attribs_str = ""
        if self.start:  self.attribs['start'] = self.start
        for attr in self.attribs:
            attribs_str += ' %s="%s"' % (attr, self.attribs[attr])
        if self.ordered: tag = 'OL'
        else:            tag = 'UL'
        result = '<%s%s>\n' % (tag, attribs_str)
        for line in self.lines:
            result += ' <LI>%s\n' % str(line)
        result += '</%s>\n' % tag
        return result


#=== FUNCTIONS ================================================================

# much simpler definition of a link as a function:
def Link(text, url):
    return '<a href="%s">%s</a>' % (url, text)

def link(text, url):
    return '<a href="%s">%s</a>' % (url, text)

def table(*args, **kwargs):
    'return HTML code for a table as a string. See Table class for parameters.'
    return str(Table(*args, **kwargs))

def list(*args, **kwargs):
    'return HTML code for a list as a string. See List class for parameters.'
    return str(List(*args, **kwargs))

###########################################################################
#####                       End HTML.py                               #####
###########################################################################




import csv, os, sys
import ij.IJ
import ij.gui
import ij.io
from ij.io import FileSaver
from ij import IJ, ImagePlus, WindowManager
from ij.gui import Roi, Overlay, GenericDialog
from java.awt.event import KeyEvent, KeyAdapter, ActionListener, WindowAdapter
from javax.swing import JScrollPane, JPanel, JComboBox, JLabel, JFrame, JButton, JFormattedTextField, JTextField, JFileChooser
from java.awt import Color, GridLayout
from random import shuffle, choice
from java.io import File


###########################################################################
#####                       Begin Grid Reader                         #####
###########################################################################


class GridReader:
    """
    Displays cropped images of a plat based on a grid generated by the
    Microarray Profile plugin:

    http://www.optinav.com/MicroArray_Profile.htm

    Attributes:
    - fp : string, a path to the grid to be read. If not specified,
           imageJ will prompt you for a path. NOTE: the filename must be
           in the form of "sourceImageName_gridName" and should be in the form
           generated by the Microarray Profile plugin. No more underscores
           are allowed in the name besides the one separating the names.
    """
    
    def __init__(self, fp = None):
        # Initialize the filepath to the grid file
        if fp is None:
            self.fp = IJ.getFilePath("Grid file")
        else:
            self.fp = fp
        # Get the directory, the name of the grid, and the name of the image
        self.initializeFilenames()
        self.loadSourceImage()
        self.initializeGridCoords()
    
    def initializeFilenames(self):
        # Save the directory to the grid file
        self.directory, gridfile = os.path.split( self.fp )
        # Get the name of the grid file without the extension
        # This is the "plateID" which is the concatenation of the image
        # and the grid IDs
        self.plateID, ext = os.path.splitext( gridfile )
        # This expect that the grid file will be named according to
        # imageID_plateID  This allows for multiple grids per plate
        fnSplit = self.plateID.split("_")
        if len(fnSplit) != 2:
            raise ValueError("File name is not formatted properly")
        # Save the imageID for later
        self.imageID, tmp = fnSplit       
    
    def close(self):
        """
        This method is called by the Closing listener below
        when the GUI frame is closed
        """
        self.sourceImage.close()
        
    def initializeGridCoords(self):
        """
        Initializes a list of coordinates that are used by
        the open method. self.n indexes these coordinates
        """
        # Read the first line of the file
        inGrid = open(self.fp,"r")
        reader = csv.reader(inGrid , delimiter="\t" )
        firstLine = reader.next()
        try:
            self.rows, self.columns, self.width = tuple(firstLine)
            self.rows = int(self.rows)
            self.columns = int(self.columns)
            self.width = int(self.width)
        except ValueError:
            raise ValueError("There are the wrong number of fields on the first line")
        self.gridCoords = []
        row = 1
        col = 1
        for x,y in reader:
            if col > self.columns:
                col = 1
                row = row + 1
            self.gridCoords.append( (self.plateID, row, col, x, y) )
            col = col + 1
        inGrid.close()
        
    def loadSourceImage( self ):
        """
        Loads the image that the grid was set up on
        """
        imgPath = os.path.join(self.directory, self.imageID + ".tif")
        img = ImagePlus(imgPath)
        if img is None:
            raise ValueError("Couldn't find the image")
        self.sourceImage = img
    
    def openSubImage( self, x, y, auto=False ):
        """
        This method is called by both openPrevious and openNext to
        display an image that is cropped from the sourceImage based
        on the grid coordinates

        Arguments:
        - auto : bool, if True the image is autoscaled
        """
        # Set the ROI on the source image
        #roi = Roi(int(self.x), int(self.y), int(self.width), int(self.width))
        roi = Roi( int(x), int(y), int(self.width), int(self.width) )
        self.sourceImage.setRoi(roi)
        # Get a processor corresponding to a cropped version of the image
        processor = self.sourceImage.getProcessor().crop()
        self.sourceImage.killRoi()
        # Make a new image of image and run contrast on it
        openImage = ImagePlus(" ", processor)
        return openImage

    def getCoords(self):
        return self.gridCoords

    def getPlateID(self):
        return self.plateID
    

            

class GridSet:
    """
    A class to keep track of multiple grid readers.
    
    cContains methods to keep track of scores and move forward and
    backward while keeping track of the scores.

    Writes a csv file containing the information about the grid as well
    as the score that was assigned to each cell in the grid.

    Writes a jpg thumbnail for each cropped cell in the grid.

    Writes an HTML report that matches scores to images.

    Images are displayed randomly to prevent biased scoring.

    Arguments:

    - fp : list, paths the the grid files used by the GridReader
    - scoreFile : string, an string giving the filename of the
      scores to write to.
    - thumbDir : string, the name of the directory to save the
      thumbnails in
    """
    def __init__(self, fp, scoreFile, thumbDir):
        # These will be indexed by the grid coordinates
        self.scores = {}
        # These will be indexed by the plateID
        self.grids = {}
        # Keeps the grid coordinates from each grid
        self.gridCoords = []
        for i in fp:
            grid = GridReader(i)
            # each coordinate is a tuple: (plateID, row, col, x, y)
            gridCoords = grid.getCoords()
            # save the grid reader in a dictionary
            self.grids[ grid.getPlateID() ] = grid
            # append the coordinates to the coordinates pile
            for coord in gridCoords:
                self.gridCoords.append(coord)
        # shuffle the coordinates
        shuffle(self.gridCoords)
        # Initialize the images, and some variable names
        self.openImage = ImagePlus()
        self.thumbDir = thumbDir
        self.scoreFile = scoreFile
        self.reportFile = os.path.splitext(scoreFile)[0] + ".html"
        self.reportFile2 = os.path.splitext(scoreFile)[0] + "-with-plate-positions.html"
        self.min = 0
        self.max = 255
        # This is the current coordinate position
        self.n = -1
        # Test for scorefiles
        if os.path.isfile( self.scoreFile ):
            print "Restoring previous scores"
            self.restoreScores()
        # Generate a spot for the HTML report to live in along with the thumbnails
        try:
            os.mkdir(self.thumbDir)
        except OSError:
            pass

    def restoreScores(self):
        """
        If a file with the same name is detected as the output score file,
        this method is called. It reads in the previous scores and
        sets the first image to be the image after the previous scores
        """
        # Open a file to the scores
        inFile = open( self.scoreFile , "r" )
        reader = csv.reader(inFile, delimiter=",")
        header = reader.next()
        # This will store the coordinates corresponding to the previous scores
        tmpCoords = []
        # for each row in the scores file, append the previous coordinates
        # and make an entry for the score
        for row in reader:
            plateID, row, col, x, y, theMin, theMax, score = row
            coord = (plateID, row, col, x, y)
            self.scores[ coord ] = (plateID, row, col, x, y, theMin, theMax, score)
            tmpCoords.append(coord)
        self.min = int(theMin)
        self.max = int(theMax)
        self.n = len(tmpCoords) - 1
        if self.n < 0:
            self.n = 0
        for coord in self.gridCoords:
            if coord not in self.scores:
                tmpCoords.append(coord)
        self.gridCoords = tmpCoords
        
    def writeThumbnail(self):
        plateID, row, col, x, y = self.currentCoordinate
        imName = "_".join([ str(plateID), str(row), str(col) ] ) + ".jpg"
        imName = os.path.join(self.thumbDir, imName)
        fs = FileSaver(self.openImage)
        fs.saveAsJpeg( imName )

    def setMinAndMax(self, minVal = None, maxVal = None):
        """
        Sets the min and max of the current image

        Arguments:
        - minVal : integer, the minimum value for the pixel display
        - maxVal : integer, the maximum value for the pixel display
        """
        if minVal is not None:
            self.min = minVal
        if maxVal is not None:
            self.max = maxVal
        self.openImage.getProcessor().setMinAndMax(self.min, self.max)
        self.openImage.updateChannelAndDraw()
        self.writeThumbnail()
            
    def openNext(self):
        """
        Opens the next image.

        Arguments:
        - thumbNails : bool, if True a thumbnail for th
          image is written when the image is opened
        """
        self.openImage.close()
        # Set the current number being examined
        self.n = self.n + 1
        try:
            self.currentCoordinate = self.gridCoords[ self.n ]
        except IndexError:
            gd = GenericDialog("")
            gd.addMessage("No more images")
            gd.showDialog()
            return None
        plateID, row, col, x, y = self.currentCoordinate
        # open the file
        grid = self.grids[ plateID ]
        self.openImage = grid.openSubImage(x,y)
        self.setMinAndMax()
        self.openImage.show()
        # Write the thumbnail
        self.writeThumbnail()
        # Try to return the information about the current score
        # if it doesn't exist, return an empty string. This
        # is used to display the score associated with the image
        try:
            return self.scores[ self.currentCoordinate ][7]
        except KeyError:
            return ""

    def openPrevious(self):
        """
        Opens the previous image.
        """
        self.n = self.n - 1
        if self.n < 0:
            self.n = 0
        else:
            self.openImage.close()
            self.currentCoordinate = self.gridCoords[ self.n ]
            plateID, row, col, x, y = self.currentCoordinate
            # open the file
            grid = self.grids[ plateID ]
            self.openImage = grid.openSubImage(x,y)
            self.setMinAndMax()
            self.openImage.show()
        # Retun the score of the image so it can be displayed
        try:
            return self.scores[ self.currentCoordinate ][7]
        except KeyError:
            return ""

    def writeScore(self, score):
        """
        Update the dictionary of scores with the new score and
        write the full dictionary to disk.

        Attributes:
        - score : string, the score to be associated with the grid
                  coordinates and the row/column info
        """
        header = ["plate", "row", "col", "x", "y", "min", "max", "score"]
        plateID, row, col, x, y = self.currentCoordinate
        # Save the info for the score in a dictionary
        info = (plateID,
                row,
                col,
                x,
                y,
                self.min,
                self.max,
                score)
        self.scores[ self.currentCoordinate ] = info
        # initialize a writer for the scores and write a header
        self.out = open( self.scoreFile , "w" )
        writer = csv.writer(self.out, delimiter=",")
        writer.writerow(header)
        for i in self.scores.values():
            writer.writerow( i )
        self.out.close() 

    def writeReport(self, reportName, thumbDir, numColumns = 5, textSize = 20, doInfo=False):
        """
        Writes an HTML report with alternating rows of
        images and their scores.

        Arguments:
        - numColumns : integer, the number of columns in the html report
        - textSize : integer, the text size for the scores
        """
        def img(location, width, height):
            return '<img src="%s" width="%i" height="%i">' % (location, width, height)
        # Initialize the HTML writer
        t = Table(col_align = ["center" for i in range(0,numColumns)])
        #t.rows.append(TableRow(["row", "col", "score", "image"], header=True))
        # For each score, sort by the colony morphology score
        scores = [i for i in self.scores.values()]
        sortedScores = [i for i in sorted( scores, key=lambda info: info[7])]
        ##### This next chunk makes a 5xn table in the HTML file with
        ##### alternating images and their scores.
        n = 0
        imgLine = []
        scoreLine = []
        for i in range(0, len(sortedScores)):
            plateID, row, col, x, y, theMin, theMax, score = sortedScores[i]
            # Font size is set above
            score = "<font size = '%i'>%s</font>" % (textSize, str(score))
            imgInfo = "%s: row %s, col %s" % (plateID, str(row), str(col))
            if doInfo:
                score = score + "<br>" + imgInfo
            # This should be a function
            imName = "_".join([ str(plateID), str(row), str(col) ] ) + ".jpg"
            # Images live in a subfolder. This splits the path so that
            # only the relative name is referenced
            thumbDir = os.path.split(thumbDir)[1]
            imName = os.path.join(thumbDir, imName)
            scoreLine.append( score )
            imgLine.append( img(imName, 300, 300) )
            n += 1
            if (( n % numColumns) == 0):
                t.rows.append( TableRow( imgLine ) )
                t.rows.append( TableRow( scoreLine) )
                n = 0
                imgLine = []
                scoreLine = []
        # Append the final row to the table
        t.rows.append( TableRow( imgLine ) )
        t.rows.append( TableRow( scoreLine) )
        # Initialize the connection for the report
        reportOut = open( reportName, "w")
        # write the html
        reportOut.write( str(t) )
        reportOut.close()

    def close(self):
        self.openImage.close()
        self.writeReport(self.reportFile, self.thumbDir)
        self.writeReport(self.reportFile2, self.thumbDir, doInfo=True)
        for grid in self.grids.values():
            grid.close()




###########################################################################
#####                       Begin GUI classes                         #####
###########################################################################

# Each of the following classes are used in the GUI frame
# Note that they inherit java swing classes
# Each class implements a method that is called by the
# swing class. When the action operates on another
# field, the field is passed in the intialization of the class

class ChangedMin(ActionListener):
    """ A listener that will update the current image with
    a new min when it's field is changed"""
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrids
        newValue = int(self.field.getText())
        plateGrid.setMinAndMax(minVal = newValue)

class ChangedMax(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        newValue = int(self.field.getText())
        plateGrid.setMinAndMax(maxVal = newValue)

class NextImage(ActionListener):
    def __init__(self, field):
        self.scoreField = field
    def actionPerformed(self, event):
        global plateGrid
        global frame
        score = plateGrid.openNext()
        if score is not None:
            self.scoreField.setText(score)
            frame.setVisible(True)

class PreviousImage(ActionListener):
    def __init__(self, field):
        self.scoreField = field
    def actionPerformed(self, event):
        global plateGrid
        global frame
        score = plateGrid.openPrevious()
        self.scoreField.setText(score)
        frame.setVisible(True)

class WriteScore(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global frame
        global plateGrid
        plateGrid.writeScore( self.field.getText() )

class Closing(WindowAdapter):
    def windowClosing(self,e):
        global plateGrid
        plateGrid.close()


###########################################################################
#####                       End GUI classes                           #####
###########################################################################




###########################################################################
#####                       Main code                                 #####
###########################################################################

# Set up the fields for the SWING interface
minField = JFormattedTextField( 0 )
minField.addActionListener( ChangedMin(minField) )

maxField = JFormattedTextField( 255 )
maxField.addActionListener( ChangedMax(maxField) )

scoreField = JTextField( "" )
scoreField.addActionListener( NextImage(scoreField) )
scoreField.addActionListener( WriteScore(scoreField) )

button = JButton("Previous image")
button.addActionListener( PreviousImage(scoreField) )

    # Pack all the fields into a JPanel
all = JPanel()
layout = GridLayout(4, 1)
all.setLayout(layout)
all.add( JLabel("  ") )
all.add( button )
all.add( JLabel("Min") )
all.add( minField )
all.add( JLabel("Max") )
all.add(maxField )
all.add( JLabel("Score :") )
all.add(scoreField)
frame = JFrame("CCM scoring")
frame.getContentPane().add(JScrollPane(all))
frame.pack()
frame.addWindowListener( Closing() )
scoreField.requestFocusInWindow()

# Get the grid files
chooser = JFileChooser()
chooser.setDialogTitle("Choose plate grids")
chooser.setMultiSelectionEnabled(True)
chooser.setCurrentDirectory( File(os.path.expanduser("~")))
chooser.showOpenDialog(JPanel())

# This is a hack to get a file path from the
# sun.awt.shell.DefaultShellFolder object returned by the chooser
fp = [str(i) for i in chooser.getSelectedFiles()]

if len(fp) != 0:
    gd = GenericDialog("Name your output file")
    gd.addStringField("Score file name", "scores.csv")
    gd.showDialog()
    if not gd.wasCanceled():
        scoreFile = gd.getNextString()
        scoreFile = os.path.join( os.path.split(fp[0])[0], scoreFile)
        cropDir = os.path.splitext( scoreFile)[0] + "_cropped"
        # Initialize the grid readers
        plateGrid = GridSet(fp,scoreFile,cropDir)
        plateGrid.openNext()
        # Show the GUI
        frame.setVisible(True)
    else:
        pass
else:
    pass





