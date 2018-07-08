#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import function
import os
from pestFile_2_pestSum import dType_creation

def human_health_impact_cal (pestFile_unit, aiNum, useToxFile):
    dtypeDict = dType_creation(aiNum)
    pestDF = pd.read_csv(pestFile_unit, dtype = dtypeDict)
    outputPath = '../data/output/'

    # import USETox data
    # converters is used for read_excel
    useToxDF = pd.read_excel(useToxFile, converters={'PCCode1': str, 'PCCode2': str, 'PCCode3': str})
    # append the CF values into pestGroup
    toxCols = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']

    df_group_zero = pestDF.copy()
    df_group_secondQ = pestDF.copy()
    df_group_thirdQ = pestDF.copy()
    df_group_max = pestDF.copy()

    # assignedCriteria can be 'zero', 'min', 'max', 'secondQ', 'thirdQ'
    for i in range(0, aiNum):
        codeText = 'AICODE' + str(i+1)
        df_group_zero = function.getUSEtoxValue(df_group_zero, useToxDF, toxCols, codeText, assignedCriteria='zero')
        df_group_secondQ = function.getUSEtoxValue(df_group_secondQ, useToxDF, toxCols, codeText, assignedCriteria='secondQ')
        df_group_thirdQ = function.getUSEtoxValue(df_group_thirdQ, useToxDF, toxCols, codeText, assignedCriteria='thirdQ')
        df_group_max = function.getUSEtoxValue(df_group_max, useToxDF, toxCols, codeText, assignedCriteria='max')


    # multiply each impact for each ai at the farmer level and sum to product level for each row
    multiplyColLists = []
    for i in range(0, aiNum):
        codeText = 'AICODE' + str(i+1)
        colList = []
        for col in toxCols:
            colText = col + '_' + codeText
            colList.append(colText)
        multiplyColLists.append(colList)
    print multiplyColLists
    '''
    [['eco_mid_AICODE1', 'eco_end_AICODE1', 'hhc_mid_AICODE1', 'hhc_end_AICODE1', 'hhnc_mid_AICODE1', 'hhnc_end_AICODE1'],
    ['eco_mid_AICODE2', 'eco_end_AICODE2', 'hhc_mid_AICODE2', 'hhc_end_AICODE2', 'hhnc_mid_AICODE2', 'hhnc_end_AICODE2']]
    '''

    aiColList = []
    for i in range(0, aiNum):
        text = 'ai' + str(i+1)
        aiColList.append(text)
    print aiColList
    '''
    ['ai1', 'ai2']
    '''

    df_group_zero_mul = function.multiplyCols(df_group_zero, aiColList, multiplyColLists)
    df_group_secondQ_mul = function.multiplyCols(df_group_secondQ, aiColList, multiplyColLists)
    df_group_thirdQ_mul = function.multiplyCols(df_group_thirdQ, aiColList, multiplyColLists)
    df_group_max_mul = function.multiplyCols(df_group_max, aiColList, multiplyColLists)

    print 'Finish pesticide impact multiplication.'

    # sum them together
    sumColLists = []
    for i in range(0, aiNum):
        sumColList = []
        for col in toxCols:
            newCol = col + '_' + 'AICODE' + str(i+1) + '_' + 'ai' + str(i+1)
            sumColList.append(newCol)
        sumColLists.append(sumColList)

    print sumColLists
    '''
     sumColList1 = ['eco_mid_AICODE1_ai1', 'eco_end_AICODE1_ai1', 'hhc_mid_AICODE1_ai1', 'hhc_end_AICODE1_ai1',
                   'hhnc_mid_AICODE1_ai1', 'hhnc_end_AICODE1_ai1']
     sumColList2 = ['eco_mid_AICODE2_ai2', 'eco_end_AICODE2_ai2', 'hhc_mid_AICODE2_ai2', 'hhc_end_AICODE2_ai2',
                   'hhnc_mid_AICODE2_ai2', 'hhnc_end_AICODE2_ai2']
    '''

    df_group_zero_sum = function.sumCols(df_group_zero_mul, sumColLists, toxCols)
    df_group_secondQ_sum = function.sumCols(df_group_secondQ_mul, sumColLists, toxCols)
    df_group_thirdQ_sum = function.sumCols(df_group_thirdQ_mul, sumColLists, toxCols)
    df_group_max_sum = function.sumCols(df_group_max_mul, sumColLists, toxCols)

    df_group_zero_sum.to_csv(outputPath + 'df_group_zero_sum.csv', index=False)
    df_group_secondQ_sum.to_csv(outputPath + 'df_group_secondQ_sum.csv', index=False)
    df_group_thirdQ_sum.to_csv(outputPath + 'df_group_thirdQ_sum.csv', index=False)
    df_group_max_sum.to_csv(outputPath + 'df_group_max_sum.csv', index=False)

    print 'Finish summing the impact of the same active ingredients for each farmer.'

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
    df_group_zero_sum_farmer = df_group_zero_sum_farmer[cols_to_keep_final]
    df_group_secondQ_sum_farmer = df_group_secondQ_sum_farmer[cols_to_keep_final]
    df_group_thirdQ_sum_farmer = df_group_thirdQ_sum_farmer[cols_to_keep_final]
    df_group_max_sum_farmer = df_group_max_sum_farmer[cols_to_keep_final]

    df_group_zero_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_zero.csv', index=False)
    df_group_secondQ_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_secondQ.csv', index=False)
    df_group_thirdQ_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_thirdQ.csv', index=False)
    df_group_max_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_max.csv', index=False)

    print 'Finish summing the impacts for each farmer.'

    # calculate the percentage of impact
    perc_cols = ['eco_mid_sum', 'eco_end_sum', 'hhc_mid_sum', 'hhc_end_sum', 'hhnc_mid_sum', 'hhnc_end_sum']
    for col in perc_cols:
        df_group_zero_sum_farmer[col] = df_group_zero_sum_farmer.loc[:, col]/float(df_group_zero_sum_farmer[col].sum())
        df_group_secondQ_sum_farmer[col] = df_group_secondQ_sum_farmer.loc[:, col]/float(df_group_secondQ_sum_farmer[col].sum())
        df_group_thirdQ_sum_farmer[col] = df_group_thirdQ_sum_farmer.loc[:, col]/float(df_group_thirdQ_sum_farmer[col].sum())
        df_group_max_sum_farmer[col] = df_group_max_sum_farmer.loc[:, col]/float(df_group_max_sum_farmer[col].sum())

    df_group_zero_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_zero_perc.csv', index=False)
    df_group_secondQ_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_secondQ_perc.csv', index=False)
    df_group_thirdQ_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_thirdQ_perc.csv', index=False)
    df_group_max_sum_farmer.to_csv(outputPath + 'toxicityImpact_corn_max_perc.csv', index=False)
    print 'Finish calculating impact percentages for each farmer.'


human_health_impact_cal ('../data/output/pestFile_unit.csv', 2, '../data/input/USEtox_all_v2.xlsx')

# if __name__ == '__main__':
#     prompt = '>'
#     entry = raw_input("This tool is used to calculate total toxicity impact at the farm level. \n"
#                       "Please enter the 1) main file with yield data 2) pesticide file with summation \n"
#                       "[e.g., mainFile_yield.csv pestFile_summed.csv] \n"
#                       )
#     mainFile = entry.split(' ')[0]
#     pestFile = entry.split(' ')[1]
#
#     human_health_impact_cal(mainFile, pestFile)
#
#     print "Done!"
#     k = raw_input("Press close to exit")

