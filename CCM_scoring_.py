import csv, os
import ij.IJ
import ij.gui
from ij import IJ, ImagePlus
from ij.gui import Roi, Overlay

class GridReader:    
    def __init__(self, fp = None):
        if fp is None:
            self.fp = IJ.getFilePath("Grid file")
        else:
            self.fp = fp
        self.reader = csv.reader( open(self.fp,"r"), delimiter="\t" )
        #
        firstLine = self.reader.next()
        #
        try:
            self.rows, self.columns, self.width = tuple(firstLine)
        except ValueError:
            raise ValueError("There are the wrong number of fields on the first line")
        # 
        self.loadSourceImage()
        self.openImage = ImagePlus()
    
    def openNext( self ):
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
        self.openImage = ImagePlus("test", processor)
        IJ.run(self.openImage, "Enhance Contrast", "saturated=0.35")
        self.openImage.show()
    
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


        
grid = GridReader("/Users/cm/Desktop/CCM_scorer/plate-001_plate1")
grid.openNext()
grid.openNext()


