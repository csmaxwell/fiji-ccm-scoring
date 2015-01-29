import csv, os
import ij.IJ
import ij.gui
from ij import IJ, ImagePlus, WindowManager
from ij.gui import Roi, Overlay, GenericDialog
from java.awt.event import KeyEvent, KeyAdapter, ActionListener, WindowAdapter
from javax.swing import JScrollPane, JPanel, JComboBox, JLabel, JFrame, JButton, JFormattedTextField, JTextField
from java.awt import Color, GridLayout
from random import shuffle


class GridReader:    
    def __init__(self, fp = None, shuffleGrid=True):
        # Initialize the filepath to the grid file
        if fp is None:
            self.fp = IJ.getFilePath("Grid file")
        else:
            self.fp = fp
        # Get the directory, the name of the grid, and the name of the image
        self.initializeFilenames()
        # Read the first line of the file
        self.inGrid = open(self.fp,"r")
        self.reader = csv.reader(self.inGrid , delimiter="\t" )
        firstLine = self.reader.next()
        try:
            self.rows, self.columns, self.width = tuple(firstLine)
            self.rows = int(self.rows)
            self.columns = int(self.columns)
            self.width = int(self.width)
        except ValueError:
            raise ValueError("There are the wrong number of fields on the first line")
        self.loadSourceImage()
        self.openImage = ImagePlus()
        self.initializeGridCoords()
        if shuffle:
            shuffle(self.gridCoords)
        self.n = -1
        self.maxN = -1
        self.scores = {}
        self.openNext(auto=True)
    
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

    def writeScore(self, score):
        """ This will write the score of the current image to disk.
        Note that the scores file is re-written each time to avoid
        losing data in case of a crash."""
        # When you move back, you start examining old files
        # This keeps track of how far you've gone.
        header = ["row", "col", "x", "y", "min", "max", "score"]
        if self.n > self.maxN:
            self.maxN = self.n
        # Save the info for the score in a dictionary
        info = [self.row, self.col, self.x, self.y, self.min, self.max, score]
        self.scores[ self.n ] = info
        # initialize a writer for the scores and write a header
        self.out = open( os.path.join(self.directory, self.plateID + "_scores.csv"), "w" )
        writer = csv.writer(self.out, delimiter=",")
        writer.writerow(header)
        # iterate through all the scores and write them to the disk
        for i in range(0, self.maxN+1):
            writer.writerow( self.scores[ i ] )
        self.out.close()
    
    def close(self):
        """ This method is called by the Closing listener below
        when the GUI frame is closed """
        self.sourceImage.close()
        self.openImage.close()
        
    def initializeGridCoords(self):
        """ Initializes a list of coordinates that are used by
        the open method. self.n indexes these coordinates """
        self.gridCoords = []
        row = 1
        col = 1
        for x,y in self.reader:
            if col > self.columns:
                col = 1
                row = row + 1
            self.gridCoords.append( (row, col, x, y) )
            col = col + 1
        self.inGrid.close()
        
    def loadSourceImage( self ):
        """ Loads the image that the grid was set up on """
        imgPath = os.path.join(self.directory, self.imageID + ".tif")
        img = ImagePlus(imgPath)
        if img is None:
            raise ValueError("Couldn't find the image")
        self.sourceImage = img

    def openNext(self, auto=False):
        """ Increments the current n """
        # Set the current number being examined
        if self.n +1 > self.rows*self.columns:
            gd = GenericDialog("")
            gd.addMessage("No more images")
            gd.showDialog()
            return None
        self.n = self.n + 1
        self.row, self.col, self.x, self.y = self.gridCoords[ self.n ]
        self.open(auto=auto)
        # Try to return the information about the current score
        # if it doesn't exist, return an empty string
        try:
            return self.scores[ self.n ][6]
        except KeyError:
            return ""

    def openPrevious(self, auto=False):
        self.n = self.n - 1
        if self.n < 0:
            self.n = 0
        else:
            self.row, self.col, self.x, self.y = self.gridCoords[ self.n ]
            self.open(auto=auto)
        return self.scores[ self.n ][6]
    
    def open( self, auto=False ):
        self.openImage.close()        
        # Set the ROI on the source image
        roi = Roi(int(self.x), int(self.y), int(self.width), int(self.width))
        self.sourceImage.setRoi(roi)
        # Get a processor corresponding to a cropped version of the image
        processor = self.sourceImage.getProcessor().crop()
        self.sourceImage.killRoi()
        # Make a new image of image and run contrast on it
        self.openImage = ImagePlus(" ", processor)
        self.setContrast(auto)
        self.openImage.show()
        return self.openImage
    
    def setMinAndMax(self, minVal, maxVal):
        self.min, self.max = minVal, maxVal
        self.openImage.getProcessor().setMinAndMax(self.min, self.max)
        self.openImage.updateAndDraw()

    def getMin(self):
        return self.min

    def getMax(self):
        return self.max
    
    def setContrast(self, auto=False):
        if auto:
            IJ.run(self.openImage, "Enhance Contrast", "saturated=0.35")
            self.min = self.openImage.getProcessor().getMin()
            self.max = self.openImage.getProcessor().getMax()
        else:
            self.openImage.getProcessor().setMinAndMax(self.min, self.max)
            self.openImage.updateAndDraw()
            
################### GUI classes
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
        global plateGrid
        newValue = int(self.field.getText())
        currentMax = plateGrid.getMax()
        plateGrid.setMinAndMax(newValue, currentMax)

class ChangedMax(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        newValue = int(self.field.getText())
        print newValue
        currentMin = plateGrid.getMin()
        plateGrid.setMinAndMax(currentMin, newValue)

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
        print score
        self.scoreField.setText(score)
        frame.setVisible(True)

class WriteScore(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        global frame
        plateGrid.writeScore( self.field.getText() )

class Closing(WindowAdapter):
    def windowClosing(self,e):
        #WindowManager.closeAllWindows()
        global plateGrid
        plateGrid.close()
        pass


###### 
    
plateGrid = GridReader()

minField = JFormattedTextField( plateGrid.getMin() )
minField.addActionListener( ChangedMin(minField) )

maxField = JFormattedTextField( plateGrid.getMax() )
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
frame.setVisible(True)

