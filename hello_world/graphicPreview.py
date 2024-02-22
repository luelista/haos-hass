from tkinter import *
import random, sys

class App:
    def closedlg(self, response):
        self.dialog_result = response
        self.t.withdraw()
        self.t.destroy()
    def __init__(self, t, width, height, rgb_colors, infotext):
        self.width = width
        self.height = height
        self.t = t
        self.i = PhotoImage(width=self.width,height=self.height)
        pixels=" ".join(("{"+" ".join(('#%02x%02x%02x' %
            tuple(next(rgb_colors)) for i in range(self.width)))+"}" for j in range(self.height)))
        self.i.put(pixels,(0,0,self.width-1,self.height-1))
        txt = Text(t)
        txt.pack(side=RIGHT)
        txt.insert(END, infotext)
        
        c = Canvas(t, width=self.width, height=self.height); c.pack()
        c.create_image(0, 0, image = self.i, anchor=NW)
        ok = Button(t, text="OK", command=lambda: self.closedlg(True)); ok.pack(side=LEFT)
        cancel = Button(t, text="Cancel", command=lambda: self.closedlg(False)); cancel.pack(side=RIGHT)





def displayGraphic(width, height, graphic, infotext=""):
    t = Tk()
    a = App(t, width, height, iter(graphic), infotext)
    t.mainloop()
    return a.dialog_result

def displayRandom():
    w = 320
    h = 200
    rgb_colors = ([random.randint(0,255) for i in range(0,3)] for j in range(0,w*h))
    return displayGraphic(w,h,rgb_colors)

if __name__ == '__main__':
    res = displayRandom()
    sys.exit(0 if res else 1)
