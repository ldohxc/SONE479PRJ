import re

def tokenise(text):
	text = re.sub('\.\.+', " ", text)
	text = text.replace(', ', ' ').replace('(', ' ').replace(')',' ').\
                replace('"', ' ').replace('<', ' ').replace('>', ' ').\
                replace('+', ' ').replace('!', ' ').replace('?', ' ').\
                replace(':', ' ').replace(';', ' ').replace('/', ' ').\
                replace('\\', ' ').replace('[', ' ').replace(']', ' ').\
                replace('{', ' ').replace('}', ' ').replace('=', ' ').\
                replace('~', ' ').replace('=', ' ').replace('^', ' ').\
                replace('&', ' ').replace('$', ' ')
	return text.split()