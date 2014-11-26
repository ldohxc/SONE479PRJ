import sys
import math
import Tokenizer
import Normalizer

def error(message):
    sys.stderr.write("error: %s\n" % message)
    sys.exit(1)
    
def loadDictionary():
    dictionary = {}
    with open('../invertedIndex/dictionary', 'r') as d:
        for line in d:
            token = line.split(':')[0]
            dictionary[token] = {}
            for doc in line.split(':')[1][:-1].split(', '):
                dictionary[token][int(doc.split('|')[0])] = int(doc.split('|')[1])
    d.close()
    return dictionary

def loadDocInfo():
    docInfo = {}
    totalNumberOfToken = 0
    with open('../invertedIndex/docInfo', 'r') as di:
        for line in di:
            docId = int(line.split(':')[0])
            docLength = int(line.split(':')[1])
            docInfo[docId] = docLength
            totalNumberOfToken += docLength
    di.close()
    totalNumberOfDoc = len(docInfo)
    docInfo['average'] = totalNumberOfToken/totalNumberOfDoc
    return docInfo

def loadDocContent():
    docContents = {}
    with open('../invertedIndex/docContent', 'r') as dc:
        # [:-13] removes the last docContentEnd
        contents = dc.read()[:-13].split('docContentEnd')
        for content in contents:
            docContents[int(content.split('docContentStart')[0])] = content.split('docContentStart')[1]
    dc.close()
    return docContents

def normalizeToken(word):
    word = Normalizer.cleanUp(word)
    word = Normalizer.caseFolding(word)
    word = Normalizer.removeStopWord(word)
    word = Normalizer.stemming(word)
    return word

def tokenizeAndNormalizeQuery(query):
    # Tokenize the query
    tokens = Tokenizer.tokenise(query)
    normalizedTokens = []
    # Loop through all tokens in the query
    for token in tokens:
        token = normalizeToken(token)
        if token != "":
            normalizedTokens.append(token)
    return normalizedTokens

def getRankScore(dictionary, docInfo, docId, queryTokens):
    rsv = 0
    n = len(docInfo)-1 #  total number of documents
    aveDocLen = docInfo.get('average') # average document length
    docLen = docInfo.get(docId) # document length
    k = 1.2 # between 1.2 and 2
    b = 0.75 # between 0 and 1
    for token in queryTokens:
        if dictionary.has_key(token):
            df = len(dictionary.get(token)) # document frequency
            tf = 0
            if dictionary.get(token).has_key(docId): # term frequency
                tf = dictionary.get(token).get(docId)
            rsv = rsv + math.log(n/df, 10) * (((k + 1) * tf)/(k * ((1 - b) + b * (docLen/aveDocLen)) + tf))

    return rsv

def intersection(list1, list2):
    result = []
    if list1 is not None and list2 is not None:
        list1Index = 0
        list2Index = 0
        while list1Index < len(list1) and list2Index < len(list2):
            # Convert docID to integer
            list1Value = int(list1[list1Index])
            list2Value = int(list2[list2Index])
            # If equal, add to result and advance both index
            if list1Value == list2Value:
                result.append(list1[list1Index])
                list1Index += 1
                list2Index += 1
            # If not equal, advance the smaller value's index
            elif list1Value < list2Value:
                list1Index += 1
            else:
                list2Index += 1
    return result

def union(list1, list2):
    result = []
    if list1 is not None and list2 is not None:
        list1Index = 0
        list2Index = 0
        while list1Index < len(list1) or list2Index < len(list2):
            # If both lists have elements, compare them
            if list1Index < len(list1) and list2Index < len(list2):
                # Convert docID to integer
                list1Value = int(list1[list1Index])
                list2Value = int(list2[list2Index])
                # If equal, add once and advance both index
                if list1Value == list2Value:
                    result.append(list1[list1Index])
                    list1Index += 1
                    list2Index += 1
                # If not equal, add to the result and advance the index
                elif list1Value < list2Value:
                    result.append(list1[list1Index])
                    list1Index += 1
                else:
                    result.append(list2[list2Index])
                    list2Index += 1
            # If just one list have elements, add to the result
            elif list2Index == len(list2):
                result.append(list1[list1Index])
                list1Index += 1
            else:
                result.append(list2[list2Index])
                list2Index += 1
    return result

def negation(mylist):
    result = []
    index = 0
    # Loop through the whole docId, add the complement to the result
    for docid in range (1, 21579):
        if mylist is not None and index < len(mylist):
            value = int(mylist[index])
            if docid == value:
                index += 1
            else:
                result.append(str(docid))
        else:
            result.append(str(docid))
    return result

def processQuery(query, dictionary, docInfo):
    # Tokenize the query
    normalizedTokens = tokenizeAndNormalizeQuery(query)
    result = []
    rankedResult = {}
    isFirstToken = True
    # Loop through all tokens in the query
    for token in normalizedTokens:
        # For the first token, copy the postings list to the result
        if isFirstToken:
            result = sorted(dictionary.get(token).keys())
            isFirstToken = False
        # For the rest of tokens, do a intersection between its postings list and previous result
        else:
            result = union(result, sorted(dictionary.get(token).keys()))    

    for doc in result:
        rankScore = getRankScore(dictionary, docInfo, doc, normalizedTokens)
        if rankedResult.has_key(rankScore):
            rankedResult[rankScore].append(doc)
        else:
            rankedResult[rankScore] = [doc]

    return rankedResult
    
def main():
    
    dictionary = loadDictionary()
    docInfo = loadDocInfo()
    docContents = loadDocContent()
    numberOfDisplay = -1 
    query =  sys.argv[1]
    
    if len(sys.argv) == 3:
        numberOfDisplay = int(sys.argv[2])
        
    result = processQuery(query, dictionary, docInfo)
    
    if len(result) == 0:
        print "No article is found."
    else:
        numberOfResult = sum([len(v) for k,v in result.iteritems()])
        if numberOfDisplay < 0 or numberOfDisplay > numberOfResult:
            numberOfDisplay = numberOfResult
        print "There are " + str(numberOfResult) + " articles matching the query \"" + query + "\"."
        # sort the result by its ranking score
        counter = 0
        innerBroken = False
        for score in sorted(result.keys(), reverse=True):
            for doc in result[score]:
                if counter < numberOfDisplay:
                    print "document: " + str(doc) + " (" + str(score) + ") " + "\n" + docContents.get(doc)
                else:
                    innerBroken = True
                    break
                counter += 1
            if innerBroken == True:
                break
                
                

if __name__ == "__main__":
    main()
