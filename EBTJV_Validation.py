import arcpy
import os
import sys
import operator
import time
import math

#Translate species occurrence into EBTJV Code
def getCode(specPres):
	species = specPres.split(",")
	if species[0] == "0":
		specCode = "0"
	else:
		specCode = "1"

	if species[1] == "0":
		specCode += ",0"
	else:
		specCode += ",1"

	if species[2] == "0":
		specCode += ",0"
	else:
		specCode += ",1"
	
	
	if specCode == "0,0,0":
		return "0"
	elif specCode == "0,1,0":
		return "0.2"
	elif specCode == "0,0,1":
		return "0.3"
	elif specCode == "0,1,1":
		return "0.4"
	elif specCode == "1,0,0":
		return "1.1"
	elif specCode == "1,1,0":
		return "1.2"
	elif specCode == "1,0,1":
		return "1.3"
	elif specCode == "1,1,1":
		return "1.4"
	else:
		arcpy.AddMessage("No case for code {0}".format(specCode))


#*****Beginning of algorithm*****

catchPoly = arcpy.GetParameterAsText(0)
plusFlowVAA = arcpy.GetParameterAsText(1)
dams = arcpy.GetParameterAsText(2)
edits = arcpy.GetParameterAsText(3)
infer = arcpy.GetParameter(4)
outName = arcpy.GetParameterAsText(5)

tmpDescribe = arcpy.Describe(catchPoly)
tmpPath = "{0}".format(tmpDescribe.catalogPath)
a = tmpPath.rindex("\\")
outPath = tmpPath[:a]

#Write parameters to file
tmpParam = open("{0}/Catchment Validation Parameter Settings.txt".format(outPath), "w")
tmpParam.write("{0}".format(time.strftime("%m-%d-%Y %H:%M:%S")))
tmpParam.write("Catchment Feature Layer: {0}\n".format(catchPoly))
tmpParam.write("FlowlineVAA Table: {0}\n".format(plusFlowVAA))
tmpParam.write("Barrier Feature Layer: {0}\n".format(dams))
tmpParam.write("Edits Table: {0}\n".format(edits))
tmpParam.write("Infer upstream for catchment edits: {0}".format(infer))
tmpParam.write("Output File Name: {0}\n".format(outName))
tmpParam.close()

a = outName.rindex("\\")
outPath = outName[:a]
outFile = outName[a+1:]

arcpy.AddMessage("Copying catchment file to make edits on...")
arcpy.CopyFeatures_management(catchPoly, outName)

tmpBi = 0
fieldList = arcpy.ListFields(outName)
for field in fieldList:
	if field.name == "val_change":
		tmpBi = 1
		break

if tmpBi == 0:
	arcpy.AddMessage("Adding validation fields to output file...")
	arcpy.AddField_management(outName, "val_change", "TEXT")
	arcpy.AddField_management(outName, "val_reason", "TEXT")

CRSR = arcpy.Describe(outName)

valFields = ["FEATUREID", "EBTJV_Code", "Samp_year", "Samp_OID", "val_change", "val_reason", "Catch_Cnt", "Cum_Length", "Str_Order", "Dam", "Samp_Loc"]
VAAFields = ["COMID", "FromNode", "STREAMORDE", "LengthKM", "FCODE", "ToNode"]
damFields = ["FEATUREID", "SHAPE@X", "SHAPE@Y"]
editFields = ["CLASS", "FEATUREID", "CODE_OLD", "CODE_NEW", "COMMENT"]

#read catchPoly records into array
arcpy.AddMessage("Reading catchment records into array...")
valCnt = long(arcpy.GetCount_management(outName).getOutput(0))
valFeat = [0 for j in range(valCnt)]
valSamp = [0 for j in range(valCnt)]
valArray = [[0 for j in range(9)] for i in range(valCnt)]
valRecords = arcpy.da.UpdateCursor(outName, valFields)
i = 0
for valRow in valRecords:	
	valFeat[i] = valRow[1]
	valArray[i] = valRow
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

#read Edits records into array
arcpy.AddMessage("Reading edit records into array...")
editCnt = long(arcpy.GetCount_management(edits).getOutput(0))
editArray = [[0 for j in range(3)] for i in range(editCnt)]
editID = [0 for j in range(editCnt)]
editRecords = arcpy.da.SearchCursor(edits, editFields)
i = 0
for editRow in editRecords:
	editID[i] = editRow[0]
	editArray[i] = editRow
	i += 1

arcpy.AddMessage("{0} edit records".format(editCnt))

fields = arcpy.ListFields(outName)

for i in fields:
	if i.name == "Samp_OID":
		dType = i.type

editRecords = arcpy.da.SearchCursor(edits, editFields)

i = 0
for editRow in sorted(editRecords, reverse=True):
	i += 1
	arcpy.AddMessage("Record: {0}, feature ID: {1}".format(i, editRow[1]))
	if editRow[0] == "sample":
		tmpSamp = str(int(editRow[1]))
		tmpSQL = '"SAMP_OID" LIKE {0}{1};%{2} OR "SAMP_OID" LIKE {0}%; {1};%{2} OR "SAMP_OID" LIKE {0}%; {1}{2} OR "SAMP_OID" LIKE {0}{1}{2}'.format("'", tmpSamp, "'")
		if dType == "String":
			arcpy.AddMessage(tmpSQL)
			valRecords = arcpy.da.UpdateCursor(outName, valFields, tmpSQL)
			#valRecords = arcpy.da.UpdateCursor(outName, valFields, '"Samp_OID" LIKE {0}%{1}%{2}'.format("'", tmpSamp, "'")	)
		else:
			valRecords = arcpy.da.UpdateCursor(outName, valFields, '"Samp_OID" = {0}'.format(tmpSamp))
			
		tmpCnt = 0
		for valRow in valRecords:
			tmpCnt += 1
			if valRow[4][:7] == "Changed":
				tmpChar = valRow[4].rfind(' ')
				oldCode = valRow[4][tmpChar+1:]
			else:
				oldCode = valRow[1]
			newCode = getCode(editRow[3])
			valRow[1] = newCode
			valRow[4] = "Changed from {0}".format(oldCode)
			valRow[5] = editRow[4]

			valRecords.updateRow(valRow)
		if tmpCnt == 0:
			arcpy.AddMessage("No match for sample edit {0}".format(editRow[1]))
		else:
			arcpy.AddMessage("tmpCnt: {0}".format(tmpCnt))

	elif editRow[0] == "catchment":
		tmpCatch = editRow[1]
		valRecords = arcpy.da.UpdateCursor(outName, valFields, '"FEATUREID" = {0}'.format(tmpCatch))
		tmpCnt = 0
		for valRow in valRecords:
			tmpCnt += 1
			if valRow[4][:7] == "Changed":
				tmpChar = valRow[4].rfind(' ')
				oldCode = valRow[4][tmpChar+1:]
			else:
				oldCode = valRow[1]
			valRow[1] = editRow[3]
			valRow[4] = "Changed from {0}".format(oldCode)
			valRow[5] = editRow[4]
			tmpSamp = valRow[3]

			if oldCode == "-1":
				valRow[6] = 1
				#arcpy.AddMessage("Updated catch_cnt for catchment {0}".format(tmpCatch))

				vaaIndex = vaaID.index(tmpCatch)
				valRow[7] = vaaArray[vaaIndex][3]
				if vaaArray[vaaIndex][2] > 0:
					valRow[8] = vaaArray[vaaIndex][2]
				else:
					valRow[8] = 1

				try:
					damIndex = damID.index(tmpCatch)
					valRow[9] = "Yes"
					valRow[10] = "Below"
				except ValueError:
					arcpy.AddMessage("No barrier for catchment {0}".format(tmpCatch))

			tmpCatchCnt = valRow[6]
			valRecords.updateRow(valRow)
		if tmpCnt == 0:
			arcpy.AddMessage("No match for catchment edit {0}".format(editRow[1]))
		else:
			arcpy.AddMessage("tmpCnt: {0}".format(tmpCnt))
			if infer == True:
				if dType == "String":
					valRecords = arcpy.da.UpdateCursor(outName, valFields, '"Samp_OID" = {0}{1}{2} AND {3}Catch_Cnt{4} > {5}'.format("'", tmpSamp, "'", '"', '"', tmpCatchCnt))
				else:
					valRecords = arcpy.da.UpdateCursor(outName, valFields, '"Samp_OID" = {0} AND "Catch_Cnt" > {1}'.format(tmpSamp, tmpCatchCnt))

				tmpCnt = 0
				for valRow in valRecords:
					tmpCnt += 1
					#if valRow[4] == "":
					valRow[1] = editRow[3]
					valRow[4] = "Changed from {0}".format(oldCode)
					valRow[5] = editRow[4]
					valRecords.updateRow(valRow)
				arcpy.AddMessage("tmpCnt: {0}".format(tmpCnt))

#valFields = ["FEATUREID", "EBTJV_Code", "Catch_Cnt", "Samp_OID", "val_change", "val_reason", "Catch_Cnt"]
#editFields = ["CLASS", "ID", "CODE_OLD", "CODE_NEW", "COMMENT"]
