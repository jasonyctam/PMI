import os
import numpy as np
import pandas as pd
from pandasql import sqldf
import time
import math

###################################################################
###################################################################
###################################################################
###################################################################

class PMI_Analysis():

###################################################################
###################################################################

    def __init__(self, corpus_path, textWindow):
        
        self.textlist = [os.path.join(corpus_path, fn) for fn in sorted(os.listdir(corpus_path))]
        self.textWindow = textWindow
        
        return 
        
###################################################################
###################################################################

    def getPMI_Average(self, word_Array):

        PMI_StartTime = time.time()
        
        self.wordCompArray = []
        pmi_all_Array = []

        for i in range(0, len(word_Array)):
            j = i + 1
            if i < len(word_Array)-1:
                while j < len(word_Array):
                    print word_Array[i], word_Array[j]
                    self.wordCompArray.append([word_Array[i], word_Array[j]])
                    pmi_all_Array.append(float(0))
                    j = j + 1
        
        # Loop through the file list
        for text_num in range(0,len(self.textlist)):
            
            pxy, px, py = self.runPMIAnalysis(text_num, word_Array)
            
            for i in range(0, len(self.wordCompArray)):
            
                if pxy[i] !=0:
                    pmi = math.log(pxy[i]/(px[i]*py[i]),2)
                    pmi_all_text = pmi_all_Array[i] + pmi
                    pmi_all_Array[i] = pmi_all_text
                    print self.wordCompArray[i], pmi_all_text
                    del pmi
                    del pmi_all_text
                
            del pxy
            del py
            del px

        pmi_average = []    
            
        for i in range(0,len(pmi_all_Array)):
            pmi_average.append(pmi_all_Array[i] / float(len(self.textlist)))
        
        PMI_EndTime = time.time()
        
        del pmi_all_Array
        del PMI_StartTime
        del PMI_EndTime
        
        return self.wordCompArray, pmi_average
        
###################################################################
###################################################################

    def runPMIAnalysis(self, text_num, word_Array):
    
        # Get file content into a 1D Array
        wordlist = self.getFileArray(self.textlist[text_num], ' ')

        # Create a dataframe of of the 1D array
        DF_wordlist = pd.DataFrame({'List of Words':wordlist})
        
        wordlist_len = len(wordlist)
        
        del wordlist

        # Drop unreadable values
        DF_wordlist.dropna()

        # Obtain the frequency of each word in a new column
        DF_wordlist['freq'] = DF_wordlist.groupby('List of Words')['List of Words'].transform('count')
        
        pxy = []
        px = []
        py = []
        
        for i in range(0, len(self.wordCompArray)):
            wordOne = self.wordCompArray[i][0]
            wordTwo = self.wordCompArray[i][1]
            p_xy, p_x, p_y = self.calc_PMI(DF_wordlist, wordlist_len, wordOne, wordTwo)
            pxy.append(p_xy)
            px.append(p_x)
            py.append(p_y)
            del p_xy
            del p_x
            del p_y
            del wordOne
            del wordTwo
                
        return pxy, px, py

###################################################################
###################################################################

    def calc_PMI(self, DF_wordlist, wordlist_len, wordOne, wordTwo):
        
        # Acquire the count value of each word
        print 'Acquire the count value of ' + wordOne + ' and ' + wordTwo + '...'
        if len(DF_wordlist.loc[DF_wordlist['List of Words'] == wordOne]['freq'].values) > 0:
            word1_count = DF_wordlist.loc[DF_wordlist['List of Words'] == wordOne]['freq'].values[0]
        else:
            word1_count = 0
            
        if len(DF_wordlist.loc[DF_wordlist['List of Words'] == wordTwo]['freq'].values) > 0:
            word2_count = DF_wordlist.loc[DF_wordlist['List of Words'] == wordTwo]['freq'].values[0]
        else:
            word2_count = 0

        print 'If both words are present....'
        if word1_count != 0 and word2_count != 0:
            px = float(word1_count) / float(wordlist_len)
            py = float(word2_count) / float(wordlist_len)
            
            del word1_count
            del word2_count

            # Acquire array of index for each word
            word1_index = DF_wordlist.loc[DF_wordlist['List of Words'] == wordOne]['freq'].index.values
            word2_index = DF_wordlist.loc[DF_wordlist['List of Words'] == wordTwo]['freq'].index.values
            
            del DF_wordlist

            # Converting the arrays of index to dataframes
            DF_word1_index = pd.DataFrame({'word1_index':word1_index})
            DF_word2_index = pd.DataFrame({'word2_index':word2_index})
            
            del word1_index
            del word2_index
            
            print 'Starting Query...'

            # Joining DF_word2_index to DF_word1_index with the + or - 500 words condition
            query = """
                    SELECT
                        DF_word1_index.word1_index AS word1_index
                        , DF_word2_index.word2_index AS word2_index
                    FROM
                        DF_word1_index 
                    LEFT OUTER JOIN
                        DF_word2_index
                    ON
                        DF_word2_index.word2_index <= DF_word1_index.word1_index + """ + repr(self.textWindow) + """ AND DF_word2_index.word2_index >= DF_word1_index.word1_index - """ + repr(self.textWindow) + """;
                    """
            # Executing the query
            DF_QueryResult = sqldf(query, locals())
            
            print 'Finished Query...'
            
            del query
            del DF_word1_index
            del DF_word2_index
            
            # Dropping all of the NaN values
            DF_QueryResult = DF_QueryResult.dropna(how='any')
            
            # Calculate concurrance
            coocurrence = len(DF_QueryResult.index)
            
            del DF_QueryResult
            
            print 'coocurrence: ' + repr(coocurrence)
            
            pxy = float(coocurrence) / float(wordlist_len)
            
        else:
            pxy = 0
            px = 0
            py = 0
        
        return pxy, px, py
    
###################################################################
###################################################################

    def getFileArray(self,inputFile,delimiter):
    # Converts contents of input file in formats similar to CSVs into a string array

        # Open input file
        processFile = open(inputFile, 'r')

        # Read all the lines in the file
        lines = processFile.readlines()

        # Initialize output array
        contentArray = []

        print 'Starting to loop through file'
        # Loop through the lines
        for i in range(0,len(lines)):

            # Strip the regex line dividers from each single line
            line = repr(lines[i].rstrip('\r\n'))

            # Split the single line with the input delimited into an array
            arrayLine = line.split(delimiter)
            
            print 'line: ' + repr(i) + ' arrayLine length: ' + repr(len(arrayLine))

            # Loop though each value of the line array and remove unnecessary strings
            for j in range(0,len(arrayLine)):

                # Append to output array
                contentArray.append(arrayLine[j].lower())
                
            del arrayLine
            del line
            
        print 'Finished looping through file'
        del lines

        processFile.close()
        del processFile

        return contentArray
    
###################################################################
###################################################################


if __name__ == "__main__":

    startTime = time.time()
    
    corpus_path = r'Files/'
    
    word1 = 'das'
    word2 = 'die'

    PMI_Object = PMI_Analysis(corpus_path)
    
    value = PMI_Object.getPMI_Average(word1, word2)
    
    print "value:" + repr(value)
    
    endTime = time.time()
    
    print "Time elapsed: " + repr(endTime-startTime)
    