import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def removePathAndExtension(filename: str) -> str:
    return filename.strip().split("\\")[-1].replace(".lcd", "")

lcDataFile = "Testdaten.txt"
nameList = "namelist.csv"
importantAcids = ["Methylsuccinat / Ethylmalonat","2H-3-Methylsuccinat","Crotonat","Mesaconat","Methylmalonat / Succinat","3-Hydroxybutyrat"]
dataRows = ["Data Filename", "Sample Name", "Sample ID"]
rowsToKeep =  dataRows + importantAcids

# Read LC Data 
# TODO: move to variables 
pdLcData = pd.read_csv(lcDataFile, sep=",")[rowsToKeep] 

# Convert Concentrations to numeric values
for column in importantAcids:
    pdLcData[column] = pdLcData[column].apply(pd.to_numeric, errors = "coerce")

#Convert "Data Filename" column to number (corresponding Nr expected in nameList variable)
pdLcData["Data Filename"] = [removePathAndExtension(filename) for filename in pdLcData["Data Filename"]]

#Read nameList
pdNameList =  pd.read_csv(nameList, sep=";", dtype={"Nr":"str"})

# Convert numbers to clear names by merging LC Data file and nameList 
pdNamedLcData = pd.merge(pdLcData, pdNameList, left_on="Data Filename", right_on="Nr")

# Group Replicates based on Name and timepoint, calculate mean, std, number 
grouped = pdNamedLcData.groupby(['Name', 'Zeitpunkt'])
meanDev=grouped.agg({x :["mean", "std","count"] for x in importantAcids})


# Split Results for each acid given in importantAcids
perAcid = {acid: meanDev[acid].sort_values('mean', ascending=False) for acid in importantAcids}


# For each acid in importantAcids
for acid in perAcid:
    # sort concentration in descening order. Take best 10.
    perAcid[acid] = perAcid[acid].reset_index().head(10)
    perAcid[acid] = perAcid[acid].loc[perAcid[acid]['mean'] > 0]
    #print()

    #Dataframe for saving sum of acids
    sumOfAcids = pd.DataFrame()
    #get the sum of all acids for this sample and timepoint
    for index, row in perAcid[acid].iterrows():
        allAcid = meanDev.loc[(row['Name'], row["Zeitpunkt"])].xs('mean', level=1).sum()
        allAcidDf = pd.DataFrame({'Name': [row['Name']], "Zeitpunkt": [row["Zeitpunkt"]], 'sumOfAcids': [allAcid]})
        sumOfAcids=sumOfAcids.append(allAcidDf)

    perAcid[acid] = perAcid[acid].merge(sumOfAcids, on=['Name', 'Zeitpunkt'])
    perAcid[acid]['ratio'] = perAcid[acid]['mean']/perAcid[acid]['sumOfAcids']
    
    ax=perAcid[acid][['Name', 'mean', 'ratio']].set_index('Name').plot(kind='bar', secondary_y=["ratio"], title=acid)
    ax.set_ylabel("Concentration")
    ax.right_ax.set_ylabel("Ratio")
    ax.right_ax.set_ylim((0,1))

    plt.savefig(acid.replace("/", "")+"_figure"+".pdf")
    print(acid)
    print(perAcid[acid])