import csv, os
import ij.IJ
import ij.gui
from ij import IJ, ImagePlus, WindowManager
from ij.gui import Roi, Overlay, GenericDialog
from java.awt.event import KeyEvent, KeyAdapter, ActionListener

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

    def setMinMax(self, minVal, maxVal):
        self.min, self.max = minVal, maxVal
        self.openImage.getProcessor().setMinAndMax(self.min, self.max)
        self.openImage.updateAndDraw()

    def getMin(self):
        return self.min

    def getMax(self):
        return self.max
    
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
    
    def setContrast(self, auto=False):
        if auto:
            IJ.run(self.openImage, "Enhance Contrast", "saturated=0.35")
            self.min = self.openImage.getProcessor().getMin()
            self.max = self.openImage.getProcessor().getMax()
        else:
            self.openImage.getProcessor().setMinAndMax(self.min, self.max)
            self.openImage.updateAndDraw()
    
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


def doSomething(imp, keyEvent):
    """ A function to react to key being pressed on an image canvas. """
    IJ.log("clicked keyCode " + str(keyEvent.getKeyCode()) + " on image " + str(imp))
    # Prevent further propagation of the key event:
    keyEvent.consume()
 
class ListenToKey(KeyAdapter):
    def __init__(self, fxn):
        KeyAdapter.__init__(self)
        self.fxn = fxn
    def keyPressed(self, event):
        imp = event.getSource().getImage()
        self.fxn(imp, event)

def addKeyListeners(listen):
    for imp in map(WindowManager.getImage, WindowManager.getIDList()):
        win = imp.getWindow()
        if win is None:
            continue
        canvas = win.getCanvas()
        # Remove existing key listeners
        kls = canvas.getKeyListeners()
        map(canvas.removeKeyListener, kls)
        # Add our key listener
        canvas.addKeyListener(listen)
        # Optionally re-add existing key listeners
        # map(canvas.addKeyListener, kls)

listener = ListenToKey(doSomething)


plateGrid = GridReader(fp = "/Users/cm/Desktop/CCM_scorer/plate-001_plate1")
#plateGrid.setMinMax(76, 136)
#imp = plateGrid.openNext()
addKeyListeners(listener)


# from java.awt import Color
# from java.awt.event import TextListener
# from ij import IJ
# from ij import Menus
# from ij.gui import GenericDialog

# #commands = [c for c in ij.Menus.getCommands().keySet()]
# # Above, equivalent list as below:
# gd = GenericDialog('Set new min and max')
# gd.addNumericField('Min: ', grid.min)
# gd.addNumericField('Max: ', grid.max)
# minField = gd.getNumericFields().get(0)
# maxField = gd.getNumericFields().get(1)
# # prompt.setForeground(Color.red)

# prompt.addTextListener(TypeListener())
# gd.showDialog()
# if not gd.wasCanceled():
#     newMin = gd.getNextNumber()
#     newMax = gd.getNextNumber()
