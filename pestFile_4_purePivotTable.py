import pandas as pd
import numpy as np

# use this when the data is cleaned
def pivotTableGenerator(inputFile, uniqueIdCol, pestCol, valueCol):
    pestDF = pd.read_csv(inputFile, converters={'STATE': str, 'COUNTY': str, 'POID': str,
                                               'AICODE1': str, 'AICODE2': str})

    # if uniqueIdCol is stateCountyFarmId, then it is at farm level pivot table
    # if uniqueIdCol is stateCountyId, the it is at county level (pesticide amount summed across the county)
    # the function of summation is used
    df = pd.pivot_table(pestDF, values=valueCol,
                        index=uniqueIdCol, columns=[pestCol],
                        aggfunc=np.sum).reset_index()

    df['STATE'] = ''
    df['COUNTY'] = ''

    rowCount = df.shape[0]
    for i in range(0, rowCount):
        df.at[i, 'STATE'] = list(pestDF.loc[pestDF['POID'] == df['POID'][i], 'STATE'])[0]
        df.at[i, 'COUNTY'] = list(pestDF.loc[pestDF['POID'] == df['POID'][i], 'COUNTY'])[0]

    outputFile = inputFile.split('.')[0] + '_pivotTable.csv'
    df.to_csv(outputFile)



if __name__ == '__main__':

    prompt = '>'
    # corn2010_pesticide_pivot.csv farm_id Pest Amount
    entry = raw_input("This tool is used to create a pivot table. \n"
                      "Four inputs: 1) input file name, 2) uniqueId column name \n"
                      "(it can be stateCountyFarmId or stateCountyId), \n"
                      "3) pesticide column name, 4) amount value column name.\n"
                      " [e.g., pestFile_summed.csv POID AICODE1 AIAMT1_kg_sum]\n")

    inputFile = entry.split(' ')[0]
    uniqueIdCol = entry.split(' ')[1]
    pestCol = entry.split(' ')[2]
    valueCol = entry.split(' ')[3]
    pivotTableGenerator(inputFile, uniqueIdCol, pestCol, valueCol)

    print "Done!"
    k = raw_input("Press close to exit")