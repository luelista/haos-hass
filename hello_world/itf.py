
# source: https://github.com/emfcamp/python-barcode/blob/master/barcode/itf.py

START = 'NnNn'
STOP = 'WnN'
CODES = ('NNWWN', 'WNNNW', 'NWNNW', 'WWNNN', 'NNWNW', 'WNWNN', 'NWWNN', 'NNNWW', 'WNNWN', 'NWNWN')
def build(code, narrow=2, wide=5):
	data = START
	for i in range(0, len(code), 2):
		bars_digit = int(code[i])
		spaces_digit = int(code[i+1])
		for j in range(5):
			data += CODES[bars_digit][j].upper()
			data += CODES[spaces_digit][j].lower()
	data += STOP
	raw = ''
	for e in data:
		if e == 'W':
			raw += '1' * wide
		if e == 'w':
			raw += '0' * wide
		if e == 'N':
			raw += '1' * narrow
		if e == 'n':
			raw += '0' * narrow
	return raw

def calccheckdigit(code):
	nsum = 0
	for i in range(len(code)):
		nsum += int(code[i]) * (3 if ((i % 2) == 0) else 1)
	return 10 - (nsum % 10)

