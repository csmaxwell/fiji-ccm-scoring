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
        self.getImage()
    
    def next(self):
        return self.reader.next()

    def getImage(self):
        head, tail = os.path.split( self.fp )
        fn, ext = os.path.splitext( tail )
        fnSplit = fn.split("_")
        if len(fnSplit) != 2:
            raise ValueError("File name is not formatted properly")
        imgPath = os.path.join(head, fnSplit[0] + ".tif")
        img = IJ.openImage(imgPath)
        if img is None:
            raise ValueError("Couldn't find the image")
        self.sourceImage = img

        
grid = GridReader("/Users/cm/Desktop/CCM_scorer/plate-001_plate1")

x,y = grid.next()
x,y = grid.next()

roi = Roi(int(x), int(y), int(grid.width), int(grid.width))
grid.sourceImage.setRoi(roi)
grid.sourceImage2 = grid.sourceImage.getProcessor().crop()
grid.sourceImage.killRoi()
grid.sourceImage3 = ImagePlus("test", grid.sourceImage2)
IJ.run(grid.sourceImage3, "Enhance Contrast", "saturated=0.35")
grid.sourceImage3.show()

#.close()


