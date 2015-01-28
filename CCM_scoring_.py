import csv
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
        self.sourceImage = IJ.getImage()

grid = GridReader("/Users/cm/Desktop/foo")

x,y = grid.next()
roi = Roi(int(x), int(y), int(grid.width), int(grid.width))
grid.sourceImage.setRoi(roi)

# gd = ij.gui.GenericDialog('Command Launcher')
# gd.addStringField('Command: ', '');
# prompt = gd.getStringFields().get(0)

grid.sourceImage2 = grid.sourceImage.getProcessor().crop()
grid.sourceImage.killRoi()

grid.sourceImage3 = ImagePlus("test", grid.sourceImage2)
grid.sourceImage3.show()

#.close()
