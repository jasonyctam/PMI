import PMI_Analysis as pmi
import time

startTime = time.time()

corpus_path = r'Files/'
textWindow = 500

print 'Starting PMI Analysis...'

word_Array = ['geben', 'sogar', 'tatsache']

PMI = pmi.PMI_Analysis(corpus_path, textWindow)    
WORD_COMP, PMI_AVG = PMI.getPMI_Average(word_Array)

for i in range(0,len(WORD_COMP)):
    print 'PMI(' + WORD_COMP[i][0] + ',' + WORD_COMP[i][1] + '): ' + repr(PMI_AVG[i])

endTime = time.time()

print "Time elapsed: " + repr(endTime-startTime)