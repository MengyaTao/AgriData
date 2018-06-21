import pandas as pd
import numpy as np
import function

def pest_file_sum (inputFile):
    df = pd.read_csv(inputFile, converters={'STATE': str, 'COUNTY': str, 'CROPCODE': str,
                                            'POID': str, 'AICODE1': str, 'AICODE2': str})
    rowCount = df.shape[0]
    # unit converstion to kg from pounds
    df['AIAMT1_kg'] = np.nan
    df['AIAMT2_kg'] = np.nan
    for i in range(0, rowCount):
        df.ix[i, 'AIAMT1_kg'] = df.ix[i, 'AIAMT1'] * 0.453592
        df.ix[i, 'AIAMT2_kg'] = df.ix[i, 'AIAMT2'] * 0.453592

    # group data by state-county-farmer 3 columns combination, sum each pest use at the farmers level
    df_group = df.groupby(['STATE', 'COUNTY', 'POID', 'AICODE1']).sum()
    print df_group
    # reset the index
    df_group = df_group.add_suffix('_sum').reset_index()
    # create an empty column for aicode2 and yield
    df_group['AICODE2'] = ''
    # get aicode2 amount value column back
    df_group = function.getValueBasedOnAnotherCol(df, df_group, 'AICODE1', 'AICODE2', 'AIAMT2_kg_sum')
    print df_group
    df_group.to_csv('pestFile_summed.csv', index=False)

# pest_file_sum ('pestFile_processed.csv')



if __name__ == '__main__':
    prompt = '>'
    entry = raw_input("This tool is used to calculate the pesticide data. \n"
                      "Please enter the 1) input file name"
                      "[e.g., pestFile_processed.csv] \n"
                      )
    inputFile = entry.split(' ')[0]

    pest_file_sum(inputFile)

    print "Done!"
    k = raw_input("Press close to exit")