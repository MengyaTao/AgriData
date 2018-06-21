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
    for i in range(0, rowCount):
        if len(pestDF.loc[i, 'AICODE2']) == 0:
            pass
        else:
            codeList = pestDF.loc[i, 'AICODE2']
            newCodeList = ""
            length = len(codeList)
            if '.' in codeList:
                j = 0
                while j <= length-1 and codeList[j]!= '.':
                    newCodeList = newCodeList+codeList[j]
                    j = j+1
                pestDF.loc[i, 'AICODE2'] = newCodeList

    print pestDF
    raw_input()
    # attach yield to pest df for each farmer
    for i in range(0, rowCount):
        try:
            pestDF.loc[i, 'yield'] = mainDF.loc[mainDF['POID'] == pestDF.loc[i, 'POID'], 'YIELD_2'].iloc[0]
        except:
            pass

    # calculate pest use per unit yield for each farmer
    pestDF['ai1_unit'] = pestDF['AIAMT1_kg_sum'].div(pestDF['yield']) # kg-pest/kg-yield
    pestDF['ai2_unit'] = pestDF['AIAMT2_kg_sum'].div(pestDF['yield'])

    # import USETox data
    useToxDF = pd.read_excel('USEtox_all_v2.xlsx', converters={'PCCode1': str, 'PCCode2': str, 'PCCode3': str})
    # append the CF values into pestGroup
    toxCols = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']

    df_group_zero = function.getUSEtoxValue_withMissingAssignment(pestDF, useToxDF, toxCols, 'AICODE1', 'zero')
    df_group_zero = function.getUSEtoxValue_withMissingAssignment(pestDF, useToxDF, toxCols, 'AICODE2', 'zero')
    print df_group_zero
    raw_input()
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

    print df_group_zero_mul[:5]
    print df_group_max_mul[:5]
    raw_input()

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


    df_group_zero_sum.to_csv('toxicityImpact_perPest_zero.csv', index=False)
    df_group_secondQ_sum.to_csv('toxicityImpact_perPest_secondQ.csv', index=False)
    df_group_thirdQ_sum.to_csv('toxicityImpact_perPest_thirdQ.csv', index=False)
    df_group_max_sum.to_csv('toxicityImpact_perPest_max.csv', index=False)

    # get the percentage within each farmer
    cols_to_keep = ['STATE', 'COUNTY', 'POID','eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']
    perc_cols = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']
    df_group_zero_sum = df_group_zero_sum[cols_to_keep]
    df_group_secondQ_sum = df_group_secondQ_sum[cols_to_keep]
    df_group_thirdQ_sum = df_group_thirdQ_sum[cols_to_keep]
    df_group_max_sum = df_group_max_sum[cols_to_keep]

    df_list = [df_group_zero_sum, df_group_secondQ_sum, df_group_thirdQ_sum, df_group_max_sum]

    for df in df_list:
        index = df_list.index(df)
        for col in perc_cols:
            colName = col + '_perc'
            df[colName] = (df / df.groupby(['STATE', 'COUNTY', 'POID']).transform(sum))[col]
        print df
        # df = pd.DataFrame(df)
        df.to_csv('toxicityImpact_perPest' + str(index) + '_perc.csv', index=False)


    # df_group_zero_sum_farmer = df_group_zero_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    # df_group_secondQ_sum_farmer = df_group_secondQ_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    # df_group_thirdQ_sum_farmer = df_group_thirdQ_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    # df_group_max_sum_farmer = df_group_max_sum.groupby(['STATE', 'COUNTY', 'POID']).sum()
    #
    # # df['sales_ratio'] = (df / df.groupby(['state']).transform(sum))['sales']
    #
    # for x in perc_cols:
    #     df_group_zero_sum_farmer_perc = df_group_zero_sum_farmer.groupby(level=['STATE', 'COUNTY', 'POID']).\
    #         apply(lambda x:100 * x / float(x.sum()))
    #     df_group_secondQ_sum_farmer_perc = df_group_secondQ_sum_farmer.groupby(level=['STATE', 'COUNTY', 'POID']).\
    #         apply(lambda x: 100 * x / float(x.sum()))
    #     df_group_thirdQ_sum_farmer_perc = df_group_thirdQ_sum_farmer.groupby(level=['STATE', 'COUNTY', 'POID']).\
    #         apply(lambda x: 100 * x / float(x.sum()))
    #     df_group_max_sum_farmer_perc = df_group_max_sum_farmer.groupby(level=['STATE', 'COUNTY', 'POID']).\
    #         apply(lambda x: 100 * x / float(x.sum()))

    # df_group_zero_sum_farmer_perc.to_csv('toxicityImpact_perPest_zero_perc.csv', index=False)
    # df_group_secondQ_sum_farmer_perc.to_csv('toxicityImpact_perPest_secondQ_perc.csv', index=False)
    # df_group_thirdQ_sum_farmer_perc.to_csv('toxicityImpact_perPest_thirdQ_perc.csv', index=False)
    # df_group_max_sum_farmer_perc.to_csv('toxicityImpact_perPest_max_perc.csv', index=False)

    print 'Saved impact results in csv files.'


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

