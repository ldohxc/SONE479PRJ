from bs4 import BeautifulSoup
import Tokenizer 
import Normalizer

def getAllTokens(soup):    
    invertedIndex = {}
    fInfo = open('../invertedIndex/docInfo', 'a')
    fContent = open('../invertedIndex/docContent', 'a')
    # Create inverted index, loop through all articles in one file
    for doc in soup.find_all('reuters'):
        docId = int(doc['newid'].encode('utf8'))
        tokenCounter = 0
        if doc.body is not None:
            content = doc.body.text
            fContent.write (str(docId) + 'docContentStart' + content.encode('utf8') + 'docContentEnd')
            tokens = Tokenizer.tokenise(content)
            for token in tokens:
                # Normalization
                token = Normalizer.cleanUp(token)
                token = Normalizer.caseFolding(token)
                token = Normalizer.removeStopWord(token)
                token = Normalizer.stemming(token)
                if token != '':
                    tokenCounter += 1
                    # Add to the postings list if the word exists
                    if invertedIndex.has_key(token):
                        if invertedIndex[token].has_key(docId):
                            tf = invertedIndex[token][docId]
                            invertedIndex[token][docId] = tf +1
                        else:
                            invertedIndex[token][docId] = 1
                    else:
                        invertedIndex[token] = {docId:1}
        fInfo.write (str(docId) + ":" + str(tokenCounter) +'\n')
    fInfo.close()
    fContent.close()                
    return invertedIndex

def writeBlockToDisk(suffix):
    resourceFilePath = '../resources/reut2-' + suffix + '.sgm'
    #read and parse docutments
    document = open(resourceFilePath)
    soup = BeautifulSoup(document, 'html.parser')
    
    invertedIndex = getAllTokens(soup)
    
    #save the inverted index into disk
    f = open('../invertedIndex/index' + suffix, 'w')
    for k in sorted(invertedIndex):#sort the inverted index when writing to disk
        # add encode('utf8') to handle UnicodeEncodeError: 'ascii' codec can't encode character
        ss = ''
        for key, value in sorted(invertedIndex[k].items()):
            s = str(key) + '|' + str(value) + ', '
            ss += s
        f.write ((k + ":" + ss[:-2] +'\n').encode('utf8'))
    f.close()      
    print "Finish constructing inverted index for reut2-" + suffix 
    
# get dictionary word from the dictionary line
def getIndexWords(indexFileLines):
    indexWords = []
    numOfFiles = len(indexFileLines)
    for num in range(numOfFiles):
        if indexFileLines[num] != "":
            indexWords.insert(num, indexFileLines[num].rsplit(':', 1)[0])
        else:
            indexWords.insert(num, "")
    return indexWords

# get dictionary postings from the dictionary line
def getIndexPostings(indexFileLines):
    indexPostings = []
    numOfFiles = len(indexFileLines)
    for num in range(numOfFiles):
        if indexFileLines[num] != "":
            #[:-1] used to remove the new line character(-2 for windows)
            indexPostings.insert(num, indexFileLines[num].rsplit(':', 1)[1][:-1] + ', ')
        else:
            indexPostings.insert(num, "")
    return indexPostings

# get the smallest world in alpha-beta order
def getSmallestWord(indexWords):
    minWord = ''
    numOfFiles = len(indexWords)
    for num in range(numOfFiles):
        if indexWords[num] != '' and (indexWords[num] < minWord or minWord == ''):
            minWord = indexWords[num]
    return minWord
    
def mergeBlocks(numberOfBlocks):
    # Open a file to write to
    dictionary = open('../invertedIndex/dictionary', 'w')
    numOfFiles = numberOfBlocks
    # Create several lists to hold inverted index data
    indexFiles = []
    indexFileLines = []
    indexWords = []
    indexPostings = []
    
    # Open all the blocks and load one line from each block to memory
    for num in range(numOfFiles):
        suffix = '%0*d' % (3, num)
        filePath = '../invertedIndex/index' + suffix
        indexFiles.insert(num, open(filePath, 'r'))
        indexFileLines.insert(num, indexFiles[num].readline())
    
    # Merge blocks and write into a new file
    while any(indexFileLines):
        indexWords = getIndexWords(indexFileLines)
        indexPostings = getIndexPostings(indexFileLines)
        minWord = getSmallestWord(indexWords) 
        postings = ""
        # Select the word need to be merged from all blocks, 
        # merge them and write to the dictionary and advance their indexes
        for num in range(numOfFiles):
            if indexWords[num] == minWord:
                postings += indexPostings[num] 
                indexFileLines[num] = indexFiles[num].readline()
        # postings[:-2] remove last two character which is ', '
        dictionary.write ((minWord + ":" + postings[:-2] + '\n'))
    
    # Close all the files
    for num in range(numOfFiles):
        indexFiles[num].close()
    dictionary.close();
        
def main():
        
    print "Start constructing inverted index"
    
    numberOfBlocks = 22
    
    for num in range(numberOfBlocks):
        suffix = '%0*d' % (3, num)
        writeBlockToDisk(suffix)
    
    mergeBlocks(numberOfBlocks)
    
    print "Finish constructing all inverted index"
    
   
if __name__ == '__main__':
    main()    