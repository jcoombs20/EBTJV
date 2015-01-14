import arcpy
import os
import sys
import operator

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

#Determines most downstream catchment containing salmonids
def moveDownstream(featureID):												
	firstFeat = featureID											
	oldFeat = featureID											
	while 1 == 1:											
		try:										
			vaaIndex = vaaID.index(featureID)									
			if vaaArray[vaaIndex][4] != 56600:									
				try:								
					pfIndex = pfNode.index(vaaArray[vaaIndex][5])							
					try:							
						cpInd = cpFeat.index(pfArray[pfIndex][2])						
												
						if cpArray[cpInd][6] == "Yes" or cpArray[cpInd][7] == 0 or cpArray[cpInd][2] == "0" or cpArray[cpInd][2] == "0P" or cpArray[cpInd][2] == "-1":						
							if cpArray[cpInd][11] == "Above" and cpArray[cpInd][2] != "0" and cpArray[cpInd][2] != "0P":					
								if usestrOrd == True:
									if cpArray[cpInd][2][0:3] == "1.1" or cpArray[cpInd][2][0:3] == "1.5":
										if cpArray[cpInd][7] > strOrdBkt:	
											oldFeat = check_oldFeat(oldFeat)
											return oldFeat
										else:	
											featureID = cpArray[cpInd][1]
											return featureID
									elif cpArray[cpInd][2][0] == "1":		
										if cpArray[cpInd][7] > strOrdBkt and cpArray[cpInd][7] > strOrdInv:	
											oldFeat = check_oldFeat(oldFeat)
											return oldFeat
										else:	
											featureID = cpArray[cpInd][1]
											return featureID
									else:		
										if cpArray[cpInd][7] > strOrdInv:	
											oldFeat = check_oldFeat(oldFeat)
											return oldFeat
										else:	
											featureID = cpArray[cpInd][1]
											return featureID
								else:			
									featureID = cpArray[cpInd][1]								
									return featureID				
							else:					
								oldFeat = check_oldFeat(oldFeat)				
								return oldFeat				
						else:						
							if usepntDis == True:					
								if cpArray[cpInd][5] > pntDis:				
									oldFeat = check_oldFeat(oldFeat)			
									return oldFeat			
								else:				
									if usestrOrd == True:			
										if cpArray[cpInd][2][0:3] == "1.1" or cpArray[cpInd][2][0:3] == "1.5":		
											if cpArray[cpInd][7] > strOrdBkt:	
												oldFeat = check_oldFeat(oldFeat)
												return oldFeat
											else:	
												featureID = cpArray[cpInd][1]
										elif cpArray[cpInd][2][0] == "1":		
											if cpArray[cpInd][7] > strOrdBkt and cpArray[cpInd][7] > strOrdInv:	
												oldFeat = check_oldFeat(oldFeat)
												return oldFeat
											else:	
												featureID = cpArray[cpInd][1]
										else:		
											if cpArray[cpInd][7] > strOrdInv:	
												oldFeat = check_oldFeat(oldFeat)
												return oldFeat
											else:	
												featureID = cpArray[cpInd][1]
									else:			
										featureID = cpArray[cpInd][1]		
							else:					
								if usestrOrd == True:				
									if cpArray[cpInd][2][0:3] == "1.1" or cpArray[cpInd][2][0:3] == "1.5":			
										if cpArray[cpInd][7] > strOrdBkt:		
											oldFeat = check_oldFeat(oldFeat)	
											return oldFeat	
										else:		
											featureID = cpArray[cpInd][1]	
									elif cpArray[cpInd][2][0] == "1":			
										if cpArray[cpInd][7] > strOrdBkt and cpArray[cpInd][7] > strOrdInv:		
											oldFeat = check_oldFeat(oldFeat)	
											return oldFeat	
										else:		
											featureID = cpArray[cpInd][1]	
									else:			
										if cpArray[cpInd][7] > strOrdInv:		
											oldFeat = check_oldFeat(oldFeat)	
											return oldFeat	
										else:		
											featureID = cpArray[cpInd][1]	
								else:				
									featureID = cpArray[cpInd][1]			
												
					except ValueError:							
						featureID = pfArray[pfIndex][2]						
					oldFeat = featureID							
				except ValueError:								
					arcpy.AddMessage("Error indexing Flowline Node Number {0}".format(vaaArray[vaaIndex][5]))							
					tmpFile.write("{0}\t{1}\t{2}\n".format(vaaArray[vaaIndex][5], oldFeat, firstFeat))							
					return firstFeat							
			else:									
				oldFeat = check_oldFeat(oldFeat)								
				return oldFeat								
		except ValueError:										
			arcpy.AddMessage("Error indexing FlowlineVAA comID {0}".format(featureID))									
			return firstFeat									

#Make sure returned feature is a catchment
def check_oldFeat(oldFeat):
	while 1 == 1:
		try:
			cpIndex = cpFeat.index(oldFeat)
			break
		except ValueError:
			vaaIndex = vaaID.index(oldFeat)
			pfIndex = pfNode.index(vaaArray[vaaIndex][1])
			oldFeat = pfArray[pfIndex][1]
	return oldFeat

#Determines catchments in patch moving upstream from most downstream catchment containing salmonids
def moveUpstream(featureID, cumDist):
	try:
		vaaIndex = vaaID.index(featureID)
		get_PFlowUS(vaaArray[vaaIndex][1], featureID, cumDist)
	except ValueError:
		arcpy.AddMessage("Error indexing FlowlineVAA comID {0}".format(featureID))

#gets PlusFlow records matching the PFVAA NodeNumber
def get_PFlowUS(NodeNum, oldFeat, cumDist):
	try:
		pfIndex = pfNode.index(NodeNum)
		tmpFeat = -1
		while pfArray[pfIndex][0] == NodeNum:
			if pfArray[pfIndex][1] > 0 and pfArray[pfIndex][1] != tmpFeat:
				tmpFeat = pfArray[pfIndex][1]
				get_catchPolyUS(pfArray[pfIndex][1], NodeNum, oldFeat, cumDist)
			pfIndex += 1
			if pfIndex == pfCnt:
				break
		
	except ValueError:
		arcpy.AddMessage("Error indexing Flowline Node Number {0}".format(NodeNum))

#gets catchment polygons for catchments upstream of sample point
def get_catchPolyUS(featureID, NodeNum, fromComID, cumDist):
	try:
		cpInd = cpFeat.index(featureID)

		tmpBi = 0
		for catch in catchUsed:
			if catch == cpArray[cpInd][1]:
				tmpBi = 1
				break
		if cpArray[cpInd][2] == "-1":
			tmpBi = 1
		
		if tmpBi == 0:
			if usestrDis == True:
				if cpArray[cpInd][9] > 0:
					cumDist = cpArray[cpInd][9]
				else:
					vaaIndex = vaaID.index(tmpComId)
					cumDist = vaaArray[vaaIndex][3]

				if cumDist > strDis:
					return
				else:
					try:
						comIndex = comArray.index(featureID)
					except ValueError:
						if usepntDis == True:
							#arcpy.AddMessage("Feature: {0}, Distance: {1}".format(cpArray[cpInd][1], cpArray[cpInd][5]))
							if cpArray[cpInd][5] > pntDis:		#Add catchment but don't move upstream
								comArray.append(featureID)
								comCodes.append(cpArray[cpInd][2])
								cpUsed.append(featureID)
								catchUsed.append(cpArray[cpInd][1])
								return
							else:
								comArray.append(featureID)
								comCodes.append(cpArray[cpInd][2])
								cpUsed.append(featureID)
								catchUsed.append(cpArray[cpInd][1])
						else:
							comArray.append(featureID)
							comCodes.append(cpArray[cpInd][2])
							cpUsed.append(featureID)
							catchUsed.append(cpArray[cpInd][1])
			else:
				try:
					comIndex = comArray.index(featureID)
				except ValueError:
					if usepntDis == True:
						if cpArray[cpInd][5] > pntDis:		#Add catchment but don't move upstream
							comArray.append(featureID)
							comCodes.append(cpArray[cpInd][2])
							cpUsed.append(featureID)
							catchUsed.append(cpArray[cpInd][1])
							return
						else:
							comArray.append(featureID)
							comCodes.append(cpArray[cpInd][2])
							cpUsed.append(featureID)
							catchUsed.append(cpArray[cpInd][1])
					else:
						comArray.append(featureID)
						comCodes.append(cpArray[cpInd][2])
						cpUsed.append(featureID)
						catchUsed.append(cpArray[cpInd][1])

			if cpArray[cpInd][6] != "No":
				if cpArray[cpInd][6] == "Yes":
					if cpArray[cpInd][11] == "Above":
						#arcpy.AddMessage("featureID: {0}".format(cpArray[cpInd][1]))
						comArray.pop()
						comCodes.pop()
						cpUsed.pop()
						catchUsed.pop()					
					return
				else:
					try:
						damIndex = damID.index(featureID)

						if usedamDis == True:
							sampFDRNull = str(arcpy.GetCellValue_management(fdrNull, "{0} {1}".format(damArray[damIndex][1], damArray[damIndex][2]), "1").getOutput(0))
							tmpSpot = getNoData(damArray[damIndex][1], damArray[damIndex][2], sampFDRNull)
							tmpdamDist = math.sqrt(math.pow(tmpSpot[0] - damArray[damIndex][1],2) + math.pow(tmpSpot[1] - damArray[damIndex][2],2))

							if tmpdamDist > damDis:
								moveUpstream(featureID, cumDist)
							else:
								return
						else:
							return
					except ValueError:
						moveUpstream(featureID, cumDist)
			else:
				moveUpstream(featureID, cumDist)
	except ValueError:
		moveUpstream(featureID, cumDist)

#get EBTJV_Code and patch composition
def get_composition():
	bkt = 0
	bnt = 0
	rbt = 0
	bktCount = 0
	
	for tmpCode in comCodes:
		if tmpCode == "0.1" or tmpCode == "0.1P":
			bnt = 1
			rbt = 1
		elif tmpCode == "0.2" or tmpCode == "0.2P":
			bnt = 1
		elif tmpCode == "0.3" or tmpCode == "0.3P":
			rbt = 1
		elif tmpCode == "0.4" or tmpCode == "0.4P":
			bnt = 1
			rbt = 1
		elif tmpCode == "0.5" or tmpCode == "0.5P":
			bkt = 1
		elif tmpCode == "1.0" or tmpCode == "1.0P":
			bkt = 1
			bnt = 1
			rbt = 1
		elif tmpCode == "1.1" or tmpCode == "1.1P":
			bkt = 1
		elif tmpCode == "1.2" or tmpCode == "1.2P":
			bkt = 1
			bnt = 1
		elif tmpCode == "1.3" or tmpCode == "1.3P":
			bkt = 1
			rbt = 1
		elif tmpCode == "1.4" or tmpCode == "1.4P":
			bkt = 1
			bnt = 1
			rbt = 1
		elif tmpCode == "1.5" or tmpCode == "1.5P":
			bkt = 1

		if tmpCode[0] == "1":
			bktCount += 1

	bktProp = float(bktCount)/len(comCodes)
	#arcpy.AddMessage("bktProp: {0}, bktCount: {1}, comCodes: {2}".format(bktProp, bktCount, len(comCodes)))

	tmpArray = []
	tmpCnt = []

	for i in comCodes:
		try:
			tmpIndex = tmpArray.index(i)
			tmpCnt[tmpIndex] += 1
		except:
			tmpArray.append(i)
			tmpCnt.append(1)

	a = 0
	for i in tmpArray:
		if a == 0:
			patchComp = "{0} = {1}".format(tmpArray[a], tmpCnt[a])
		else:
			patchComp += "; {0} = {1}".format(tmpArray[a], tmpCnt[a])
		a += 1

	if bkt == 1 and bnt == 1 and rbt == 1:
		return "1.4", patchComp, bktProp
	elif bkt == 1 and rbt == 1:
		return "1.3", patchComp, bktProp
	elif bkt == 1 and bnt == 1:
		return "1.2", patchComp, bktProp
	elif bkt == 1:
		return "1.1", patchComp, bktProp
	elif bnt == 1 and rbt == 1:
		return "0.4", patchComp, bktProp
	elif rbt == 1:
		return "0.3", patchComp, bktProp
	elif bnt == 1:
		return "0.2", patchComp, bktProp

#*****Beginning of algorithm*****

catchPoly = arcpy.GetParameterAsText(0)
streams = arcpy.GetParameterAsText(1)
dams = arcpy.GetParameterAsText(2)
fdrNull = arcpy.GetParameterAsText(3)
plusFlowVAA = arcpy.GetParameterAsText(4)
plusFlow = arcpy.GetParameterAsText(5)
outName = arcpy.GetParameterAsText(6)
usepntDis = arcpy.GetParameter(7)
pntDis = long(arcpy.GetParameterAsText(8))
usestrOrd = arcpy.GetParameter(9)
strOrdBkt = long(arcpy.GetParameterAsText(10))
strOrdInv = long(arcpy.GetParameterAsText(11))
usestrDis = arcpy.GetParameter(12)
strDis = float(arcpy.GetParameterAsText(13))
usedamDis = arcpy.GetParameter(14)
damDis = float(arcpy.GetParameterAsText(15))

tmpDescribe = arcpy.Describe(catchPoly)
tmpPath = "{0}".format(tmpDescribe.dataElement.catalogPath)
a = tmpPath.rindex("\\")
outPath = tmpPath[:a]

tmpFile = open("{0}/Patch Error Log.txt".format(outPath), "w")
tmpFile.write("Node\toldFeat\tfirstFeat\n")

#Write parameters to file
tmpParam = open("{0}/Patch Parameter Settings.txt".format(outPath), "w")
tmpParam.write("Catchment Feature Layer: {0}\n".format(catchPoly))
tmpParam.write("Flowline Feature Layer: {0}\n".format(streams))
tmpParam.write("Barrier Feature Layer: {0}\n".format(dams))
tmpParam.write("Flow Direction Null Raster Layer: {0}\n".format(fdrNull))
tmpParam.write("PlusFlowlineVAA Table: {0}\n".format(plusFlowVAA))
tmpParam.write("PlusFlow Table: {0}\n".format(plusFlow))
tmpParam.write("Output Base File Name: {0}\n".format(outName))
tmpParam.write("Use Max Sample Point Distance: {0}\n".format(usepntDis))
if usepntDis == True:
	tmpParam.write("Max Sample Point Distance (m): {0}\n".format(pntDis))
tmpParam.write("Use Max Stream Distance: {0}\n".format(usestrDis))
if usestrDis == True:
	tmpParam.write("Max Stream Distance (km): {0}\n".format(strDis))
tmpParam.write("Use Max Barrier Distance: {0}\n".format(usedamDis))
if usedamDis == True:
	tmpParam.write("Max Barrier Point Distance (m): {0}\n".format(damDis))
tmpParam.write("Use Max Stream Order: {0}\n".format(usestrOrd))
if usestrOrd == True:
	tmpParam.write("Max Stream Order Brook Trout: {0}\n".format(strOrdBkt))
	tmpParam.write("Max Stream Order Brown & Rainbow Trout: {0}\n".format(strOrdInv))
tmpParam.close()

a = outName.rindex("\\")
outPath = outName[:a]
outFile = outName[a+1:]

CRSR = arcpy.Describe(catchPoly)

cpFields = ["GRIDCODE", "FEATUREID", "EBTJV_Code", "Catch_Cnt", "Samp_Year", "Samp_Dist", "Dam", "Str_Order", "Comment", "Cum_Length", "Samp_OID", "Samp_Loc"]
streamFields = ["COMID", "SHAPE@"]
VAAFields = ["COMID", "FromNode", "STREAMORDE", "LengthKM", "FCODE", "ToNode"]
damFields = ["FEATUREID", "SHAPE@X", "SHAPE@Y"]
PFlowFields = ["NodeNumber", "FromComId", "ToComId"]
catchFields = ["Str_Order", "FEATUREID", "Catch_Cnt", "Samp_Loc", "Samp_Dist"]

#read catchPoly records into array
arcpy.AddMessage("Reading Catchment records into array...")
cpCnt = long(arcpy.GetCount_management(catchPoly).getOutput(0))
cpFeat = [0 for j in range(cpCnt)]
cpArray = [[0 for j in range(9)] for i in range(cpCnt)]
cpRecords = arcpy.da.UpdateCursor(catchPoly, cpFields)
i = 0
for cpRow in cpRecords:	
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

#Create new patch feature layer
arcpy.CreateFeatureclass_management(outPath, outFile, "POLYGON", "", "DISABLED", "DISABLED", CRSR.SpatialReference)
arcpy.AddField_management(outName, "Feat_ID", "DOUBLE")
arcpy.AddField_management(outName, "EBTJV_Code", "TEXT")
arcpy.AddField_management(outName, "Num_Catch", "LONG")
arcpy.AddField_management(outName, "Area_HA", "DOUBLE")
arcpy.AddField_management(outName, "Patch_Comp", "TEXT")
arcpy.AddField_management(outName, "Prop_BKT", "DOUBLE")
arcpy.DeleteField_management(outName, "Id")

patchFields = ["SHAPE@", "Feat_ID", "EBTJV_Code", "Num_Catch", "Patch_Comp", "Prop_BKT"]
patchRecords = arcpy.da.InsertCursor(outName, patchFields)

catchRecords = arcpy.da.SearchCursor(catchPoly, catchFields, '"Str_Order" > 0')
#catchRecords = arcpy.da.SearchCursor(catchPoly, catchFields, '"Catch_Cnt" =1')
#catchRecords = arcpy.da.SearchCursor(catchPoly, catchFields, '"FEATUREID" = 6731463')

cpUsed = []
q = 0

for catchRow in sorted(catchRecords, key=lambda k: (k[0], -k[2]), reverse=True):
	q += 1
	arcpy.AddMessage("Record {0}, Feature ID = {1}, Stream Order = {2}, catchCnt = {3}".format(q, catchRow[1], catchRow[0], catchRow[2]))
	tmpComId = 0
	tmpBi = 0
	comArray = []
	comCodes = []
	catchUsed = []
	whereClause = ""

	#Determine if catchment has already been assigned to a patch
	try:
		#If successful then catchment has already been used
		usedIndex = cpUsed.index(catchRow[1])

	except ValueError:
		comArray.append(catchRow[1])
		cpUsed.append(catchRow[1])
		cpIndex = cpFeat.index(catchRow[1])
		comCodes.append(cpArray[cpIndex][2])

		if catchRow[3] == "Above":
			tmpComId = catchRow[1]
		elif usepntDis == True:
			if catchRow[4] > pntDis:
				tmpComId = catchRow[1]
			else:
				tmpComId = moveDownstream(catchRow[1])
		else:
			tmpComId = moveDownstream(catchRow[1])

		#arcpy.AddMessage("catchRow: {0}, tmpComId: {1}".format(catchRow[1], tmpComId))
		cpIndex = cpFeat.index(tmpComId)

		if usestrDis == True:
			if cpArray[cpIndex][9] > 0:
				cumDist = cpArray[cpIndex][9]
			else:
				vaaIndex = vaaID.index(tmpComId)
				cumDist = vaaArray[vaaIndex][3]

			if cumDist < strDis:
				try:
					comIndex = comArray.index(tmpComId)
				except ValueError:
					comArray.append(tmpComId)
					cpUsed.append(tmpComId)
					comCodes.append(cpArray[cpIndex][2])
			else:
				tmpBi = 1
		else:
			cumDist = 0
			try:
				comIndex = comArray.index(tmpComId)
			except ValueError:
				comArray.append(tmpComId)
				cpUsed.append(tmpComId)
				comCodes.append(cpArray[cpIndex][2])

		if cpArray[cpIndex][2] != "0" and cpArray[cpIndex][2] != "0P" and tmpBi == 0:
			if  cpArray[cpIndex][6] != "Yes" or cpArray[cpIndex][11] != "Below":
				if usestrOrd == True:
					if cpArray[cpIndex][2][0:3] == "1.1" or cpArray[cpIndex][2][0:3] == "1.5":
						if cpArray[cpIndex][7] <= strOrdBkt:
							if usepntDis == True:
								if cpArray[cpIndex][5] < pntDis:
									moveUpstream(tmpComId, cumDist)
							else:
								moveUpstream(tmpComId, cumDist)
					elif cpArray[cpIndex][2][0] == "1":
						if cpArray[cpIndex][7] <= strOrdBkt or cpArray[cpIndex][7] <= strOrdInv:
							if usepntDis == True:
								if cpArray[cpIndex][5] < pntDis:
									moveUpstream(tmpComId, cumDist)
							else:
								moveUpstream(tmpComId, cumDist)
					else:
						if cpArray[cpIndex][7] <= strOrdInv:
							if usepntDis == True:
								if cpArray[cpIndex][5] < pntDis:
									moveUpstream(tmpComId, cumDist)
							else:
								moveUpstream(tmpComId, cumDist)
				else:
					if usepntDis == True:
						if cpArray[cpIndex][5] < pntDis:
							moveUpstream(tmpComId, cumDist)
						else:
							moveUpstream(tmpComId, cumDist)
					else:
						moveUpstream(tmpComId, cumDist)
		
			#Select catchments by FeatureID and export them to a new layer
			a = 0
			for i in comArray:
				if a == 0:
					whereClause = '"FEATUREID" = {0}'.format(comArray[a])
				else:
					whereClause += ' or "FEATUREID" = {0}'.format(comArray[a])
				a += 1

			#arcpy.AddMessage("whereClause: {0}".format(whereClause))
			tmpSelect = "{0}\\tmpSelect.shp".format(outPath)
			tmpDissolve = "{0}\\tmpDissolve.shp".format(outPath)

			arcpy.Select_analysis(catchPoly, tmpSelect, '{0}'.format(whereClause))
			arcpy.Dissolve_management(tmpSelect, tmpDissolve, ["SOURCEFC"], "", "MULTI_PART")

			patchCode, patchComp, bktProp = get_composition()

			dissolveRecords = arcpy.da.SearchCursor(tmpDissolve, ["SHAPE@"], "", CRSR.spatialReference)
			for dissolveRow in dissolveRecords:
				patchRecords.insertRow((dissolveRow[0], tmpComId, patchCode, len(comArray), patchComp, bktProp))

#Calculate patch area
arcpy.AddMessage("Calculating patch area...")
arcpy.CalculateField_management(outName, "Area_HA", "!SHAPE.AREA@HECTARES!", "PYTHON_9.3")

try:
	arcpy.Delete_management(tmpSelect)
except:
	i = 0 #Just need an except, doesn't mean anything
try:
	arcpy.Delete_management(tmpDissolve)
except:
	i = 0 #Just need an except, doesn't mean anything

#Remove partial patches
arcpy.AddMessage("Verifying patches...")

patchFields = ["Area_HA", "Feat_ID", "SHAPE@", "FID"]

patchCnt = long(arcpy.GetCount_management(outName).getOutput(0))
patchFeat = [0 for j in range(patchCnt)]
patchArray = [[0 for j in range(9)] for i in range(patchCnt)]
patchRecords = arcpy.da.SearchCursor(outName, patchFields)
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

dupsFID.sort(reverse=True)

for dup in dupsFID:
	delete = arcpy.da.UpdateCursor(outName, ["FID", "Feat_ID"], '"FID" = {0}'.format(dup))
	for rows in delete:
		arcpy.AddMessage("Deleting FeatureID {0}, FID {1}".format(rows[1], rows[0]))
		delete.deleteRow()

#Create layers for each salmonid species
arcpy.AddMessage("Making patch layer for each salmonid species...")

a = outFile.index(".")

tmpStr = "{0}_BKT.shp".format(outFile[:a])
tmpOutput = "{0}\\{1}".format(outPath, tmpStr)
whereClause = '"EBTJV_Code" = ' + "'1.1' or " + '"EBTJV_Code" = ' + "'1.2' or " + '"EBTJV_Code" = ' + "'1.3' or " + '"EBTJV_Code" = ' + "'1.4'" 
arcpy.Select_analysis(outName, tmpOutput, '{0}'.format(whereClause))

tmpStr = "{0}_BNT.shp".format(outFile[:a])
tmpOutput = "{0}\\{1}".format(outPath, tmpStr)
whereClause = '"EBTJV_Code" = ' + "'0.2' or " + '"EBTJV_Code" = ' + "'0.4' or " + '"EBTJV_Code" = ' + "'1.2' or " + '"EBTJV_Code" = ' + "'1.4'" 
arcpy.Select_analysis(outName, tmpOutput, '{0}'.format(whereClause))

tmpStr = "{0}_RBT.shp".format(outFile[:a])
tmpOutput = "{0}\\{1}".format(outPath, tmpStr)
whereClause = '"EBTJV_Code" = ' + "'0.3' or " + '"EBTJV_Code" = ' + "'0.4' or " + '"EBTJV_Code" = ' + "'1.3' or " + '"EBTJV_Code" = ' + "'1.4'" 
arcpy.Select_analysis(outName, tmpOutput, '{0}'.format(whereClause))

tmpFile.close()
