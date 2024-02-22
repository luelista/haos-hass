#!/usr/bin/env python3
# vim: noexpandtab 
#from hubarcode.code128 import Code128Encoder
import itf
import serial, socket
from my_font import my_font
import math
import random, string
import time
import logging

class PTouch:
	BARCODE_CONTROL = ["no change", "no barcode", "barcode only", "including barcode"]

	def __init__(self, serPort):
		if isinstance(serPort, tuple):
			logging.info("Connecting to PTouch over TCP/IP at %s:%d", *serPort)
			self.ser = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.ser.connect(serPort)
			self.isSerial = False
		elif isinstance(serPort, str):
			logging.info("Connecting to PTouch over Serial at %s, 9600 baud", serPort)
			self.ser = serial.Serial(port=serPort, baudrate=9600, dsrdtr=True, timeout=5)
			self.isSerial = True
		else:
			raise "Param must be tuple for TCP or string for serial port"
		self.initStatus = self.statusRequest()

	# Printer communication routines

	def initPrinter(self):
		self.writeBytes(0x1b, 0x40)  # ESC @

	def setMode(self, feedAmount=26, autocut=True, mirrorPrint=False):
		mode = feedAmount | (1<<6 if autocut else 0) | (1<<7 if mirrorPrint else 0)
		self.writeBytes(0x1b, 0x69, 0x4d, mode) # ESC i M

	def writeBytes(self, *b):
		#print(bytearray(b))
		#print(" ".join("%02X"%x for x in b))
		if self.isSerial:
			self.ser.write(bytearray(b))
		else:
			self.ser.send(bytearray(b))

	def print(self, eject=True):
		if eject:
			self.writeBytes(0x1a)
		else:
			self.writeBytes(0x0C) # Form Feed

	def setAbsPosition(self, pos):
		self.writeBytes(0x1b, 0x24, pos%256, pos>>8)

	def setRelPosition(self, pos):
		if pos < 0: pos = 65536 + pos
		self.writeBytes(0x1b, ord("\\"), pos%256, pos>>8)

	# bitmap is an array of pixels, where each pixel is an int of 1 or 0
	# each row is scanned left to right, then the rows top to bottom
	def sendFullImage(self, bitmap):
		# begriffsklärung: eine line besteht aus 24 rows, eine row ist 
		#  ein 1 dot hoch und so breit wie das bild breit ist
		lineheight = 24
		lines_ceil = int(math.ceil(self.dotswidth / lineheight))
		#lines = int(math.floor(self.dotswidth / lineheight))
		lines = lines_ceil
		# sollte eigentlich mit math.ceil funktionieren - allerdings meldet der Drucker dann den Fehler PRINT BUFFER FULL

		size = int(len(bitmap)/self.dotswidth)
		for line in range(lines):
			bmp = bytearray(lineheight * size)
			for y_pos in range(lineheight):
				line_start_idx = (line*lineheight+y_pos)*size
				if line_start_idx >= len(bitmap): continue
				for col in range(size):
					bmp[col *lineheight + y_pos] = bitmap[line_start_idx + col]
			self.send24RowImage(bmp)
			print("\n--> sent line %d of %d"%(line+1,lines_ceil))
			#time.sleep(0.8)
			if line != lines - 1:
				self.writeBytes(0x0d, 0x0a)
				time.sleep(0.8)

		# if lines_ceil > lines:
		# 	# letzte partielle Zeile
		# 	missing_rows = self.dotswidth - lineheight*lines
		# 	jump_up_rows = lineheight - missing_rows
		# 	print("missing=",missing_rows,"jump up:",jump_up_rows)
		# 	#self.setRelPosition(-jump_up_rows-10)
		# 	time.sleep(3.8)

		# 	bmp = bytearray(missing_rows * size)
		# 	for y_pos in range(missing_rows):
		# 		line_start_idx = (line*lineheight+y_pos)*size
		# 		if line_start_idx >= len(bitmap): continue
		# 		for col in range(size):
		# 			bmp[col *missing_rows + y_pos] = bitmap[line_start_idx + col]
		# 	self.send24RowImage(bmp)
		# 	print("\n--> sent last partial line of %d"%(lines_ceil))
		# 	time.sleep(0.8)
		# 	self.writeBytes(0x0d, 0x0a)
		# 	time.sleep(0.8)



	# bitmap is an array of pixels, where each pixel is an int of 1 or 0
	# each col is scanned top to bottom, then the cols left to right
	def send24RowImage(self, bitmap):
		size = len(bitmap)/24
		print(size)
		size=int(size)
		self.writeBytes(0x1b, 0x2a, 0x27, size%256, size>>8)
		bmp3 = bytearray(int(len(bitmap)/8))
		print(len(bmp3))
		for i in range(len(bmp3)):
			if (i%3)==0: print("")
			byte = 0
			for b in range(8):
				byte = byte | ((bitmap[i*8+7-b] & 0x01) << b)
			bmp3[i] = byte
			print(format(bmp3[i], '08b'), end="")
			if self.isSerial:
				self.writeBytes(byte)
		if self.isSerial:
			pass #self.ser.write(bmp3)
		else:
			self.ser.send(bmp3)
		self.statusRequest()

	def sendText(self, text):
		img = bytearray(len(text)*8*24)
		for i,char in enumerate(text):  # iterate through all chars of the text
			for j in range(8): # each char has 8 cols
				for k in range(8):  # each char is 8 rows high
					# each char uses 8*8*3 = 192 pixels
					# each col has 8*3 = 24 pixels
					# each row of the char is stretched to two rows
					bit = 0xff if my_font[ord(char)][k] & (1<<j) else 0x00
					img[i*8*8*3+j*24+k*3+0] = bit
					img[i*8*8*3+j*24+k*3+1] = bit
					img[i*8*8*3+j*24+k*3+2] = bit
		for x in range(len(img)):
			if x%24==0: print("")
			if img[x]==0:
				print("  ",end="")
			else:
				print("%02x"%(img[x]), end="")
		self.send24RowImage(img)
	


	# Printer status request

	def statusRequest(self):
		self.writeBytes(0x1b, 0x69, 0x53) # ESC i S
		
		if self.isSerial:
			status = self.ser.read(32)
		else:
			status = self.ser.recv(32)
		if len(status) == 0:
			raise Exception("No response from printer")
		header = status[0:8]
		err1 = status[8] # no tape, tape end, cutter jam
		err2 = status[9] # type change err, print buf full, transm err, recp buf full
		self.tapewidth = status[10]
		tapetype = status[11]
		reserved = status[12:15]
		mode = status[15]
		print_density_bytes = status[16]
		print_density = print_density_bytes & 0b1111
		barcode_control = (print_density_bytes & 0b110000) >> 4
		reserved2 = status[17:32]
		q = ""
		q += "Header:         "
		for x in header: q += "%02X "%(x)
		q += "\n"
		q += "Error 1:        "
		q += "%02X "%(err1)
		if err1 & 0x01: q += "NO_TAPE "
		if err1 & 0x02: q += "TAPE_END "
		if err1 & 0x04: q += "CUTTER_JAM "
		q += "\n"

		q += "Error 2:        "
		q += "%02X "%(err2)
		if err2 & 0x01: q += "TAPE_CHANGE_ERROR "
		if err2 & 0x02: q += "PRINT_BUFFER_FULL "
		if err2 & 0x04: q += "TRANSMISSION_ERROR "
		if err2 & 0x08: q += "RECEPTION_BUFFER_FULL "
		q += "\n"

		q += "Tape Width:     %d\n" % (self.tapewidth)
		q += "Tape Type:      %d\n" % (tapetype)
		q += "Mode:           %d\n" % (mode)
		q += "Print Density:  %d\n" % (print_density)
		q += "Barcode Ctrl:   %d (%s)\n" % (barcode_control, PTouch.BARCODE_CONTROL[barcode_control])
		print(q)
		self.statusInfoText = q

		# Available dots, copied from manual
		if self.tapewidth == 24:
			self.dotswidth = 128
		elif self.tapewidth == 18:
			self.dotswidth = 85
		elif self.tapewidth == 12:
			self.dotswidth = 57
		elif self.tapewidth == 9:
			self.dotswidth = 49
		elif self.tapewidth == 6:
			self.dotswidth = 28
		return q


	# Buffer operations
	
	def getFullImageWidth(self):
		return self.dotswidth

	def makeBuffer(self, cols):
		self.buffer = bytearray(cols*self.dotswidth)
		self.buffersize = cols

	def printBuffer(self):
		self.sendFullImage(self.buffer)
		#self.print(False)

	def setPixel(self, line, col, onoff):
		self.buffer[line*self.buffersize + col] = onoff
	def textToBuffer(self,x, y, stretch, text):
		(stretchX, stretchY) = stretch
		for i,char in enumerate(text):  # iterate through all chars of the text
			for j in range(8): # each char has 8 cols
				for k in range(8):  # each char is 8 rows high
					# each char uses 8*8*3 = 192 pixels
					# each col has 8*3 = 24 pixels
					# each row of the char is stretched to two rows
					bit = 0xff if my_font[ord(char)][k] & (1<<j) else 0x00
					col = x + (i*8+j)*stretchX
					line = y + k*stretchY
					for sx in range(stretchX):
						for sy in range(stretchY):
							if line+sy < self.dotswidth:
								self.buffer[ (line+sy) * self.buffersize + col+sx  ] = bit

	def code128ToBuffer(self, x, y, stretch, text):
		(barwidth, height)=stretch
		dm = Code128Encoder(text)
		for c in range(len(dm.bars)):
			col = x + c*barwidth
			bit = dm.bars[c]
			for sx in range(barwidth):
				for sy in range(height):
					self.buffer[ (y+sy) * self.buffersize + col+sx  ] = bit
				
	def itfToBuffer(self, x, y, stretch, text):
		(barwidth, height)=stretch
		dm = itf.build(text)
		for c in range(len(dm)):
			bit = 0xff if dm[c] == "1" else 0x00
			for sy in range(height):
				self.buffer[ (y+sy) * self.buffersize + x+c  ] = bit
				
	def dataMatrixToBuffer(self, x, y, stretch, text):
		from hubarcode.datamatrix import DataMatrixEncoder
		from hubarcode.datamatrix.renderer import DataMatrixRenderer
		dm = DataMatrixEncoder(text)
		dmtx = DataMatrixRenderer(dm.matrix)
		for r in range(len(dmtx.matrix)):
			line = y + r*stretch
			for c in range(len(dmtx.matrix)):
				col = x + c*stretch
				bit = dmtx.matrix[r][c]
				for sx in range(stretch):
					for sy in range(stretch):
						self.buffer[ (line+sy) * self.buffersize + col+sx  ] = bit
						print(bit,end="")
			print("")
				
	
	def textWidth(self, stretch, text):
		(stretchX, stretchY) = stretch
		return len(text) * stretchX * 8
	
	def showBufferAscii(self):
		for row in range(self.dotswidth):
			for col in range(self.buffersize):
				print('.' if self.buffer[row*self.buffersize + col] == 0 else '#', end='')
			print("|")

	def showBufferTk(self):
		BLACK=[0,0,0]
		RED=[255,0,0]
		BLUE=[0,0,255]
		WHITE=[255,255,255]
		# dot ruler
		ruler5 = [ RED if i % 5 == 0 else WHITE for i in range(self.buffersize)]
		ruler10 = [ RED if i % 10 == 0 else WHITE for i in range(self.buffersize)]
		ruler50 = [ RED if i % 50 == 0 else WHITE for i in range(self.buffersize)]

		# cm ruler (180 dpi => ~ 71dots = 1cm)
		rulercm = [ BLUE if i % 71 == 0 else WHITE for i in range(self.buffersize)]

		ruler=ruler50*5+ruler10*5+ruler5*5+rulercm*7

		buffer = [ WHITE if self.buffer[row*self.buffersize + col] == 0 else BLACK 
						for row in range(self.dotswidth)
						for col in range(self.buffersize)]
		from graphicPreview import displayGraphic
		return displayGraphic(self.buffersize, self.dotswidth+22, ruler + buffer, self.statusInfoText)

	def writeBufferXPM2(self, fileDesc):
		fileDesc.write(b"! XPM2\n%d %d 2 1\n* c #000000\n. c #ffffff\n" % (self.buffersize, self.dotswidth, ))
		for row in range(self.buffersize):
			data = [b'.' if self.buffer[row*self.buffersize + col] == 0 else b'*' for col in range(self.dotswidth)]
			fileDesc.write(b"".join(data) + b"\n")

	def writeBufferPBM(self, fileDesc):
		fileDesc.write("P1\n%d %d\n" % (self.buffersize, self.dotswidth, ))
		for row in range(self.dotswidth):
			data = ['0' if self.buffer[row*self.buffersize + col] == 0 else '1' for col in range(self.buffersize)]
			fileDesc.write(" ".join(data) + "\n")

	def readBufferPBM(self, fileDesc):
		headers = []
		while len(headers) < 2:
			line = fileDesc.readline().strip()
			if line.startswith("#"): continue
			headers.append(line)
		assert(headers[0].strip() == "P1")
		header2 = headers[1].split(" ")
		width, height = int(header2[0]), int(header2[1])
		if height != self.dotswidth:
			raise Error("Image height mismatch (tape: %d, image: %d)"%(self.dotswidth,height))
		self.makeBuffer(width)
		content = fileDesc.read().strip().replace(" ","").replace("\n","").replace("\r","")
		for i in range(self.dotswidth * self.buffersize):
			self.buffer[i] = int(content[i])






