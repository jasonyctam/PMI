import PMI_Analysis as pmi
import os
import time

startTime = time.time()

corpus_path = r'Files/'

textlist = [os.path.join(corpus_path, fn) for fn in sorted(os.listdir(corpus_path))]
for i in range(0,len(textlist)):
    print textlist[i]

textWindow = 500

print 'Starting PMI Analysis...'

wordList = []

wordArray = ['geben', 'sogar', 'tatsache']
wordArray2 = ['russisch', 'nehmen', 'letzt']

wordList.append(wordArray)
wordList.append(wordArray2)

allWordCompArray = []
allPMIVals = []

print 'Filling word combinations...'
for k in range(0,len(wordList)):
    wordCompArray = []
    PMI_Vals = []
    word_Array = wordList[k]
    for i in range(0, len(word_Array)):
        j = i + 1
        if i < len(word_Array)-1:
            while j < len(word_Array):
                print word_Array[i], word_Array[j]
                wordCompArray.append([word_Array[i], word_Array[j]])
                PMI_Vals.append(float(0))
                j = j + 1
    allWordCompArray.append(wordCompArray)
    allPMIVals.append(PMI_Vals)
    del word_Array
    del wordCompArray
    del PMI_Vals
    
resultWordCompArray = []   
resultPMIArray = []

for i in range(0,len(textlist)):
    print 'Processing ' + textlist[i]
    PMI = pmi.PMI_Analysis(textlist[i], textWindow)    
    wordCompArray, PMI_VAL = PMI.getPMI_Average(wordList)
    resultPMIArray.append(PMI_VAL)
    resultWordCompArray.append(wordCompArray)
    del wordCompArray
    del PMI_VAL
    del PMI
    
for i in range(0,len(textlist)):
    for j in range(0, len(allWordCompArray)):
        WORD_COMP = allWordCompArray[j]
        for k in range(0,len(WORD_COMP)):
            if WORD_COMP[k][0] == allWordCompArray[j][k][0] and WORD_COMP[k][1] == allWordCompArray[j][k][1]:
                PMI_Val = resultPMIArray[i][j][k] + allPMIVals[j][k]
                allPMIVals[j][k] = PMI_Val
                del PMI_Val
        del WORD_COMP

PMI_AVG = []

for i in range(0,len(allPMIVals)):
    PMI_Vals = allPMIVals[i]
    row = []
    
    for j in range(0,len(PMI_Vals)):
        row.append(PMI_Vals[j]/float(len(textlist)))
        
    PMI_AVG.append(row)
    del PMI_Vals
    del row
        
for i in range(0,len(allWordCompArray)):
    print 'Results for: ' + repr(wordList[i])
    row = allWordCompArray[i]
    for j in range(0,len(row)):
        print 'PMI(' + row[j][0] + ',' + row[j][1] + '): ' + repr(PMI_AVG[i][j])
    del row

endTime = time.time()

print "Time elapsed: " + repr(endTime-startTime)
