import pandas as pd
import numpy as np
import function
import os

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

def pest_file_sum (inputFile, aiNum):
    # aiNum is to define how many active ingredients would be included, mostly 2-3
    dtypeDict = {'STATE': str,
                 'COUNTY': str,
                 'CROPCODE': str,
                 'POID': str,}
    for num in range(0, aiNum):
        keyText = 'AICODE' + str(num + 1)
        dtypeDict[keyText] = str

    df = pd.read_csv(inputFile, dtype=dtypeDict)
    print 'Original dataset shape: ', df.shape

    rowCount = df.shape[0]
    # unit converstion to kg from pounds
    for num in range(0, aiNum):
        keyText_raw = 'AIAMT' + str(num + 1)
        keyText_new = keyText_raw + '_kg'
        df[keyText_new] = np.nan
        for i in range(0, rowCount):
            df.ix[i, keyText_new] = df.ix[i, keyText_raw] * 0.453592
        # drop the original amount col
        df = df.drop([keyText_raw], axis=1)

    print 'Finish converting pest amount from pound to kg.'

    # group data by state-county-farmer 3 columns combination, sum each pest use at the farmers level
    gourpbyList = ['STATE', 'COUNTY', 'POID']
    for num in range(0, aiNum):
        gourpbyList.append('AICODE' + str(num + 1))

    print 'The gourpbyList is: ', gourpbyList
    df_group = df.groupby(gourpbyList).sum()

    # reset the index
    df_group = df_group.add_suffix('_sum').reset_index()

    print 'Finish summing the pest use of each kind for each farmer.'
    # create an empty column for yield
    df_group.to_csv('../data/output/pestFile_summed.csv', index=False)

pest_file_sum ('../data/output/pestFile_processed.csv', aiNum=2)



# if __name__ == '__main__':
#     prompt = '>'
#     entry = raw_input("This tool is used to calculate the pesticide data. \n"
#                       "Please enter the 1) input file name"
#                       "[e.g., pestFile_processed.csv] \n"
#                       )
#     inputFile = entry.split(' ')[0]
#
#     pest_file_sum(inputFile)

    # print "Done!"
    # k = raw_input("Press close to exit")