import arcpy
import os
import sys

#*****Beginning of algorithm*****
catchPoly = arcpy.GetParameterAsText(0)
dams = arcpy.GetParameterAsText(1)
outName = arcpy.GetParameterAsText(2)

tmpFile = open(outName, "w")
tmpFile.write("COMID\n")

#read catchPoly records into array
arcpy.AddMessage("Reading Catchment records into array...")
cpCnt = long(arcpy.GetCount_management(catchPoly).getOutput(0))
cpFeat = [0 for j in range(cpCnt)]
#*****Changed to read Flowline input, change COMID to FEATUREID if you want to use Catchment input*****
cpRecords = arcpy.da.SearchCursor(catchPoly, ["COMID"])
i = 0
for cpRow in cpRecords:	
	cpFeat[i] = cpRow[0]
	i += 1

#read dams records into array
arcpy.AddMessage("Reading Barrier records into array...")
damCnt = long(arcpy.GetCount_management(dams).getOutput(0))
damID = [0 for j in range(damCnt)]
damRecords = arcpy.da.SearchCursor(dams, ["COMID"])
i = 0
for damRow in damRecords:
	damID[i] = damRow[0]
	i += 1

i = 1
rows = len(damID)
errCnt = 0

for tmpID in damID:
	arcpy.AddMessage("Record {0} of {1}".format(i, rows))

	try:
		a = cpFeat.index(tmpID)
	except ValueError:
		errCnt += 1
		tmpFile.write("{0}\n".format(tmpID))
	i += 1

tmpFile.close()
arcpy.AddMessage("{0} COMID errors found".format(errCnt))

