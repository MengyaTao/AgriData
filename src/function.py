#!/usr/bin/python
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import os

dir_path = os.getcwd()

def fileInFolder(folderPath):
    # list all of the files in a folder
    files = os.listdir(folderPath)
    return files

def mkFolderNotExist(folderPath):
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)

def readInPestAndMainCSV(pestFile, mainFile):
    pestDF = pd.read_csv(pestFile, converters={'state': str, 'county': str, 'crop': str,
                                                   'state_poid': str, 'aicode1': str, 'aicode2': str})
    mainDF = pd.read_csv(mainFile, dtype={'state': str, 'county': str, 'state_poid': str})
    return pestDF, mainDF


def pestDFbyCrops (pestDF):
    # 2. segarate pestDF to crop type
    pestGroups = pestDF.groupby('crop')
    cropFolder = os.path.join(dir_path, 'pestCrop')
    mkFolderNotExist(cropFolder)
    # 3. create a folder to host those pest files for each crop type
    for key, values in pestGroups:
        # print pestGroups.get_group(key)
        pestGroups.get_group(key).to_csv(os.path.join(cropFolder, key + '.csv'), index=False)
    return cropFolder


def readInCropFile (cropFilePath, cropFile, strColList):
    fileName = os.path.join(cropFilePath, cropFile)
    cropType = fileName.split('.')[0].split('/')[-1]
    # print cropType
    strDict = {}
    for strName in strColList:
        strDict[strName] = str
    df = pd.read_csv(fileName, converters=strDict)
    return cropType, df

def getAIcol(df, df_group, otherAICols, otherAICols_amt):
    for col in otherAICols:
        index = otherAICols.index(col)
        df_group[col] = ''
        # get aicode2 amount value column back
        df_group = getValueBasedOnAnotherCol(df, df_group, 'aicode1', col, otherAICols_amt[index])
    return df_group


def calUnitPest (df_group, aiAmountList, yieldCol):
    for aiCol in aiAmountList:
        newColName = aiCol.split('_')[0] + '_unit'
        df_group[newColName] = df_group[aiCol].div(df_group[yieldCol])
    # drop the sum and yield col
    colsToDrop = aiAmountList
    colsToDrop.append(yieldCol)
    df_group.drop(colsToDrop, axis=1, inplace=True)
    return df_group

def createYieldCol(df_group, mainDF, cropDict, cropType, farmerId):
    df_group['yield'] = np.nan
    # attach yield to pest df for each farmer
    df_group = getYieldFromMain2(df_group, mainDF, 'yield', cropDict, farmerId, cropType)
    return df_group

def readInUSEtox(USEtoxFile):
    USEToxDF = pd.read_excel(USEtoxFile, converters={'PCCode1': str, 'PCCode2': str, 'PCCode3': str})
    return USEToxDF

def appendCF(df_group_unit, USEToxDF, aiCodeList):
    toxCols = ['eco_mid', 'eco_end', 'hhc_mid', 'hhc_end', 'hhnc_mid', 'hhnc_end']
    for aiCode in aiCodeList:
        df_group_zero = getUSEtoxValue_zeroToMissing(df_group_unit, USEToxDF, toxCols, aiCode)
        df_group_secondQ = getUSEtoxValue_secondQuantileToMissing(df_group_unit, USEToxDF, toxCols, aiCode)
        df_group_thirdQ = getUSEtoxValue_thirdQuantileToMissing(df_group_unit, USEToxDF, toxCols, aiCode)
        df_group_max = getUSEtoxValue_maxToMissing(df_group_unit, USEToxDF, toxCols, aiCode)
    return df_group_zero, df_group_secondQ, df_group_thirdQ, df_group_max

def getValueBasedOnAnotherCol(df_from, df_to, col_from, col_to, refCol_to):
    colCount_to = df_to.shape[0]
    for i in range(colCount_to):
        if pd.isnull(df_to[refCol_to][i]):
            continue
        else:
            df_to[col_to][i] = df_from.loc[df_from[col_from] == df_to[col_from][i], col_to].iloc[0]
    return df_to



def getYieldFromMain(df, df_main, yieldColName, cropDict, farmIdColName, cropColName):
    colCount = df.shape[0]
    for i in range(colCount):
        if pd.isnull(df[farmIdColName][i]):
            continue
        else:
            cropCode = df[cropColName][i]
            mainCropColName = cropDict[cropCode]
            df[yieldColName][i] = df_main.loc[df_main[farmIdColName] == df[farmIdColName][i], mainCropColName]
    return df

def getYieldFromMain2(df, df_main, yieldColName, cropDict, farmIdColName, cropCode):
    colCount = df.shape[0]
    for i in range(colCount):
        if pd.isnull(df[farmIdColName][i]):
            continue
        else:
            mainCropColName = cropDict[cropCode]
            df[yieldColName][i] = df_main.loc[df_main[farmIdColName] == df[farmIdColName][i], mainCropColName]
    return df


def getUSEtoxValue(df, df_useTox, colNameList, aiColName):
    colCount = df.shape[0]
    for col in colNameList:
        dfColName = col + '_' + aiColName
        print dfColName
        df[dfColName] = np.nan
        for i in range(colCount):
            chemCode = df[aiColName][i]
            # check if a value is in the column
            if chemCode in df_useTox['PCCode1'].values:
                df[dfColName][i] = df_useTox.loc[df_useTox['PCCode1']==chemCode, col]
            elif chemCode in df_useTox['PCCode2'].values:
                df[dfColName][i] = df_useTox.loc[df_useTox['PCCode2'] == chemCode, col]
            elif chemCode in df_useTox['PCCode3'].values:
                df[dfColName][i] = df_useTox.loc[df_useTox['PCCode3'] == chemCode, col]
    return df


def getUSEtoxValue_withMissingAssignment(df, df_useTox, colNameList, aiColName, assignment):
    rowCount = df.shape[0]
    df_new = df.copy()
    for col in colNameList:
        dfColName = col + '_' + aiColName
        df_new[dfColName] = np.nan
        for i in range(rowCount):
            chemCode = df_new.loc[i, aiColName]
            # check if a value is in the column
            if chemCode in df_useTox['PCCode1'].values:
                df_new.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode1'] == chemCode, col].iloc[0]
            elif chemCode in df_useTox['PCCode2'].values:
                df_new.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode2'] == chemCode, col].iloc[0]
            elif chemCode in df_useTox['PCCode3'].values:
                df_new.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode3'] == chemCode, col].iloc[0]
            elif len(chemCode) == 0:
                df_new.loc[i, dfColName] = 0.0

            if pd.isnull(df_new.loc[i, dfColName]):
                if assignment == 'zero':
                    df_new.loc[i, dfColName] = 0.0
                elif assignment == 'max':
                    df_new.loc[i, dfColName] = max(df_useTox[col].values)
                elif assignment == 'secondQ':
                    df_new.loc[i, dfColName] = df_useTox[col].quantile(0.25)
                elif assignment == 'thirdQ':
                    df_new.loc[i, dfColName] = df_useTox[col].quantile(0.75)
    return df_new


def getValue(df_useTox_col, assignedCriteria):
    if assignedCriteria == 'zero':
        value = 0.0
    elif assignedCriteria == 'max':
        value = np.nanmax(df_useTox_col.values)
    elif assignedCriteria == 'secondQ':
        value = np.nanpercentile(df_useTox_col, 50)
    elif assignedCriteria == 'thirdQ':
        value = np.nanpercentile(df_useTox_col, 70)
    elif assignedCriteria == 'avg':
        value = np.nanmean(df_useTox_col.values)
    elif assignedCriteria == 'min':
        value = np.nanmin(df_useTox_col.values)

    return value


def getUSEtoxValue(df, df_useTox, colNameList, aiColName, assignedCriteria):
    # colNameList is toxCols
    rowCount = df.shape[0]
    for col in colNameList:
        dfColName = col + '_' + aiColName
        df[dfColName] = np.nan
        for i in range(rowCount):
            value = getValue(df_useTox[col], assignedCriteria)
            chemCode = str(df.loc[i, aiColName])

            if chemCode != 'nan':
                # check if a value is in the column
                if chemCode in df_useTox['PCCode1'].values:
                    df.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode1'] == chemCode, col].iloc[0]
                elif chemCode in df_useTox['PCCode2'].values:
                    df.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode2'] == chemCode, col].iloc[0]
                elif chemCode in df_useTox['PCCode3'].values:
                    df.loc[i, dfColName] = df_useTox.loc[df_useTox['PCCode3'] == chemCode, col].iloc[0]
                else:
                    df.loc[i, dfColName] = value

                # this need to put in the last order so that all NA would be convert to 0s
                if pd.isnull(df.loc[i, dfColName]):
                    df.loc[i, dfColName] = value
    return df


def multiplyCols(df, unitColList, multiplyColLists):
    df_new = df.copy()
    for unitCol in unitColList:
        index = unitColList.index(unitCol)
        multiColList = multiplyColLists[index]
        for multiCol in multiColList:
            newCol = multiCol + '_' + unitCol
            df_new[newCol] = df[unitCol] * df[multiCol]
            df_new = df_new.drop(multiCol, axis=1)
    return df_new


def divideColsPerc(df, colList, sumColList):
    for col in colList:
        index = colList.index(col)
        df[colList[index] + '_perc'] = df[colList[index]].div(df[sumColList[index]])
    return df


def sumCols(df, sumColLists, toxCols):
    colCount = len(sumColLists[0])
    sumColCount = len(sumColLists)
    rowCount = df.shape[0]
    for i in range(colCount):
        df[toxCols[i]] = 0.0
        for j in range(rowCount):
            # for cell with NAN, use 0 for summation
            for m in range(sumColCount):
                df.loc[j, toxCols[i]] = df.loc[j, sumColLists[m][i]] + df.loc[j, toxCols[i]]
    # delete the sumColList1 and sumColList2
    for m in range(sumColCount):
        df = df.drop(sumColLists[m], axis=1)
    return df


def percCols(df, colNameList, groupByList):
    for col in colNameList:
        newCol = col + '_' + 'pct'
        df[newCol] = df.groupby(groupByList)[col].apply(lambda x: x.astype(float) / x.sum())
        df = df.drop(df[col], axis=1)
    return df


def get_stats(group):
    return {'min': group.min(), 'max': group.max(),
            'count': group.count(), 'mean': group.mean(),
            'standard deviation': group.std()}

def multiplyAndSumCF (df, unitColList, multiplyColLists, sumColLists, colNameList):
    df = multiplyCols(df, unitColList, multiplyColLists)
    df = sumCols(df, sumColLists, colNameList)
    # drop unitColList
    df.drop(unitColList, axis=1, inplace=True)
    return df