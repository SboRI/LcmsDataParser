import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
# CONFIG
###############################################################################

# LC Data File
lcDataFile = {'filename': "testdata.txt", 'sep': ';', 'decimal': ','}

# nameList
nameList = {'filename': "namelist_all.csv", 'sep': ';', 'decimal': ','}

importantAcids = ["Crotonate","Acetate","Propionate","3- Hydroxybutyrate","Methylsuccinate","Ethylmalonate","Mesaconate","2-Hydroxy-3-Methylsuccinate","Succinate","Methylmalonate"]
dataRows = ["Data Filename", "Sample Name", "Sample ID"]
rowsToKeep = dataRows + importantAcids

# How many strains should be shown in the "best of" list
noOfBestHits = 20


###############################################################################

# Methods
# -----------------------------------------------------------------
def removePathAndExtension(filename: str) -> str:
    return filename.strip().split("\\")[-1].replace(".lcd", "")


# -----------------------------------------------------------------

# Programm
# ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#replace decimal comma by decimal point, remove thousand point, set '----' to 0
with open(lcDataFile['filename'], 'r') as dataFile:
    with open("cleanDataFile.txt", 'w') as outfile:
        for num, line in enumerate(dataFile):
            lineArray = line.split(lcDataFile['sep'])
            if num>0:
                for num, el in enumerate(lineArray):
                    if num>0:
                        lineArray[num] = el.replace('.', '').replace(',', '.').replace('-----', '')
            transformedLine = lcDataFile['sep'].join(lineArray)
            outfile.write(transformedLine)