import pandas as pd
import numpy as np

lcDataFile = "Testdaten.txt"
nameList = "namelist2.csv"
importantAcids = ["Methylsuccinat / Ethylmalonat","2H-3-Methylsuccinat","Crotonat","Mesaconat","Methylmalonat / Succinat","3-Hydroxybutyrat"]
dataRows = ["Data Filename", "Sample Name", "Sample ID"]
rowsToKeep =  dataRows + importantAcids

# move to variables 
pdLcData = pd.read_csv(lcDataFile, sep=",")[rowsToKeep] 

for column in importantAcids:
    pdLcData[column] = pdLcData[column].apply(pd.to_numeric, errors = "coerce")

pdNameList =  pd.read_csv(nameList, sep=";")

pdNamedLcData = pd.merge(pdLcData, pdNameList, left_on="Data Filename", right_on="Nr", how="left")
print(pdNamedLcData)