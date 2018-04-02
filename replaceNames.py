import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#CONFIG
###############################################################################

#LC Data File
lcDataFile = {'filename':"Testdaten.txt", 'sep':',', 'decimal':'.'}

#nameList
nameList = {'filename':"namelist.csv", 'sep':';', 'decimal':'.'}


importantAcids = ["Methylsuccinat / Ethylmalonat","2H-3-Methylsuccinat","Crotonat","Mesaconat","Methylmalonat / Succinat","3-Hydroxybutyrat"]
dataRows = ["Data Filename", "Sample Name", "Sample ID"]
rowsToKeep =  dataRows + importantAcids

###############################################################################

#Methods
#-----------------------------------------------------------------
def removePathAndExtension(filename: str) -> str:
    return filename.strip().split("\\")[-1].replace(".lcd", "")


#-----------------------------------------------------------------

#Programm
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# Read LC Data 
pdLcData = pd.read_csv(lcDataFile['filename'], sep=lcDataFile['sep'], decimal=lcDataFile['decimal'])[rowsToKeep] 

# Convert Concentrations to numeric values
for column in importantAcids:
    pdLcData[column] = pdLcData[column].apply(pd.to_numeric, errors = "coerce")

#Convert "Data Filename" column to number (corresponding Nr expected in nameList variable)
pdLcData["Data Filename"] = [removePathAndExtension(filename) for filename in pdLcData["Data Filename"]]

#Read nameList
pdNameList =  pd.read_csv(nameList['filename'], sep=nameList['sep'], decimal=nameList['decimal'], dtype={"Nr":"str"})

# Convert numbers to clear names by merging LC Data file and nameList 
pdNamedLcData = pd.merge(pdLcData, pdNameList, left_on="Data Filename", right_on="Nr")

# Group Replicates based on Name and timepoint, calculate mean, std, number 
grouped = pdNamedLcData.groupby(['Name', 'Zeitpunkt'])
meanDev=grouped.agg({x :["mean", "std","count"] for x in importantAcids})


# Split Results for each acid given in importantAcids
perAcid = {acid: meanDev[acid].sort_values('mean', ascending=False) for acid in importantAcids}


# For each acid in importantAcids
for acid in perAcid:
    # sort concentration in descening order. Take best 10. remove negative concentrations
    perAcid[acid] = perAcid[acid].reset_index().head(10)
    perAcid[acid] = perAcid[acid].loc[perAcid[acid]['mean'] > 0]

    #Dataframe for saving sum of acids
    sumOfAcids = pd.DataFrame()

    #get the sum of all acids for this sample and timepoint
    for index, row in perAcid[acid].iterrows():
        allAcid = meanDev.loc[(row['Name'], row["Zeitpunkt"])].xs('mean', level=1).sum()
        allAcidDf = pd.DataFrame({'Name': [row['Name']], "Zeitpunkt": [row["Zeitpunkt"]], 'sumOfAcids': [allAcid]})
        sumOfAcids=sumOfAcids.append(allAcidDf)

    # add sum of all acids to result table
    perAcid[acid] = perAcid[acid].merge(sumOfAcids, on=['Name', 'Zeitpunkt'])
    # add ratio to results
    perAcid[acid]['ratio'] = perAcid[acid]['mean']/perAcid[acid]['sumOfAcids']
    
    #plotting

    #select relevant columns
    #TODO: error bars
    ax=perAcid[acid][['Name', 'mean', 'ratio']].set_index('Name').plot(kind='bar', secondary_y=["ratio"], title=acid)
    #Axis labels
    ax.set_ylabel("Concentration")
    ax.right_ax.set_ylabel("Ratio")
    #Axis limits
    ax.right_ax.set_ylim((0,1))

    #save figure without unallowed system characters
    plt.savefig(acid.replace("/", "")+"_figure"+".pdf")
    
    
    print(acid)
    print(perAcid[acid])