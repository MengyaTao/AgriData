import pandas as pd
import numpy as np

# use this when the data is cleaned
def pivotTableGenerator(mainFile, pestFile, uniqueIdCol, pestCol, valueCol):
    pestDF = pd.read_csv(pestFile, dtype={'STATE': str, 'COUNTY': str, 'POID': str,
                                               'AICODE1': str, 'AICODE2': str})
    mainDF = pd.read_csv(mainFile, dtype={'STATE': str, 'COUNTY': str, 'POID': str})
    pestDF['yield'] = np.nan
    rowCount = pestDF.shape[0]
    # attach yield to pest df for each farmer
    for i in range(0, rowCount):
        try:
            pestDF['yield'][i] = mainDF.loc[mainDF['POID'] == pestDF['POID'][i], 'YIELD_2']
        except:
            pass
    # calculate pest use per unit yield for each farmer
    pestDF['AI1_unit'] = pestDF['AIAMT1_kg_sum'].div(pestDF['yield'])
    pestDF['AI2_unit'] = pestDF['AIAMT2_kg_sum'].div(pestDF['yield'])

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

    outputFile = pestFile.split('.')[0] + '_pivotTable.csv'
    df.to_csv(outputFile)



if __name__ == '__main__':

    prompt = '>'
    # corn2010_pesticide_pivot.csv farm_id Pest Amount
    entry = raw_input("This tool is used to create a pivot table. \n"
                      "Four inputs: 1) input mainFile name, 2) input pestFile name"
                      "3) uniqueId column name \n"
                      "(it can be stateCountyFarmId or stateCountyId), \n"
                      "4) pesticide column name, 5) amount value column name.\n"
                      " [e.g., mainFile_yield.csv pestFile_summed.csv POID AICODE1 AI1_unit]\n"
                      "[e.g., mainFile_yield.csv pestFile_summed.csv POID AICODE2 AI2_unit]\n")

    mainFile = entry.split(' ')[0]
    pestFile = entry.split(' ')[1]
    uniqueIdCol = entry.split(' ')[2]
    pestCol = entry.split(' ')[3]
    valueCol = entry.split(' ')[4]
    pivotTableGenerator(mainFile, pestFile, uniqueIdCol, pestCol, valueCol)

    print "Done!"
    k = raw_input("Press close to exit")