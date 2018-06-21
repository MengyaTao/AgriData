#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

'''
Assumption 1 - yield data in mainFile [only work with For Grain]
    + BHARVACR - acres harvest
    + BYIELD - yield per acre
    + BYLDUNIT - unit code (need conversion later)

Step 2 - Yield calculation
STATE, COUNTY, POID, CROPCODE, BHARVACR, BYIELD, BYLDUNIT
Yield = BHARVACR * BYIELD

'''

def main_yield_calculation(inputFile):
    df = pd.read_csv(inputFile, dtype={'STATE': str, 'COUNTY': str, 'CROPCODE':str,
                                       'POID': str, 'BYLDUNIT': str})
    # drop the rows without either BHARVACR, BYIELD, or BYLDUNIT
    df.dropna(subset=['BHARVACR'], inplace=True)
    df.dropna(subset=['BYIELD'], inplace=True)
    df.dropna(subset=['BYLDUNIT'], inplace=True)
    # drop the rows with BYLDUNIT = 0 or -1
    df = df[df.BYLDUNIT != '0']
    df = df[df.BYLDUNIT != '0.0']
    df = df[df.BYLDUNIT != '-1']
    df = df[df.BYLDUNIT != '-1.0']
    df = df.reset_index(drop=True)
    # multiplication
    df['YIELD_1'] = df['BHARVACR'].mul(df['BYIELD'])
    rowCount = df.shape[0]
    print rowCount
    # unit converstion to kg
    df['YIELD_2'] = np.nan

    for i in xrange(0, rowCount):
        if df.at[i,'BYLDUNIT'] == '1' or df.at[i,'BYLDUNIT'] == '1.0': # pound
            df.at[i,'YIELD_2'] = df.at[i,'YIELD_1'] * 0.453592

        elif df.at[i,'BYLDUNIT'] == '2' or df.at[i,'BYLDUNIT'] == '2.0': # cwt
            df.at[i,'YIELD_2'] = df.at[i,'YIELD_1'] * 50.8023

        elif df.at[i,'BYLDUNIT'] == '3' or df.at[i,'BYLDUNIT'] == '3.0': # tons
            df.at[i,'YIELD_2'] = df.at[i,'YIELD_1'] * 907.185

        elif df.at[i,'BYLDUNIT'] == '4' or df.at[i,'BYLDUNIT'] == '4.0': # bushels
            df.at[i,'YIELD_2'] = df.at[i,'YIELD_1'] * 25.40

    df.to_csv('mainFile_yield.csv', index=False)
    return df

# main_yield_calculation('mainFile_processed.csv')

if __name__ == '__main__':
    prompt = '>'
    entry = raw_input("This tool is used to calculate the yield data. \n"
                      "Please enter the 1) input file name \n"
                      "[e.g., mainFile_processed.csv] \n"
                      )
    inputFile = entry.split(' ')[0]

    main_yield_calculation(inputFile)

    print "Done!"
    k = raw_input("Press close to exit")