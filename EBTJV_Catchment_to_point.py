import arcpy
import os

#Moves dam and sample points to nearest stream using fdr (flow direction) raster layer
def getNoData(X,Y, tmpVal):
	while tmpVal != "NoData":
		if tmpVal == "0":
			return [X, Y]
		elif tmpVal == "1":
			X += 30
		elif tmpVal == "2":
			X += 30
			Y -= 30
		elif tmpVal == "4":
			Y -= 30
		elif tmpVal == "8":
			X -= 30
			Y -= 30
		elif tmpVal == "16":
			X -= 30
		elif tmpVal == "32":
			X -= 30
			Y += 30
		elif tmpVal == "64":
			Y += 30
		elif tmpVal == "128":
			X += 30
			Y += 30
		tmpVal = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(X, Y), "1").getOutput(0))
	return [X, Y]

#***** Beginning of algorithm*****

catch = arcpy.GetParameterAsText(0)
comID = arcpy.GetParameterAsText(1)
catchCode = arcpy.GetParameterAsText(2)
streams = arcpy.GetParameterAsText(3)
fdrNull = arcpy.GetParameterAsText(4)
outPnt = arcpy.GetParameterAsText(5)

#Get spatial reference for catchments raster layer to use with cursors
CRSR = arcpy.Describe(fdrNull)

arcpy.AddMessage("Making centroid point layer from polygons...")
arcpy.FeatureToPoint_management(catch, outPnt, "INSIDE")
pntFields = ["SHAPE@XY", comID, catchCode]

arcpy.AddMessage("Moving centroids to nearest stream based on flow direction...")
pntRecords = arcpy.da.UpdateCursor(outPnt, pntFields, "", CRSR.spatialReference)
i = 0

for pntRow in pntRecords:
	i += 1
	X = pntRow[0][0]
	Y = pntRow[0][1]
	tmpVal = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(X, Y), "1").getOutput(0))

	tmpShape = getNoData(X,Y, tmpVal)
	pntRow[0] = tmpShape
	pntRecords.updateRow(pntRow)
	arcpy.AddMessage("sample: {0}".format(i))

#arcpy.AddMessage("Creating copy of unsnapped, modified centroids...")
#a = outPnt.rindex(".")
#outSnap = outPnt[:a] + "_Unsnapped.shp"
#arcpy.CopyFeatures_management(outPnt, outSnap)

arcpy.AddMessage("Snapping updated centroids to edge of nearest stream within 50 meters...")
arcpy.Snap_edit(outPnt, [[streams, "EDGE", "50 Meters"]])
	
