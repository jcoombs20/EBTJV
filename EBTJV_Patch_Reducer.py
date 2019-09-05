import arcpy
import os
import sys

tmpFile = open("Patch Multiples.txt", "w")
tmpFile.write("COMID\n")

patches = arcpy.GetParameterAsText(0)

patchFields = ["Area_HA", "Feat_ID", "SHAPE@", "FID"]

#read patches records into array
arcpy.AddMessage("Reading patch records into array...")
patchCnt = long(arcpy.GetCount_management(patches).getOutput(0))
patchFeat = [0 for j in range(patchCnt)]
patchArray = [[0 for j in range(9)] for i in range(patchCnt)]
patchRecords = arcpy.da.SearchCursor(patches, patchFields)
i = 0
for patchRow in sorted(patchRecords, reverse=True):	
	patchFeat[i] = patchRow[1]
	patchArray[i] = patchRow
	i += 1

a = 0
dupsFID = []

while a < patchCnt:
	b = a + 1
	while b < patchCnt:
		tmpStr = patchArray[a][2].contains(patchArray[b][2])
		if tmpStr == True:
			try:
				arcpy.AddMessage("{0} contains {1}".format(patchArray[a][1], patchArray[b][1]))
				dupsFID.index(patchArray[b][3])
			except ValueError:
				dupsFID.append(patchArray[b][3])
		b += 1
	a += 1

for dup in dupsFID:
	delete = arcpy.da.UpdateCursor(patches, ["FID"], '"FID" = {0}'.format(dup))
	for rows in delete:
		arcpy.AddMessage("Deleting FID {0}".format(dup))
		delete.deleteRow()