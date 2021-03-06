import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# CONFIG
###############################################################################

# LC Data File
lcDataFile = {'filename': "Laura_all_comma.txt", 'sep': ';', 'decimal': ','}

# Output file for cleaned LC Data

cleanDataFile = {'filename': "cleanDataFile.txt", 'sep': lcDataFile['sep'], 'decimal': '.'}

# nameList
nameList = {'filename': "namelist2.csv", 'sep': ';', 'decimal': ','}

importantAcids = ["Crotonate","Acetate","Propionate","3-Hydroxybutyrate","Methylsuccinate","Ethylmalonate","Mesaconate","2-Hydroxy-3-Methylsuccinate","Succinate","Methylmalonat"]
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


#replace decimal comma by decimal point, remove thousand point, set '----' to ''
with open(lcDataFile['filename'], 'r') as dataFile:
    with open(cleanDataFile['filename'], 'w') as outfile:
        for num, line in enumerate(dataFile):
            lineArray = line.split(lcDataFile['sep'])
            if num>0:
                for num, el in enumerate(lineArray):
                    if num>0:
                        lineArray[num] = el.replace('.', '').replace(',', '.').replace('-----', '')
            transformedLine = lcDataFile['sep'].join(lineArray)
            outfile.write(transformedLine)






# Read LC Data 
pdLcData = pd.read_csv(cleanDataFile['filename'], sep=cleanDataFile['sep'], decimal=cleanDataFile['decimal'], encoding="utf-8", dtype="str")[rowsToKeep]

# Convert Concentrations to numeric values
for column in importantAcids:
    pdLcData[column] = pdLcData[column].apply(pd.to_numeric, errors="coerce")


#Remove negative concentrations
for column in importantAcids:
    pdLcData[column][pdLcData[column]<0] = 0

# Convert "Data Filename" column to number (corresponding Nr expected in nameList variable)
pdLcData["Data Filename"] = [removePathAndExtension(filename) for filename in pdLcData["Data Filename"]]

print(pdLcData)
# Read nameList
pdNameList = pd.read_csv(nameList['filename'], sep=nameList['sep'], decimal=nameList['decimal'], dtype={"Nr": "str"})


# Convert numbers to clear names by merging LC Data file and nameList 
pdNamedLcData = pd.merge(pdLcData, pdNameList, left_on="Data Filename", right_on="Nr")

# Group Replicates based on Name and timepoint, calculate mean, std, number 
grouped = pdNamedLcData.groupby(['Name', 'Zeitpunkt'])
meanDev = grouped.agg({x: ["mean", "std", "count"] for x in importantAcids})
meanDev.to_csv("overview.csv", sep=";", decimal=".")


# Split Results for each acid given in importantAcids
perAcid = {acid: meanDev[acid].sort_values('mean', ascending=False) for acid in importantAcids}

# For each acid in importantAcids
for acid in perAcid:
    # sort concentration in descening order. Take best 10. remove negative concentrations
    perAcid[acid] = perAcid[acid].reset_index().head(noOfBestHits)
    perAcid[acid] = perAcid[acid].loc[perAcid[acid]['mean'] > 0]

    # Dataframe for saving sum of acids
    sumOfAcids = pd.DataFrame()


    # get the sum of all acids for this sample and timepoint
    for index, row in perAcid[acid].iterrows():
        allAcid = meanDev.loc[(row['Name'], row["Zeitpunkt"])].xs('mean', level=1).sum()
        allAcidDf = pd.DataFrame({'Name': [row['Name']], "Zeitpunkt": [row["Zeitpunkt"]], 'sumOfAcids': [allAcid]})
        sumOfAcids = sumOfAcids.append(allAcidDf)

    # add sum of all acids to result table
    perAcid[acid] = perAcid[acid].merge(sumOfAcids, on=['Name', 'Zeitpunkt'])
    # add ratio to results
    perAcid[acid]['ratio'] = perAcid[acid]['mean'] / perAcid[acid]['sumOfAcids']

    # plotting

    # Select errror column for error bars, rename to 'mean' to match mean value column
    errors = perAcid[acid][['Name', 'std']].set_index('Name')
    errors.columns = ['mean']
    # select relevant columns for plot
    ax = perAcid[acid][['Name', 'mean', 'ratio']].set_index('Name').plot(kind='bar', secondary_y=["ratio"], title=acid,
                                                                         yerr=errors)

    # Axis labels
    ax.set_ylabel("Concentration")
    ax.right_ax.set_ylabel("Ratio")
    # Axis limits
    ax.set_ylim(bottom=0)
    ax.right_ax.set_ylim((0, 1))

    # save figure without unallowed system characters
    plt.savefig(acid.replace("/", "") + "_figure" + ".pdf")

    # print(acid)
    # print(perAcid[acid])

    # export as csv
    perAcid[acid].to_csv(acid.replace("/", "") + "_table" + ".csv", sep=";", decimal=".")
