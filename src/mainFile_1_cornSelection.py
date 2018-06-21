import sys
sys.setrecursionlimit(5000)
import pandas as pd

# this script is design to be working on corn data
# just do the pesticides calculation - HHC, HHNC

'''
Assumption 1 - yield data in mainFile [only work with For Grain]
    + BHARVACR - acres harvest
    + BYIELD - yield per acre
    + BYLDUNIT - unit code (need conversion later)

Step 1 - Yield columns, get manually from main file [copy and paste] or from cols_to_keep
STATE, COUNTY, POID, CROPCODE, BHARVACR, BYIELD, BYLDUNIT

'''

# step 1 - yield data

def main_file_process (inputFile, cols_to_keep, cornCode):
    # read the data in the right format
    if '.csv' in inputFile:
        df = pd.read_csv(inputFile)

    elif '.sas7bdat' in inputFile:
        df = pd.read_sas(inputFile)

    elif '.txt' in inputFile:
        df = pd.read_table(inputFile)

    else:
        df = pd.read_excel(inputFile, sheetname='Sheet1')

    print 'Successfully imported the file.'
    # decide which columns to keep
    if cols_to_keep == ['all'] or cols_to_keep == ['ALL'] or cols_to_keep == ['All']:
        df = df
        print 'Keep all of the columns.'
    else:
        print cols_to_keep
        df = df[cols_to_keep] # cols_to_keep is a list of colNames
        print 'Keep the selected columns'
        # df = df.iloc[:, cols_to_keep], get by index

    # change STATE, COUNTY, CROPCODE, BYLDUNIT to string
    cols_to_string = ['STATE', 'COUNTY', 'POID', 'CROPCODE', 'BYLDUNIT']
    for col in cols_to_string:
        df[col] = df[col].astype(str)

    # only select the rows that have the cornCode
    df = df.loc[df['CROPCODE'] == cornCode]
    df.to_csv('mainFile_processed.csv', index=False)
    return df

#
# df = main_file_process ('mainSample.csv', 'ALL', '6')
# print df
# mainSample.csv STATE,COUNTY 6

if __name__ == '__main__':
    prompt = '>'
    entry = raw_input("This tool is used to select a subset of COLUMNS to keep. \n"
                      "You can also use it to transform file between different file formats. \n"
                      "Please enter the 1) input file name 2) column names to keep \n"
                      "[e.g., mainSample.csv all 6] \n")
    inputFile = entry.split(' ')[0]
    cols2keep = entry.split(' ')[1]

    if cols2keep != 'all' or cols2keep != 'ALL' or cols2keep != 'All':
        elementsList = cols2keep.split(',')
        cols2keep = []
        for ele in elementsList:
            cols2keep.append(ele)
    cornCode = str(entry.split(' ')[2])
    print cornCode
    main_file_process(inputFile, cols2keep, cornCode)

    print "Done!"
    k = raw_input("Press close to exit")