import csv, os
import ij.IJ
import ij.gui
from ij import IJ, ImagePlus, WindowManager
from ij.gui import Roi, Overlay, GenericDialog
from java.awt.event import KeyEvent, KeyAdapter, ActionListener, WindowAdapter
from javax.swing import JScrollPane, JPanel, JComboBox, JLabel, JFrame, JButton, JFormattedTextField, JTextField
from java.awt import Color, GridLayout
from random import shuffle


# Keycode 78 is "n"

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
        self.initializeWriter()
        self.initializeGridCoords()
        if shuffle:
            shuffle(self.gridCoords)
        self.n = -1
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

    def initializeWriter(self):
        self.out = open( os.path.join(self.directory, self.plateID + "_scores.csv"), "w" )
        self.writer = csv.writer(self.out, delimiter=",")
        self.writer.writerow(["row", "col", "x", "y", "min", "max", "score"])
        self.out.close()

    def writeScore(self, score):
        self.out = open( os.path.join(self.directory, self.plateID + "_scores.csv"), "a" )
        self.writer = csv.writer(self.out, delimiter=",")
        self.writer.writerow( [self.row, self.col, self.x,
                               self.y, self.min, self.max, score])
        self.out.close()
    
    def close(self):
        self.sourceImage.close()
        self.openImage.close()
        self.out.close()
        
    def initializeGridCoords(self):
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
        # This was here for testing
        # f =  open( os.path.join(self.directory, self.plateID + ".csv"), "w")
        # writer = csv.writer(f, delimiter=",")
        # for tmp in self.gridCoords:
        #     writer.writerow(tmp)
        # f.close()        
        
    def loadSourceImage( self ):
        imgPath = os.path.join(self.directory, self.imageID + ".tif")
        img = ImagePlus(imgPath)
        if img is None:
            raise ValueError("Couldn't find the image")
        self.sourceImage = img

    def openNext(self, auto=False):
        self.n = self.n + 1
        self.row, self.col, self.x, self.y = self.gridCoords[ self.n ]
        self.open(auto=auto)

    def openPrevious(self, auto=False):
        self.n = self.n - 1
        self.row, self.col, self.x, self.y = self.gridCoords[ self.n ]
        self.open(auto=auto)
    
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

# def dialogMinMax(gridObject):
#     gd = GenericDialog('Set new min and max')
#     gd.addNumericField('Min: ', gridObject.getMin(), 0)
#     gd.addNumericField('Max: ', gridObject.getMax(), 0)
#     minField = gd.getNumericFields().get(0)
#     maxField = gd.getNumericFields().get(1)
#     gd.showDialog()
#     if not gd.wasCanceled():
#         newMin = gd.getNextNumber()
#         newMax = gd.getNextNumber()
#         gridObject.setMinAndMax(newMin, newMax)
 



################### GUI

class ChangedMin(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        newValue = self.field.getText()
        currentMax = plateGrid.getMax()
        plateGrid.setMinAndMax(newValue, currentMax)

class ChangedMax(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        newValue = self.field.getText()
        currentMin = plateGrid.getMin()
        plateGrid.setMinAndMax(currentMin, newValue)

class NextImage(ActionListener):
  def actionPerformed(self, event):
      global plateGrid
      global listener
      global frame
      plateGrid.openNext()
      frame.setVisible(True)

class PreviousImage(ActionListener):
  def actionPerformed(self, event):
      global plateGrid
      global listener
      global frame
      plateGrid.openPrevious()
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

# class NextImageListener(KeyAdapter):
#     def keyPressed(self, keyEvent):
#         global plateGrid
#         global frame
#         IJ.log("clicked keyCode " + str(keyEvent.getKeyCode()))
#         keyPressed = keyEvent.getKeyCode()
#         if keyPressed == 78: # This is the 'n' key
#             plateGrid.openNext()
#             frame.setVisible(True)
#         if keyPressed == 10: # This is the 'enter' key
#             plateGrid.openNext()
#             frame.setVisible(True)
#         # Prevent further propagation of the key event:
#         keyEvent.consume()

plateGrid = GridReader(fp = "/Users/cm/Desktop/CCM_scorer/plate-001_plate1")

all = JPanel()
layout = GridLayout(4, 1)
all.setLayout(layout)

all.add( JLabel("  ") )
button = JButton("Previous image")
button.addActionListener( PreviousImage() )
#button.addKeyListener(NextImageListener())
all.add( button )

all.add( JLabel("Min") )
textField1 = JFormattedTextField( plateGrid.getMin() )
textField1.addActionListener( ChangedMin(textField1) )
#textField1.addKeyListener(listener)
all.add(textField1)

all.add( JLabel("Max") )
textField2 = JFormattedTextField( plateGrid.getMax() )
textField2.addActionListener( ChangedMax(textField2) )
#textField2.addKeyListener(listener)
all.add(textField2)

all.add( JLabel("Score :") )
scoreField = JTextField( "" )
scoreField.addActionListener( WriteScore(scoreField) )
scoreField.addActionListener( NextImage() )
#textField3.addKeyListener( NextImageListener() )
all.add(scoreField)

frame = JFrame("CCM scoring")
frame.getContentPane().add(JScrollPane(all))
frame.pack()
frame.addWindowListener( Closing() )
scoreField.requestFocusInWindow()
frame.setVisible(True)





#plateGrid.setMinMax(76, 136)
#imp = plateGrid.openNext()


#dialogMinMax(plateGrid)


# from java.awt import Color
# from java.awt.event import TextListener
# from ij import IJ
# from ij import Menus
# from ij.gui import GenericDialog


