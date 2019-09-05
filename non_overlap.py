import arcpy

#*****Beginning of algorithm*****

catchPoly = arcpy.GetParameterAsText(0)

arcpy.SelectLayerByAttribute_management("test_subset", "NEW_SELECTION")

tmpRecs = arcpy.da.SearchCursor(catchPoly, ['OID@', 'SHAPE@'])

tmpList = []

for row in tmpRecs:
	tmpRecs2 = arcpy.da.SearchCursor(catchPoly, ['OID@', 'SHAPE@'])
	for row2 in tmpRecs2:
		if row2[0] != row[0]:
			if row2[1].overlaps(row[1]):
				tmpList.append(row2[0])
				#arcpy.AddMessage("{0}".format(row2[0]))

whereClause = ""

a = 0
for id in tmpList:
	if a == 0:
		whereClause = '"FID" = {0}'.format(id)
	else:
		whereClause += ' or "FID" = {0}'.format(id)
	a += 1

arcpy.SelectLayerByAttribute_management("test_subset", "REMOVE_FROM_SELECTION", whereClause)
