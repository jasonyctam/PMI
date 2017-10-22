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

word_Array = ['geben', 'sogar', 'tatsache']
wordCompArray = []
PMI_Vals = []
pmi_all_Array = []

print 'Filling word combinations...'
for i in range(0, len(word_Array)):
    j = i + 1
    if i < len(word_Array)-1:
        while j < len(word_Array):
            print word_Array[i], word_Array[j]
            wordCompArray.append([word_Array[i], word_Array[j]])
            PMI_Vals.append(float(0))
            j = j + 1

for i in range(0,len(textlist)):
    print 'Processing ' + textlist[i]
    PMI = pmi.PMI_Analysis(textlist[i], textWindow)    
    WORD_COMP, PMI_VAL = PMI.getPMI_Average(word_Array)
    pmi_all_Array.append(PMI_VAL)
    del PMI_VAL
    del PMI
    
    
for i in range(0,len(textlist)):
    for j in range(0,len(WORD_COMP)):
        if WORD_COMP[j][0] == wordCompArray[j][0] and WORD_COMP[j][1] == wordCompArray[j][1]:
            PMI_Val = pmi_all_Array[i][j] + PMI_Vals[j]
            PMI_Vals[j] = PMI_Val
            del PMI_Val

PMI_AVG = []

for i in range(0,len(PMI_Vals)):
    PMI_AVG.append(PMI_Vals[i]/float(len(textlist)))
        
for i in range(0,len(wordCompArray)):
    print 'PMI(' + wordCompArray[i][0] + ',' + wordCompArray[i][1] + '): ' + repr(PMI_AVG[i])

endTime = time.time()

print "Time elapsed: " + repr(endTime-startTime)
