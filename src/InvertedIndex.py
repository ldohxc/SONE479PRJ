from bs4 import BeautifulSoup
import os
import Tokenizer 
import Normalizer

PAGEID = 1

def incrementPageId():
    global PAGEID
    PAGEID += 1

def parseAllHtml(resourcesPath, invertedIndex):
    # Loop through everything in the directory
    for f in os.listdir(resourcesPath):
        pathname = os.path.join(resourcesPath, f)
        # If it is a folder, loop through the folder
        if os.path.isdir(pathname):
            invertedIndex = parseAllHtml(pathname, invertedIndex)
        # If is a file, parse it.
        else:
            invertedIndex = parseSingleHtml(pathname, invertedIndex)
            incrementPageId()
    return invertedIndex

def parseSingleHtml(filePath, invertedIndex):

    newInvertedIndex = invertedIndex
    # Read and parse page, decode used to handle special characters
    page = open(filePath).read().decode('utf-8', 'ignore')
    soup = BeautifulSoup(page, 'html.parser')
    # Kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out
    if soup.body is not None:
        # Add space for some between some tag, such as <li>   
        body = " ".join(soup.body.strings)
        # Remove all extra space from the body and concatenate each line
        content = ""
        for line in body.splitlines():
            line = line.strip()
            if line:
                content += line + " "
        content = content[:-1]
        # Construct a id for each html page
        prefix = filePath.split('/')[2]
        pageFolderPath = '/'.join(filePath.split('/')[3:])
        #
        newInvertedIndex = appendAllTokens(prefix, content, invertedIndex)
        # Store the page content in one file for sentiment analysis
        appendPageContent(prefix, content)
        # Store the map between page id and page folder path
        appendPageId(prefix, pageFolderPath)
    return newInvertedIndex

def appendAllTokens(prefix, content, invertedIndex): 
    tokenCounter = 0
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
                if invertedIndex[token].has_key(PAGEID):
                    tf = invertedIndex[token][PAGEID]
                    invertedIndex[token][PAGEID] = tf +1
                else:
                    invertedIndex[token][PAGEID] = 1
            else:
                invertedIndex[token] = {PAGEID:1} 
    # Store the number of tokens for each page in one file for tf-idf calculation
    appendPageInfo(prefix, tokenCounter)
    
    return invertedIndex
    
def appendPageContent(prefix, content):
    directory = '../invertedIndex/' + prefix
    if not os.path.exists(directory):
        os.makedirs(directory)
    fContent = open(directory + '/PageContent', 'a')
    fContent.write (str(PAGEID) + 'docContentStart' + content.encode('utf8') + 'docContentEnd\n')
    fContent.close() 

def appendPageInfo(prefix, tokenCounter):
    directory = '../invertedIndex/' + prefix
    if not os.path.exists(directory):
        os.makedirs(directory)
    fInfo = open(directory + '/PageInfo', 'a')
    fInfo.write (str(PAGEID) + ":" + str(tokenCounter) +'\n')
    fInfo.close() 

def appendPageId(prefix, pageFolderPath):
    directory = '../invertedIndex/' + prefix
    if not os.path.exists(directory):
        os.makedirs(directory)
    fInfo = open(directory + '/PageId', 'a')
    fInfo.write (str(PAGEID) + ":" + pageFolderPath +'\n')
    fInfo.close()

def writeToDictionary(prefix, invertedIndex):
    directory = '../invertedIndex/' + prefix
    if not os.path.exists(directory):
        os.makedirs(directory)        
    #save the inverted index into disk
    f = open(directory + '/dictionary', 'w')
    for k in sorted(invertedIndex):#sort the inverted index when writing to disk
        # add encode('utf8') to handle UnicodeEncodeError: 'ascii' codec can't encode character
        ss = ''
        for key, value in sorted(invertedIndex[k].items()):
            s = str(key) + '|' + str(value) + ', '
            ss += s
        f.write ((k + ":" + ss[:-2] +'\n').encode('utf8'))
    f.close() 

def storeCategories(prefix, resourcesPath):
    # Loop through everything in the directory
    directory = '../invertedIndex/' + prefix
    if not os.path.exists(directory):
        os.makedirs(directory)
    fCat = open(directory + '/PageCategory', 'w')
    for f in os.listdir(resourcesPath):
        pathname = os.path.join(resourcesPath, f)
        # If it is a folder, loop through the folder
        if os.path.isdir(pathname):
            print f
            fCat.write (f + '\n')
    fCat.close()    
       
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
    
    resourcesPath = '../resources/McGillAlt'
    invertedIndex = {}  
    prefix = resourcesPath.split('/')[2]
    
    #storeCategories(prefix, resourcesPath)
    invertedIndex = parseAllHtml(resourcesPath, invertedIndex)
           
    writeToDictionary(prefix, invertedIndex)
    
    print "Finish constructing all inverted index"
    
   
if __name__ == '__main__':
    main()    