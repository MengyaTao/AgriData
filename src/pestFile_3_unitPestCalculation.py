import pandas as pd
import numpy as np
from pestFile_2_pestSum import dType_creation

def unit_pest_cal (pestFile, yieldFile, aiNum):
    dtypeDict = dType_creation(aiNum)
    pestDF = pd.read_csv(pestFile, dtype=dtypeDict)
    mainDF = pd.read_csv(yieldFile, dtype={'STATE': str, 'COUNTY': str, 'POID': str})

    # combine STATE-COUNTY-POID to one column make it uniq
    pestDF['uniqID'] = pestDF['STATE'] + '-' + pestDF['COUNTY'] + '-' + pestDF['POID']
    mainDF['uniqID'] = mainDF['STATE'] + '-' + mainDF['COUNTY'] + '-' + mainDF['POID']

    pestDF['yield'] = np.nan
    rowCount = pestDF.shape[0]

    # attach yield to pest df for each farmer
    for i in range(0, rowCount):
        try:
            pestDF['yield'][i] = mainDF.at[mainDF['uniqID'] == pestDF['uniqID'][i], 'YIELD_2']
        except:
            pass

    print 'Finish attaching yield data to pestDF.'

    # calculate pest use per unit yield for each farmer
    for i in range(0, aiNum):
        sumText = 'AIAMT' + str(i + 1) + '_kg_sum'
        unitText = 'ai' + str(i + 1)
        pestDF[unitText] = pestDF[sumText].div(pestDF['yield'])

    # remove unnecessary cols
    pestDF = pestDF.drop(['AIAMT1_kg_sum', 'AIAMT2_kg_sum', 'yield'], axis=1)
    print 'Finish calculating the unit pest use data.'
    pestDF.to_csv('../data/output/pestFile_unit.csv', index=False)


unit_pest_cal ('../data/output/pestFile_summed.csv', '../data/output/mainFile_yield.csv', 2)