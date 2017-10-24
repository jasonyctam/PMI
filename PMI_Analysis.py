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

    def __init__(self, textFile, textWindow):
        
        self.textFile = textFile
        self.textWindow = textWindow
        
        return 
        
###################################################################
###################################################################

    def getPMI_Average(self, wordList):

        PMI_StartTime = time.time()

        print 'Starts processing ' + self.textFile
    
        # Get file content into a 1D Array
        sourcelist = self.getFileArray(self.textFile, ' ')
        self.wordlist_len = len(sourcelist)
        
        print 'Storing the wordlist into a dataframe....'
        
        # Create a dataframe of of the 1D array
        self.DF_wordlist = pd.DataFrame({'List of Words':sourcelist})
        
        del sourcelist
        
        print 'Dropping unreadable values....'
        # Drop unreadable values
        self.DF_wordlist.dropna()

        print 'Obtain the frequency of each word in a new column....'
        # Obtain the frequency of each word in a new column
        self.DF_wordlist['freq'] = self.DF_wordlist.groupby('List of Words')['List of Words'].transform('count')
        
        allWordCompArray = []
        pmi_all_Array = []
        
        for i in range(0,len(wordList)):
        
            word_Array = wordList[i]

            wordCompArray, pmi_Array = self.getWordComp(word_Array)

            pxy, px, py = self.runPMIAnalysis(wordCompArray)

            # Calculate PMI
            for i in range(0, len(wordCompArray)):
                if pxy[i] !=0:
                    pmi = math.log(pxy[i]/(px[i]*py[i]),2)
                    pmi_Array[i] = pmi
                    print wordCompArray[i], pmi_Array[i]
                    del pmi

            allWordCompArray.append(wordCompArray)
            pmi_all_Array.append(pmi_Array)
            del wordCompArray
            del pmi_Array

        del pxy
        del py
        del px

        PMI_EndTime = time.time()
        
        del PMI_StartTime
        del PMI_EndTime
        
        return allWordCompArray, pmi_all_Array
        
###################################################################
###################################################################

    def runPMIAnalysis(self, wordCompArray):
        
        pxy = []
        px = []
        py = []
        
        print 'Looping through each word combination....'
        for i in range(0, len(wordCompArray)):
            wordOne = wordCompArray[i][0]
            wordTwo = wordCompArray[i][1]
            p_xy, p_x, p_y = self.calc_PMI(wordOne, wordTwo)
            pxy.append(p_xy)
            px.append(p_x)
            py.append(p_y)
            del p_xy
            del p_x
            del p_y
            del wordOne
            del wordTwo
            
        del wordCompArray
                
        return pxy, px, py

###################################################################
###################################################################

    def calc_PMI(self, wordOne, wordTwo):
        
        # Acquire the count value of each word
        print 'Acquire the count value of ' + wordOne + ' and ' + wordTwo + '...'
        if len(self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordOne]['freq'].values) > 0:
            word1_count = self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordOne]['freq'].values[0]
        else:
            word1_count = 0
            
        if len(self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordTwo]['freq'].values) > 0:
            word2_count = self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordTwo]['freq'].values[0]
        else:
            word2_count = 0

        print 'If both words are present....'
        if word1_count != 0 and word2_count != 0:
            px = float(word1_count) / float(self.wordlist_len)
            py = float(word2_count) / float(self.wordlist_len)
            
            del word1_count
            del word2_count

            # Acquire array of index for each word
            word1_index = self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordOne]['freq'].index.values
            word2_index = self.DF_wordlist.loc[self.DF_wordlist['List of Words'] == wordTwo]['freq'].index.values
            
            #del DF_wordlist

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
            
            pxy = float(coocurrence) / float(self.wordlist_len)
            
        else:
            pxy = 0
            px = 0
            py = 0
        
        return pxy, px, py
    
###################################################################
###################################################################

    def getWordComp(self, word_Array):

        wordCompArray = []
        pmiArray = []

        # Getting word combinations for comparisons
        for i in range(0, len(word_Array)):
            j = i + 1
            if i < len(word_Array)-1:
                while j < len(word_Array):
                    #print word_Array[i], word_Array[j]
                    wordCompArray.append([word_Array[i], word_Array[j]])
                    pmiArray.append(float(0))
                    j = j + 1
                    
        return wordCompArray, pmiArray
    
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
            
            del line
            
            print 'line: ' + repr(i) + ' arrayLine length: ' + repr(len(arrayLine))

            # Loop though each value of the line array and remove unnecessary strings
            for j in range(0,len(arrayLine)):

                # Append to output array
                contentArray.append(arrayLine[j].lower())
                
            del arrayLine
            
            
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
    
