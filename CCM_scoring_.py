import csv, os
import ij.IJ
import ij.gui
from ij import IJ, ImagePlus, WindowManager
from ij.gui import Roi, Overlay, GenericDialog
from java.awt.event import KeyEvent, KeyAdapter, ActionListener, WindowAdapter
from javax.swing import JScrollPane, JPanel, JComboBox, JLabel, JFrame, JButton, JFormattedTextField, JTextField
from java.awt import Color, GridLayout

# Keycode 78 is "n"

class GridReader:    
    def __init__(self, fp = None):
        if fp is None:
            self.fp = IJ.getFilePath("Grid file")
        else:
            self.fp = fp
        self.reader = csv.reader( open(self.fp,"r"), delimiter="\t" )
        firstLine = self.reader.next()
        try:
            self.rows, self.columns, self.width = tuple(firstLine)
        except ValueError:
            raise ValueError("There are the wrong number of fields on the first line")
        self.loadSourceImage()
        self.openImage = ImagePlus()
        self.openNext(auto=True)
    
    def loadSourceImage( self ):
        head, tail = os.path.split( self.fp )
        fn, ext = os.path.splitext( tail )
        fnSplit = fn.split("_")
        if len(fnSplit) != 2:
            raise ValueError("File name is not formatted properly")
        imgPath = os.path.join(head, fnSplit[0] + ".tif")
        img = ImagePlus(imgPath)
        if img is None:
            raise ValueError("Couldn't find the image")
        self.sourceImage = img
    
    def openNext( self, auto=False ):
        self.openImage.close()
        # Reads in the next grid coordinates
        x,y = self.reader.next()
        # Set the ROI on the source image
        roi = Roi(int(x), int(y), int(self.width), int(self.width))
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
        newValue = self.field.getValue()
        currentMax = plateGrid.getMax()
        plateGrid.setMinAndMax(newValue, currentMax)

class ChangedMax(ActionListener):
    def __init__(self, field):
        self.field = field
    def actionPerformed(self, event):
        global plateGrid
        newValue = self.field.getValue()
        currentMin = plateGrid.getMin()
        plateGrid.setMinAndMax(currentMin, newValue)

class NextImage(ActionListener):
  def actionPerformed(self, event):
      global plateGrid
      global listener
      global frame
      plateGrid.openNext()
      frame.setVisible(True)

class Closing(WindowAdapter):
    def windowClosing(self,e):
        #WindowManager.closeAllWindows()
        global plateGrid
        plateGrid.sourceImage.close()
        plateGrid.openImage.close()
        pass

class NextImageListener(KeyAdapter):
    def keyPressed(self, keyEvent):
        global plateGrid
        global frame
        IJ.log("clicked keyCode " + str(keyEvent.getKeyCode()))
        keyPressed = keyEvent.getKeyCode()
        if keyPressed == 78: # This is the 'n' key
            plateGrid.openNext()
            frame.setVisible(True)
        if keyPressed == 10: # This is the 'enter' key
            plateGrid.openNext()
            frame.setVisible(True)
        # Prevent further propagation of the key event:
        keyEvent.consume()

plateGrid = GridReader(fp = "/Users/cm/Desktop/CCM_scorer/plate-001_plate1")

all = JPanel()
layout = GridLayout(4, 1)
all.setLayout(layout)

all.add( JLabel("  ") )
button = JButton("Next image")
button.addActionListener( NextImage() )
button.addKeyListener(NextImageListener())
all.add( button )

all.add( JLabel("Min") )
textField1 = JFormattedTextField(68)
textField1.addActionListener( ChangedMin(textField1) )
#textField1.addKeyListener(listener)
all.add(textField1)

all.add( JLabel("Max") )
textField2 = JFormattedTextField(130)
textField2.addActionListener( ChangedMax(textField2) )
#textField2.addKeyListener(listener)
all.add(textField2)

all.add( JLabel("Score :") )
textField3 = JFormattedTextField( float(0.0) )
textField3.addActionListener( NextImage() )
#textField3.addKeyListener( NextImageListener() )
all.add(textField3)

frame = JFrame("CCM scoring")
frame.getContentPane().add(JScrollPane(all))
frame.pack()
frame.addWindowListener( Closing() )
frame.setVisible(True)





#plateGrid.setMinMax(76, 136)
#imp = plateGrid.openNext()


#dialogMinMax(plateGrid)


# from java.awt import Color
# from java.awt.event import TextListener
# from ij import IJ
# from ij import Menus
# from ij.gui import GenericDialog


