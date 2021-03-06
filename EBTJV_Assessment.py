import arcpy
import os
import sys

#Gets EBTJV assessment code based on salmonid species present
def get_code(bkt, bnt, rbt, bktStock):

	if useStock == True:
		if bkt >= 1 and bnt >= 1 and rbt >= 1:
			return "1.4"
		elif bkt >= 1 and rbt >= 1:
			return "1.3"
		elif bkt >= 1 and bnt >= 1:
			return "1.2"
		elif bkt >= 1:
			if bktStock >= 1:
				return "1.5"
			else:
				return "1.1"
		elif bnt >= 1 and rbt >= 1:
			return "0.4"
		elif rbt >= 1:
			return "0.3"
		elif bnt >= 1:
			return "0.2"
		elif bktStock >= 1:
			return "0.5"
		else:
			return "0"
	else:
		if bkt >= 1 and bnt >= 1 and rbt >= 1:
			return "1.4"
		elif bkt >= 1 and rbt >= 1:
			return "1.3"
		elif bkt >= 1 and bnt >= 1:
			return "1.2"
		elif bkt >= 1:
			return "1.1"
		elif bnt >= 1 and rbt >= 1:
			return "0.4"
		elif rbt >= 1:
			return "0.3"
		elif bnt >= 1:
			return "0.2"
		else:
			return "0"


#Compare species occurrence for two samples in the same year in the same catchment
def findSpecies(newCode, oldCode):
	status = "unchanged"
	bkt = 0
	bktStock = 0
	bnt = 0
	rbt = 0

	if oldCode[0] == "1":
		bkt = 1
	if oldCode[0:3] == "0.5":
		bktStock = 1
	if oldCode[0:3] == "0.2" or oldCode[0:3] == "0.4" or oldCode[0:3] == "1.2" or oldCode[0:3] == "1.4":
		bnt = 1
	if oldCode[0:3] == "0.3" or oldCode[0:3] == "0.4" or oldCode[0:3] == "1.3" or oldCode[0:3] == "1.4":
		rbt = 1

	if newCode[0] == "1":
		if bkt == 0:
			bkt = 1
			status = "changed"
	if newCode[0:3] == "0.5":
		if bktStock == 0:
			bktStock = 1
			status = "changed"
	if newCode[0:3] == "0.2" or newCode[0:3] == "0.4" or newCode[0:3] == "1.2" or newCode[0:3] == "1.4":
		if bnt == 0:
			bnt = 1
			status = "changed"
	if newCode[0:3] == "0.3" or newCode[0:3] == "0.4" or newCode[0:3] == "1.3" or newCode[0:3] == "1.4":
		if rbt == 0:
			rbt = 1
			status = "changed"
	
	arcpy.AddMessage("{0}, {1}, {2}, {3}".format(status, bkt, bnt, rbt))
	return status, bkt, bnt, rbt, bktStock


#compares dam and sample point locations to determine if sample is upstream or downstream of dam
def dam_samp(damInd):
	damFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(damArray[damInd][1], damArray[damInd][2]), "1").getOutput(0))
	if damFDRNull != "NoData":
		tmpDam = getNoData(damArray[damInd][1], damArray[damInd][2], damFDRNull)
	else:
		tmpDam = [damArray[damInd][1], damArray[damInd][2]]

	sampFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(bktRow[1], bktRow[2]), "1").getOutput(0))
	tmpSamp = getNoData(bktRow[1], bktRow[2], sampFDRNull)

	damFDR = arcpy.GetCellValue_management(fdr, "{0} {1}".format(tmpDam[0], tmpDam[1]), "1")
	sampFDR = arcpy.GetCellValue_management(fdr, "{0} {1}".format(tmpSamp[0], tmpSamp[1]), "1")
	sampLoc = getLoc(tmpDam, damFDR, tmpSamp, sampFDR)
	return sampLoc


#Determines if sample location is above or below dam location
def getLoc(tmpDam, damFDR, tmpSamp, sampFDR):
	eucDist = math.sqrt(math.pow(tmpSamp[0] - tmpDam[0],2) + math.pow(tmpSamp[1] - tmpDam[1],2))
	tmpDist = eucDist
	X = tmpSamp[0]
	Y = tmpSamp[1]

	tmpVal = sampFDR
	while tmpDist > 43 and tmpDist < 3 * eucDist:
		#arcpy.AddMessage("tmpDist: {0}, eucDist: {1}, tmpVal: {2}".format(tmpDist, eucDist, tmpVal))
		if tmpVal == "0":
			return "Above"
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
		tmpVal = str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X, Y), "1").getOutput(0))
		if tmpVal == "NoData":
			break
		tmpDist = math.sqrt(math.pow(X - tmpDam[0],2) + math.pow(Y - tmpDam[1],2))

	if tmpDist <= 43:
		if tmpDist < eucDist:
			return "Above"
		else:
			return "Below"
	else:
		return "Below"


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


#gets PlusFlowlineVAA records matching catchment polygon feature id
def get_PFVAA(featureID, catchCnt, tmpLength, tmpCode):
	try:
		vaaIndex = vaaID.index(featureID)
		get_PFlow(vaaArray[vaaIndex][1], catchCnt, vaaArray[vaaIndex][2], featureID, tmpLength, tmpCode)
	except ValueError:
		arcpy.AddMessage("Error indexing FlowlineVAA comID {0}".format(featureID))


#gets PlusFlow records matching the PFVAA NodeNumber
def get_PFlow(NodeNum, catchCnt, strOrd, oldFeat, tmpLength, tmpCode):
	try:
		pfIndex = pfNode.index(NodeNum)
		tmpFeat = -1
		while pfArray[pfIndex][0] == NodeNum:
			if pfArray[pfIndex][1] > 0 and pfArray[pfIndex][1] != tmpFeat:
				tmpFeat = pfArray[pfIndex][1]
				get_catchPoly(pfArray[pfIndex][1], catchCnt, strOrd, NodeNum, oldFeat, tmpLength, tmpCode)
			pfIndex += 1
			if pfIndex == pfCnt:
				break
	except ValueError:
		arcpy.AddMessage("Error indexing Flowline Node Number {0}".format(NodeNum))


#gets catchment polygons for catchments upstream of sample point
def get_catchPoly(featureID, catchCnt, strOrd, NodeNum, fromComID, tmpLength, tmpCode):
	try:
		cpInd = cpFeat.index(featureID)
	except ValueError:
		try:
			vaaInd = vaaID.index(featureID)
			get_PFlow(vaaArray[vaaInd][1], catchCnt, strOrd, vaaArray[vaaInd][0], tmpLength, tmpCode)
			return
		except ValueError:
			arcpy.AddMessage("error with featureID {0}".format(featureID))
			cpInd = cpFeat.index(find_comID(fromComID, featureID, NodeNum))
	
	tmpBi = 0
	for catch in catchUsed:
		if catch == cpArray[cpInd][1]:
			tmpBi = 1
			break

	catchCnt += 1
	vaaIndex = vaaID.index(cpArray[cpInd][1])
	strOrd = vaaArray[vaaIndex][2]
	tmpLength += vaaArray[vaaIndex][3]
	fCode = vaaArray[vaaIndex][4]

	#Determine if dam is present, and if so its distance to nearest stream
	damHere, damIndex = get_dam(cpArray[cpInd][1])
	
	if damHere == "Yes":
		sampFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(damArray[damIndex][1], damArray[damIndex][2]), "1").getOutput(0))
		tmpSpot = getNoData(damArray[damIndex][1], damArray[damIndex][2], sampFDRNull)
		tmpdamDist = math.sqrt(math.pow(tmpSpot[0] - damArray[damIndex][1],2) + math.pow(tmpSpot[1] - damArray[damIndex][2],2))

		if usedamDis == True:
			if tmpdamDist > damDis:
				damHere = "No"
		#arcpy.AddMessage("tmpdamDist = {0}, damDis = {1}, damHere = {2}".format(tmpdamDist, damDis, damHere))


	tmpFilter = 0
	if usestrDis == True:
		if tmpCode[0:3] == "1.1" or tmpCode[0:3] == "1.5":
			if tmpLength > strDisBKT:
				tmpFilter = 1
		elif tmpCode[0] == "1":
			if tmpLength > strDisBKT and tmpLength > strDisInv:
				tmpFilter = 1
			elif tmpLength > strDisBKT:
				tmpCode = "0" + tmpCode[1:]
			elif tmpLength > strDisInv:
				tmpCode = tmpCode[:2] + "1" + tmpCode[3:]
		else:
			if tmpLength > strDisInv:
				tmpFilter = 1
	
	if ((tmpYear + sampDiff) >= cpArray[cpInd][4] and catchCnt <= cpArray[cpInd][3] and tmpBi == 0 and tmpFilter == 0) or (cpArray[cpInd][3] == 0 and tmpBi == 0 and tmpFilter == 0):
		if fCode != 56600: #Coastline
			cpArray[cpInd][2] = tmpCode
			cpArray[cpInd][3] = catchCnt
			cpArray[cpInd][4] = tmpYear
			cpArray[cpInd][6] = damHere
			cpArray[cpInd][7] = strOrd
			cpArray[cpInd][9] = tmpLength
			cpArray[cpInd][10] = sampOID
			catchUsed.append(cpArray[cpInd][1])
		
			if cpArray[cpInd][6] == "No":
				get_PFVAA(cpArray[cpInd][1], catchCnt, tmpLength, tmpCode)


#searches for feature ID when NHD 'FromComID' doesn't exist
def find_comID(fromComID, featureID, NodeNum):
	try:
		streamIndex = streamID.index(featureID)
		return streamArray[streamIndex][2]
	except ValueError:
		#get stream record and add to array
		streamIndex = streamID.index(0)
		streamRecords = arcpy.da.SearchCursor(streams, streamFields, '"COMID" = {0}'.format(featureID), CRSR.spatialReference)
		for streamRow in streamRecords:
			streamID[streamIndex] = streamRow[0]
			streamArray[streamIndex][0] = streamRow[0]
			streamArray[streamIndex][1] = streamRow[1]
		
		try:
			for part in streamArray[streamIndex][1]:
				for pnt in part:
					X = pnt.X
					Y = pnt.Y
					break
				break

			tmpGrid = long(arcpy.GetCellValue_management(catchRast, "{0} {1}".format(X, Y), "1").getOutput(0))
			tmpInd = cpGrid.index(tmpGrid)
			toComID = cpArray[tmpInd][1]
			
			if toComID == fromComID:
				while toComID == fromComID:
					if str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X-30, Y), "1").getOutput(0)) == "1":
						X -= 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X-30, Y+30), "1").getOutput(0)) == "2":
						X -= 30
						Y += 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X, Y+30), "1").getOutput(0)) == "4":
						Y += 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X+30, Y+30), "1").getOutput(0)) == "8":
						X += 30
						Y += 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X+30, Y), "1").getOutput(0)) == "16":
						X += 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X+30, Y-30), "1").getOutput(0)) == "32":
						X += 30
						Y -= 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X, Y-30), "1").getOutput(0)) == "64":
						Y -= 30
					elif str(arcpy.GetCellValue_management(fdr, "{0} {1}".format(X-30, Y-30), "1").getOutput(0)) == "128":
						X -= 30
						Y -= 30
					else:
						arcpy.AddMessage("breaking loop")
						break
					tmpGrid = long(arcpy.GetCellValue_management(catchRast, "{0} {1}".format(X, Y), "1").getOutput(0))
					tmpInd = cpGrid.index(tmpGrid)
					toComID = cpArray[tmpInd][1]

			streamArray[streamIndex][2] = toComID
			tmpFile.write("{0}\t{1}\t{2}\t{3}\n".format(featureID, fromComID, NodeNum, streamArray[streamIndex][2]))
			return toComID
		except:
			arcpy.AddMessage("Error reading geometry for featureID {0}".format(streamArray[streamIndex][0]))
			streamArray[streamIndex][2] = 0
			return 0


#determines if dam is present in catchment polygon based on featureID
def get_dam(comID):
	try:
		damIndex = damID.index(comID)
		return "Yes", damIndex
	except ValueError:
		return "No", 0


#determines stream order based on featureID
def get_order(comID):
	try:
		vaaIndex = vaaID.index(comID)
		return vaaArray[vaaIndex][2]
	except ValueError:
		return 0


#Writes cpArray to catchPoly
def dump_cpArray():
	i = 0
	cpRecords = arcpy.da.UpdateCursor(catchPoly, cpFields)
	for cpRow in cpRecords:
		if cpArray[i] != cpRow:
			cpRow = cpArray[i]
			cpRecords.updateRow(cpRow)
		i += 1


#***** Beginning of algorithm*****
sys.setrecursionlimit(10000)

bktPoints = arcpy.GetParameterAsText(0)
useStock = arcpy.GetParameter(1)
useAbsence = arcpy.GetParameter(2)
absYear = long(arcpy.GetParameterAsText(3))
catchRast = arcpy.GetParameterAsText(4)
catchPoly = arcpy.GetParameterAsText(5)
streams = arcpy.GetParameterAsText(6)
fdr = arcpy.GetParameterAsText(7)
fdrNull = arcpy.GetParameterAsText(8)
dams = arcpy.GetParameterAsText(9)
plusFlowVAA = arcpy.GetParameterAsText(10)
plusFlow = arcpy.GetParameterAsText(11)
sampYear = long(arcpy.GetParameterAsText(12))
sampDiff = long(arcpy.GetParameterAsText(13))
usepntDis = arcpy.GetParameter(14)
pntDis = long(arcpy.GetParameterAsText(15))
usestrOrd = arcpy.GetParameter(16)
strOrdBkt = long(arcpy.GetParameterAsText(17))
strOrdInv = long(arcpy.GetParameterAsText(18))
usestrDis = arcpy.GetParameter(19)
strDisBKT = float(arcpy.GetParameterAsText(20))
strDisInv = float(arcpy.GetParameterAsText(21))
usedamDis = arcpy.GetParameter(22)
damDis = float(arcpy.GetParameterAsText(23))
addDel = arcpy.GetParameter(24)
classType = arcpy.GetParameter(25)

tmpDescribe = arcpy.Describe(catchPoly)
tmpPath = "{0}".format(tmpDescribe.catalogPath)
a = tmpPath.rindex("\\")
outPath = tmpPath[:a]

tmpFile = open("{0}/Error Log.txt".format(outPath), "w")
tmpFile.write("ToComID\tFromComID\tNode\tNewComID\n")

tmpSampErr = open("{0}/Sample Point Errors.txt".format(outPath), "w")
tmpSampErr.write("OID\tSiteDate\tLongitude\tLatitude\n")

#Write parameters to file
tmpParam = open("{0}/Catchment Parameter Settings.txt".format(outPath), "w")
tmpParam.write("Sample Location Point Layer: {0}\n".format(bktPoints))
tmpParam.write("Use stocking information: {0}\n".format(useStock))
tmpParam.write("Use 'Trout Absent' sampling points: {0}\n".format(useAbsence))
if useAbsence == True:
	tmpParam.write("Absent since (year): {0}\n".format(absYear))
tmpParam.write("Catchment Raster Layer: {0}\n".format(catchRast))
tmpParam.write("Catchment Feature Layer: {0}\n".format(catchPoly))
tmpParam.write("Flowline Feature Layer: {0}\n".format(streams))
tmpParam.write("Flow Direction Raster Layer: {0}\n".format(fdr))
tmpParam.write("Flow Direction Null Raster Layer: {0}\n".format(fdrNull))
tmpParam.write("Barrier Point Layer: {0}\n".format(dams))
tmpParam.write("PlusFlowline VAA Table: {0}\n".format(plusFlowVAA))
tmpParam.write("PlusFlow Table: {0}\n".format(plusFlow))
tmpParam.write("Assessment Year: {0}\n".format(sampYear))
tmpParam.write("Sample Year Differential: {0}\n".format(sampDiff))
tmpParam.write("Use Max Sample Point Distance: {0}\n".format(usepntDis))
if usepntDis == True:
	tmpParam.write("Max Sample Point Distance (m): {0}\n".format(pntDis))
tmpParam.write("Use Max Stream Order: {0}\n".format(usestrOrd))
if usestrOrd == True:
	tmpParam.write("Max Stream Order Brook Trout: {0}\n".format(strOrdBkt))
	tmpParam.write("Max Stream Order Brown & Rainbow Trout: {0}\n".format(strOrdInv))
tmpParam.write("Use Max Stream Distance: {0}\n".format(usestrDis))
if usestrDis == True:
	tmpParam.write("Max Stream Distance Brook Trout (km): {0}\n".format(strDisBKT))
	tmpParam.write("Max Stream Distance Brown & Rainbow Trout: {0}\n".format(strDisInv))
tmpParam.write("Use Max Barrier Distance: {0}\n".format(usedamDis))
if usedamDis == True:
	tmpParam.write("Max Barrier Point Distance (m): {0}\n".format(damDis))
tmpParam.write("Delete and Re-Add Fields: {0}\n".format(addDel))
tmpParam.write("Use only most recent sample: {0}\n".format(classType))
tmpParam.close()

#Get spatial reference for catchments raster layer to use with cursors
CRSR = arcpy.Describe(catchRast)

if addDel == True:
	#Delete field if present
	if len(arcpy.ListFields(catchPoly, "EBTJV_Code")) > 0:
		arcpy.AddMessage("Deleting fields from Catchment Feature layer...")
		arcpy.DeleteField_management(catchPoly, ["EBTJV_Code", "Catch_Cnt", "Cum_Length", "Samp_Year", "Samp_Dist", "Samp_OID", "Dam", "Samp_Loc", "Str_Order", "Comment"])

	#Add field to layer to populate with assessment code
	arcpy.AddMessage("Adding fields to Catchment Feature layer...")
	arcpy.AddField_management(catchPoly, "EBTJV_Code", "TEXT")
	arcpy.AddField_management(catchPoly, "Catch_Cnt", "LONG")
	arcpy.AddField_management(catchPoly, "Cum_Length", "DOUBLE")
	arcpy.AddField_management(catchPoly, "Samp_Year", "LONG")
	arcpy.AddField_management(catchPoly, "Samp_Dist", "DOUBLE")
	arcpy.AddField_management(catchPoly, "Samp_OID", "TEXT")
	arcpy.AddField_management(catchPoly, "Dam", "TEXT")
	arcpy.AddField_management(catchPoly, "Samp_Loc", "TEXT")
	arcpy.AddField_management(catchPoly, "Str_Order", "LONG")
	arcpy.AddField_management(catchPoly, "Comment", "TEXT")

	arcpy.AddMessage("Filling in default EBTJV_Code of -1...")
	arcpy.CalculateField_management(catchPoly, "EBTJV_Code", "-1", "PYTHON_9.3")
	arcpy.AddMessage("Filling in default Samp_OID of -1...")
	arcpy.CalculateField_management(catchPoly, "Samp_OID", "-1", "PYTHON_9.3")

if useStock == True:
	bktFields = ["SiteDate", "SHAPE@X", "SHAPE@Y", "BKT", "BNT", "RBT", "OID@", "BKT_STOCK"]
else:
	bktFields = ["SiteDate", "SHAPE@X", "SHAPE@Y", "BKT", "BNT", "RBT", "OID@"]

cpFields = ["GRIDCODE", "FEATUREID", "EBTJV_Code", "Catch_Cnt", "Samp_Year", "Samp_Dist", "Dam", "Str_Order", "Comment", "Cum_Length", "Samp_OID", "Samp_Loc"]
streamFields = ["COMID", "SHAPE@"]
damFields = ["FEATUREID", "SHAPE@X", "SHAPE@Y"]
VAAFields = ["COMID", "FromNode", "STREAMORDE", "LengthKM", "FCODE"]
PFlowFields = ["NodeNumber", "FromComId"]

#read catchPoly records into array
arcpy.AddMessage("Reading Catchment records into array...")
cpCnt = long(arcpy.GetCount_management(catchPoly).getOutput(0))
cpGrid = [0 for j in range(cpCnt)]
cpFeat = [0 for j in range(cpCnt)]
cpArray = [[0 for j in range(12)] for i in range(cpCnt)]
cpRecords = arcpy.da.UpdateCursor(catchPoly, cpFields)
i = 0
for cpRow in cpRecords:
	cpGrid[i] = cpRow[0]
	cpFeat[i] = cpRow[1]
	cpArray[i] = cpRow
	i += 1

#Initialize stream arrays
arcpy.AddMessage("Reading NHD Flowline records into array...")
streamCnt = long(arcpy.GetCount_management(streams).getOutput(0))
streamArray = [[0 for j in range(3)] for i in range(streamCnt)]
streamID = [0 for j in range(streamCnt)]

#read dams records into array
arcpy.AddMessage("Reading Barrier records into array...")
damCnt = long(arcpy.GetCount_management(dams).getOutput(0))
damArray = [[0 for j in range(3)] for i in range(damCnt)]
damID = [0 for j in range(damCnt)]
damRecords = arcpy.da.SearchCursor(dams, damFields, "", CRSR.spatialReference)
i = 0
for damRow in damRecords:
	damID[i] = damRow[0]
	damArray[i] = damRow
	i += 1

#read PlusFlowlineVAA records into array
arcpy.AddMessage("Reading PlusFlowlineVAA records into array...")
vaaCnt = long(arcpy.GetCount_management(plusFlowVAA).getOutput(0))
vaaArray = [[0 for j in range(3)] for i in range(vaaCnt)]
vaaID = [0 for j in range(vaaCnt)]
vaaRecords = arcpy.da.SearchCursor(plusFlowVAA, VAAFields)
i = 0
for vaaRow in vaaRecords:
	vaaID[i] = vaaRow[0]
	vaaArray[i] = vaaRow
	i += 1

#read PlusFlow records into array
arcpy.AddMessage("Reading PlusFlow records into array...")
pfCnt = long(arcpy.GetCount_management(plusFlow).getOutput(0))
pfArray = [[0 for j in range(2)] for i in range(pfCnt)]
pfNode = [0 for j in range(pfCnt)]
pfRecords = arcpy.da.SearchCursor(plusFlow, PFlowFields)
i = 0
for pfRow in sorted(pfRecords):
	pfNode[i] = pfRow[0]
	pfArray[i] = pfRow
	i += 1

bktRecords = arcpy.da.SearchCursor(bktPoints, bktFields, "", CRSR.spatialReference)
i = 0
absBi = 0
classBi = 0

for bktRow in sorted(bktRecords, reverse=True):
	#Get sampling occasion year
	catchUsed = []
	tmpYear = bktRow[0].year

	i += 1
	arcpy.AddMessage("sample: {0}, Date: {1}".format(i, bktRow[0]))
	
	#Get assessment code
	if useStock == True:
		tmpCode = get_code(bktRow[3], bktRow[4], bktRow[5], bktRow[7])
		
	else:
		tmpCode = get_code(bktRow[3], bktRow[4], bktRow[5], 0)
	
	tmpBi = 1
	if useAbsence == False:
		if tmpCode == "0":
			tmpBi = 0

	#arcpy.AddMessage("{0}".format(bktRow[6]))

	if tmpYear <= sampYear and tmpBi <> 0:
		#Determine points distance from nearest stream
		sampFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(bktRow[1], bktRow[2]), "1").getOutput(0))
		tmpSpot = getNoData(bktRow[1], bktRow[2], sampFDRNull)
		tmpDist = math.sqrt(math.pow(tmpSpot[0] - bktRow[1],2) + math.pow(tmpSpot[1] - bktRow[2],2))

		#Alter assessment code
		if sampYear - tmpYear > 10:
			tmpCode += "P"

		sampOID = str(bktRow[6])

		#Get catchRast value of sampling occasion
		try:
			gridCode = long(arcpy.GetCellValue_management(catchRast, "{0} {1}".format(bktRow[1], bktRow[2]), "1").getOutput(0))

			#Get catchPoly records filtering by gridcode
			cpIndex = cpGrid.index(gridCode)

			sampLoc = ""
			catchCnt = 1
			vaaIndex = vaaID.index(cpArray[cpIndex][1])
			tmpLength = vaaArray[vaaIndex][3]
			fCode = vaaArray[vaaIndex][4]

			#Determine if dam is present, and if so its distance to nearest stream
			damHere, damIndex = get_dam(cpArray[cpIndex][1])
	
			if damHere == "Yes":
				sampFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(damArray[damIndex][1], damArray[damIndex][2]), "1").getOutput(0))
				tmpSpot = getNoData(damArray[damIndex][1], damArray[damIndex][2], sampFDRNull)
				tmpdamDist = math.sqrt(math.pow(tmpSpot[0] - damArray[damIndex][1],2) + math.pow(tmpSpot[1] - damArray[damIndex][2],2))

				if usedamDis == True:
					if tmpdamDist > damDis:
						damHere = "No"
				#arcpy.AddMessage("tmpdamDist = {0}, damDis = {1}, damHere = {2}".format(tmpdamDist, damDis, damHere))

			#Accomodate for trout present samples occurring prior to a trout absent sample but after the absence year and greater than the overwrite period
			if useAbsence == True:
				absBi = 0
				if ((cpArray[cpIndex][2] == "0" or cpArray[cpIndex][2] == "0P") and tmpCode <> "0" and tmpCode <> "0P"):
					if tmpYear >= absYear and (tmpYear + sampDiff) >= cpArray[cpIndex][4]:
						absBi = 1

			#Determine if samples should be classified based on most recent sample or most recent year
			if classType == False:
				classBi = 0
				if tmpYear == cpArray[cpIndex][4]:
					if tmpCode != cpArray[cpIndex][2] and tmpCode != "0" and tmpCode != "0P" and cpArray[cpIndex][3] == 1:
						status, bkt, bnt, rbt, bktStock = findSpecies(tmpCode, cpArray[cpIndex][2])
						if status == "changed":
							classBi = 1
							tmpCode = get_code(bkt, bnt, rbt, bktStock)
							sampOID = "{0}; {1}".format(cpArray[cpIndex][10], sampOID)

			if ((tmpYear + sampDiff) >= cpArray[cpIndex][4] and cpArray[cpIndex][3] > 1) or cpArray[cpIndex][3] == 0 or absBi == 1 or classBi == 1:
				if fCode != 56600: #Coastline
					if absBi == 1:
						cpArray[cpIndex][8] = "{0} = {1}; {2}".format(cpArray[cpIndex][4], cpArray[cpIndex][2], cpArray[cpIndex][8])

					cpArray[cpIndex][2] = tmpCode
					cpArray[cpIndex][3] = catchCnt
					cpArray[cpIndex][4] = tmpYear
					cpArray[cpIndex][5] = tmpDist
					cpArray[cpIndex][6] = damHere
					cpArray[cpIndex][7] = get_order(cpArray[cpIndex][1])
					cpArray[cpIndex][9] = tmpLength
					cpArray[cpIndex][10] = sampOID
					catchUsed.append(cpArray[cpIndex][1])
				
					if damHere == "Yes":
						#Determine sample location relative to dam by getting dam records filtered by featureID
						#damIndex = damID.index(cpArray[cpIndex][1])
						sampLoc = dam_samp(damIndex)
						cpArray[cpIndex][11] = sampLoc

					tmpFilter = 0
					if usepntDis == True:
						if tmpDist > pntDis:
							tmpFilter = 1

					if usestrOrd == True:
						if tmpCode[0:3] == "1.1" or tmpCode[0:3] == "1.5":
							if cpArray[cpIndex][7] > strOrdBkt:
								tmpFilter = 1
						elif tmpCode[0] == "1":
							if cpArray[cpIndex][7] > strOrdBkt and cpArray[cpIndex][7] > strOrdInv:
								tmpFilter = 1
							elif cpArray[cpIndex][7] > strOrdBkt:
								tmpCode = "0" + tmpCode[1:]
							elif cpArray[cpIndex][7] > strOrdInv:
								tmpCode = tmpCode[:2] + "1" + tmpCode[3:]
						else:
							if cpArray[cpIndex][7] > strOrdInv:
								tmpFilter = 1

					if usestrDis == True:
						if tmpCode[0:3] == "1.1" or tmpCode[0:3] == "1.5":
							if tmpLength > strDisBKT:
								tmpFilter = 1
						elif tmpCode[0] == "1":
							if tmpLength > strDisBKT and tmpLength > strDisInv:
								tmpFilter = 1
							elif tmpLength > strDisBKT:
								tmpCode = "0" + tmpCode[1:]
							elif tmpLength > strDisInv:
								tmpCode = tmpCode[:2] + "1" + tmpCode[3:]
						else:
							if tmpLength > strDisInv:
								tmpFilter = 1

					if sampLoc != "Below" and tmpCode != "0" and tmpCode != "0P" and tmpCode != "0.5" and tmpCode != "0.5P" and tmpFilter == 0:
						get_PFVAA(cpArray[cpIndex][1], catchCnt, tmpLength, tmpCode)
			else:
				cpArray[cpIndex][8] += "{0} = {1}; ".format(tmpYear, tmpCode)
		except ValueError:
			#arcpy.AddMessage("{0}".format(gridCode))
			arcpy.AddMessage("No Catchment for point at {0}, {1}".format(bktRow[1], bktRow[2]))
			tmpSampErr.write("{0}\t{1}\t{2}\t{3}\n".format(bktRow[6], bktRow[0], bktRow[1], bktRow[2]))
			
dump_cpArray()
tmpFile.close()
tmpSampErr.close()