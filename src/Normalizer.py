import re
from nltk import PorterStemmer

def cleanUp(token):
	frontApostrophe = re.compile('^\'.*')
	frontComma = re.compile('^,.*')
	frontAt = re.compile('^@.*')
	frontDash = re.compile('^\-.*')
	frontDoubleDash = re.compile('^\-\-.*')
	endWithDot = re.compile('^[^\.]*\.$')
	endWithComma = re.compile('.*,$')
	endWithApostrophe = re.compile('.*\'$')
	noLetterAndNumber = re.compile('[\W_]+$')
	number = re.compile('^\d{0,3}(,?\d{3})*(.\d+)?$')
	numberStart = re.compile('^\d{1,3}(,?\d{3})*(.\d+)?.*')
	
	if frontApostrophe.match(token):
		token = token[1:]
		
	if frontComma.match(token):
		token = token[1:]
	
	if frontAt.match(token):
		token = token[1:]
			
	if frontDoubleDash.match(token):
		token = token[2:]
			
	if frontDash.match(token):
		token = token[1:]
		
	if endWithComma.match(token):
		token = token[:-1]
	
	if endWithDot.match(token):
		token = token[:-1]
	
	if endWithApostrophe.match(token):
		token = token[:-1]
			
	if noLetterAndNumber.match(token):
		token = ''	
		
	if number.match(token):
		token = ''
	# If it is not a number, remove the dot
	else:
		token = token.replace('.', '')
		
	if numberStart.match(token):
		token = ''
		
	return token

def caseFolding(token):
	token = token.lower()
	return token

def removeStopWord(token):
	#with open('../resources/30words.stop', 'r') as f:
	with open('../resources/150words.stop', 'r') as f:
		stopWords = f.read().split()
	if token in stopWords:
		token = ''
	f.close()
	return token

def stemming(token):
	stemmer=PorterStemmer()
	token = stemmer.stem(token)
	return token