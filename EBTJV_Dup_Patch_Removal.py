import arcpy
import os
import sys
import operator
import time
import math

def get_composition():
	bkt = 0
	bnt = 0
	rbt = 0
	bktCount = 0
	
	for tmpCode in comCodes:
		#arcpy.AddMessage("{0}".format(tmpCode))
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
patches = arcpy.GetParameterAsText(1)

tmpDescribe = arcpy.Describe(patches)
tmpPath = "{0}".format(tmpDescribe.catalogPath)
a = tmpPath.rindex("\\")
outPath = tmpPath[:a]

#Write parameters to file
tmpParam = open("{0}/Duplicate Patch Removal Parameter Settings.txt".format(outPath), "a")
tmpParam.write("{0}\n".format(time.strftime("%m-%d-%Y %H:%M:%S")))
tmpParam.write("Catchment Feature Layer: {0}\n".format(catchPoly))
tmpParam.write("Patch Feature Layer: {0}\n".format(patches))
tmpParam.write("\n")
tmpParam.close()

CRSR = arcpy.Describe(patches)

catchFields = ["FEATUREID", "EBTJV_Code", "Samp_year", "Samp_OID", "Catch_Cnt", "Cum_Length", "Str_Order", "Dam", "Samp_Loc"]
#patchFields = ["Feat_ID", "SHAPE@"]
patchFields = ["SHAPE@", "Feat_ID", "EBTJV_Code", "Num_Catch", "Area_HA", "Patch_Comp", "Prop_BKT"]

#Copy patch layer
arcpy.AddMessage("Copying patch layer...")
tmpPatch = "{0}/tmpPatches.shp".format(outPath)
arcpy.CopyFeatures_management(patches, tmpPatch)
arcpy.MakeFeatureLayer_management(tmpPatch, "tmpPatches")

#Run a spatial join between catchments and patches to find cathments belonging to multiple patches
arcpy.AddMessage("Running spatial join...")
catch_SJ = arcpy.SpatialJoin_analysis(catchPoly, patches, "{0}/Patch_Dups.shp".format(outPath), "JOIN_ONE_TO_ONE", "KEEP_COMMON", "#", "WITHIN")

#Select cathments occurring in multiple patches
arcpy.AddMessage("Selecting catchments with multiple joins...")
arcpy.MakeFeatureLayer_management(catch_SJ, "catch_SJ_layer")
arcpy.SelectLayerByAttribute_management("catch_SJ_layer", "NEW_SELECTION", ' "Join_Count" > 1 ')

#Use the above catchments to select associated patches
arcpy.AddMessage("Selecting patches containing catchments with multiple joins...")
arcpy.SelectLayerByLocation_management("tmpPatches", "CONTAINS", "catch_SJ_layer")

#Use the selected patches to find intersecting ones and then dissolve them
arcpy.AddMessage("Resolving erroneous patches...")
patchRecs = arcpy.da.SearchCursor("tmpPatches", ["Area_HA", "Feat_ID", "SHAPE@"])
patchUpdateRecs = arcpy.da.InsertCursor(patches, patchFields)

usedPatches = []
tmpSelect = "{0}/tmpSelect.shp".format(outPath)
tmpDissolve = "{0}/tmpDissolve.shp".format(outPath)

for row in sorted(patchRecs, reverse=True):
	try:
		i = usedPatches.index(row[1])
	except:
		patchID = [row[1]]
		usedPatches.append(row[1])
		patchRecs2 = arcpy.da.SearchCursor("tmpPatches", ["Area_HA", "Feat_ID", "SHAPE@"])
		for row2 in sorted(patchRecs2, reverse=True):
			if row2[1] != row[1]:
				if row2[2].overlaps(row[2]):
					arcpy.AddMessage("{0} overlaps {1}".format(row2[1], row[1]))
					patchID.append(row2[1])
					usedPatches.append(row2[1])
			
		#Export catchments to new shapefile
		i = 0
		for id in patchID:
			if i == 0:
				tmpClause = '"Feat_ID" = {0}'.format(id)
			else:
				tmpClause += ' or "Feat_ID" = {0}'.format(id)
			i += 1
		
		#Make a new layer from the overlapping patches
		arcpy.AddMessage("Unresolved Patches: {0}".format(tmpClause))
		arcpy.Select_analysis("tmpPatches", tmpSelect, tmpClause)

		#Dissolve overlapping patches into one feature
		arcpy.Dissolve_management(tmpSelect, tmpDissolve)
		arcpy.AddField_management(tmpDissolve, "Area_HA", "DOUBLE")
		arcpy.CalculateField_management(tmpDissolve, "Area_HA", "!SHAPE.AREA@HECTARES!", "PYTHON_9.3")

		patchArea = arcpy.da.SearchCursor(tmpDissolve, ["Area_HA"], "", CRSR.spatialReference)
		for areaRecs in patchArea:
			tmpArea = areaRecs[0]

		#Use patches to select catchments
		arcpy.SelectLayerByLocation_management(catchPoly, "WITHIN", tmpDissolve)

		#Get EBTJV_Codes of selected catchments
		catchRecs = arcpy.da.SearchCursor(catchPoly, catchFields)
		comCodes = []
		for rec in catchRecs:
			comCodes.append(str(rec[1]))
		
		#Get composition of selected catchments
		patchCode, patchComp, bktProp = get_composition()

		#Delete erroneous patches
		arcpy.SelectLayerByAttribute_management(patches, "NEW_SELECTION", tmpClause)
		#arcpy.SelectLayerByLocation_management("tmpPatches", "CONTAINS", "catch_SJ_layer")
		arcpy.DeleteFeatures_management(patches)

		#Insert new patch into patch layer
		dissolveRecords = arcpy.da.SearchCursor(tmpDissolve, ["SHAPE@"], "", CRSR.spatialReference)
		for dissolveRow in dissolveRecords:
			patchUpdateRecs.insertRow((dissolveRow[0], patchID[0], patchCode, len(comCodes), tmpArea, patchComp, bktProp))


#Clear select catchments
arcpy.SelectLayerByAttribute_management(catchPoly, "CLEAR_SELECTION")

try:
	arcpy.Delete_management(tmpSelect)
except:
	i = 0 #Just need an except, doesn't mean anything
try:
	arcpy.Delete_management(tmpDissolve)
except:
	i = 0 #Just need an except, doesn't mean anything
