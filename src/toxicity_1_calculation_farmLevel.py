#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import function
import os

def human_health_impact_cal (mainFile, pestFile):
    pestDF = pd.read_csv(pestFile, converters={'STATE': str, 'COUNTY': str, 'POID': str,
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
    pestDF['ai1'] = pestDF['AIAMT1_kg_sum'].div(pestDF['yield'])
    pestDF['ai2'] = pestDF['AIAMT2_kg_sum'].div(pestDF['yield'])

    # import USETox data
    useToxDF = pd.read_excel('USEtox_all_v2.xlsx', converters={'PCCode1': str, 'PCCode2': str, 'PCCode3': str})
    # append the CF values into pestGroup
    toxCols = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']
    df_group_zero = function.getUSEtoxValue_zeroToMissing(pestDF, useToxDF, toxCols, 'AICODE1')
    df_group_zero = function.getUSEtoxValue_zeroToMissing(pestDF, useToxDF, toxCols, 'AICODE2')
    df_group_secondQ = function.getUSEtoxValue_secondQuantileToMissing(pestDF, useToxDF, toxCols, 'AICODE1')
    df_group_secondQ = function.getUSEtoxValue_secondQuantileToMissing(pestDF, useToxDF, toxCols, 'AICODE2')
    df_group_thirdQ = function.getUSEtoxValue_thirdQuantileToMissing(pestDF, useToxDF, toxCols, 'AICODE1')
    df_group_thirdQ = function.getUSEtoxValue_thirdQuantileToMissing(pestDF, useToxDF, toxCols, 'AICODE2')
    df_group_max = function.getUSEtoxValue_maxToMissing(pestDF, useToxDF, toxCols, 'AICODE1')
    df_group_max = function.getUSEtoxValue_maxToMissing(pestDF, useToxDF, toxCols, 'AICODE2')

    # multiply each impact for each ai at the farmer level and sum to product level
    multiplyColLists = [['eco_mid_AICODE1', 'eco_end_AICODE1', 'hhc_mid_AICODE1', 'hhc_end_AICODE1', 'hhnc_mid_AICODE1',
                         'hhnc_end_AICODE1'],
                        ['eco_mid_AICODE2', 'eco_end_AICODE2', 'hhc_mid_AICODE2', 'hhc_end_AICODE2', 'hhnc_mid_AICODE2',
                         'hhnc_end_AICODE2']]
    aiColList = ['ai1', 'ai2']
    df_group_zero_mul = function.multiplyCols(df_group_zero, aiColList, multiplyColLists)
    df_group_secondQ_mul = function.multiplyCols(df_group_secondQ, aiColList, multiplyColLists)
    df_group_thirdQ_mul = function.multiplyCols(df_group_thirdQ, aiColList, multiplyColLists)
    df_group_max_mul = function.multiplyCols(df_group_max, aiColList, multiplyColLists)


    # sum them together
    colNameList = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']
    sumColList1 = ['eco_mid_AICODE1_ai1', 'eco_end_AICODE1_ai1', 'hhc_mid_AICODE1_ai1', 'hhc_end_AICODE1_ai1',
                   'hhnc_mid_AICODE1_ai1', 'hhnc_end_AICODE1_ai1']
    sumColList2 = ['eco_mid_AICODE2_ai2', 'eco_end_AICODE2_ai2', 'hhc_mid_AICODE2_ai2', 'hhc_end_AICODE2_ai2',
                   'hhnc_mid_AICODE2_ai2', 'hhnc_end_AICODE2_ai2']
    df_group_zero_sum = function.sumCols(df_group_zero_mul, [sumColList1, sumColList2], colNameList)
    df_group_secondQ_sum = function.sumCols(df_group_secondQ_mul, [sumColList1, sumColList2], colNameList)
    df_group_thirdQ_sum = function.sumCols(df_group_thirdQ_mul, [sumColList1, sumColList2], colNameList)
    df_group_max_sum = function.sumCols(df_group_max_mul, [sumColList1, sumColList2], colNameList)


    # aggregate (sum) the impact within a farmer
    df_group_zero_sum_farmer = df_group_zero_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    df_group_zero_sum_farmer = df_group_zero_sum_farmer.add_suffix('_sum').reset_index()
    df_group_secondQ_sum_farmer = df_group_secondQ_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    df_group_secondQ_sum_farmer = df_group_secondQ_sum_farmer.add_suffix('_sum').reset_index()
    df_group_thirdQ_sum_farmer = df_group_thirdQ_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    df_group_thirdQ_sum_farmer = df_group_thirdQ_sum_farmer.add_suffix('_sum').reset_index()
    df_group_max_sum_farmer = df_group_max_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    df_group_max_sum_farmer = df_group_max_sum_farmer.add_suffix('_sum').reset_index()

    # just contain the final useful cols
    cols_to_keep_final = ['STATE', 'COUNTY', 'POID', 'eco_mid_sum', 'eco_end_sum',
                          'hhc_mid_sum', 'hhc_end_sum', 'hhnc_mid_sum', 'hhnc_end_sum']
    df_group_zero_sum_farmer_new = df_group_zero_sum_farmer[cols_to_keep_final]
    df_group_secondQ_sum_farmer_new = df_group_secondQ_sum_farmer[cols_to_keep_final]
    df_group_thirdQ_sum_farmer_new = df_group_thirdQ_sum_farmer[cols_to_keep_final]
    df_group_max_sum_farmer = df_group_max_sum_farmer[cols_to_keep_final]

    df_group_zero_sum_farmer_new.to_csv('toxicityImpact_corn_zero.csv', index=False)
    df_group_secondQ_sum_farmer_new.to_csv('toxicityImpact_corn_secondQ.csv', index=False)
    df_group_thirdQ_sum_farmer_new.to_csv('toxicityImpact_corn_thirdQ.csv', index=False)
    df_group_max_sum_farmer.to_csv('toxicityImpact_corn_max.csv', index=False)

    print 'Saved impact results in csv files.'

    # calculate the percentage of impact
    perc_cols = ['eco_mid_sum', 'eco_end_sum', 'hhc_mid_sum', 'hhc_end_sum', 'hhnc_mid_sum', 'hhnc_end_sum']
    for col in perc_cols:
        df_group_zero_sum_farmer_new[col] = df_group_zero_sum_farmer_new[col]/\
                                                   df_group_zero_sum_farmer_new[col].sum()
        df_group_secondQ_sum_farmer_new[col] = df_group_secondQ_sum_farmer_new[col] / \
                                               df_group_secondQ_sum_farmer_new[col].sum()
        df_group_thirdQ_sum_farmer_new[col] = df_group_thirdQ_sum_farmer_new[col] / \
                                              df_group_thirdQ_sum_farmer_new[col].sum()
        df_group_max_sum_farmer[col] = df_group_max_sum_farmer[col] / \
                                       df_group_max_sum_farmer[col].sum()

    df_group_zero_sum_farmer_new.to_csv('toxicityImpact_corn_zero_perc.csv', index=False)
    df_group_secondQ_sum_farmer_new.to_csv('toxicityImpact_corn_secondQ_perc.csv', index=False)
    df_group_thirdQ_sum_farmer_new.to_csv('toxicityImpact_corn_thirdQ_perc.csv', index=False)
    df_group_max_sum_farmer.to_csv('toxicityImpact_corn_max_perc.csv', index=False)
    print 'Saved impact percentages in csv files.'


# human_health_impact_cal ('mainFile_yield.csv', 'pestFile_summed.csv')

if __name__ == '__main__':
    prompt = '>'
    entry = raw_input("This tool is used to calculate total toxicity impact at the farm level. \n"
                      "Please enter the 1) main file with yield data 2) pesticide file with summation \n"
                      "[e.g., mainFile_yield.csv pestFile_summed.csv] \n"
                      )
    mainFile = entry.split(' ')[0]
    pestFile = entry.split(' ')[1]

    human_health_impact_cal(mainFile, pestFile)

    print "Done!"
    k = raw_input("Press close to exit")

