#!/usr/bin/env python
import sys
import os
import string
from Tkinter import *
import tkFont
""" Guidelines for python script header formatting:

The idea of the GUI class is that it provides a graphical editor of
only the variables contained in the header of a python script, and
that it can also be used to launch the script.

Usage:
  python xmipp_protocol_gui.py script.py

Where the header of script.py should be organized as follows:

Obligatory:
    * Include a {end-of-header} label at the end of the header
    * Variable declaration (visible in GUI): Variablename=XXX
          o If XXX is True or False, the variable is considered as a
            Boolean (yes/no button in GUI)
          o If XXX starts with \" or \', the variable is considered as
            a string (text field in GUI)
          o If XXX is a number, the variable is considered as a number
            (text field in GUI) 
    * The first single comment line above each variable (starting with a #)
      will be displayed in the GUI, as a label left from the variable entry field

    * More detailed help for each variable can be placed between the comment
      line and the variable declaration line using \""" ...\""".
      This text will become visible in the GUI by pressing a -what's this?-
      button, at the right side of the variable entry field.
      !!!NOTE that the first character in newlines within these comments
      should start with spaces or a tab!!!
    * An {expert} label on the comment line (#) marks the option as -expert-
      (by default not shown in the GUI, unless you press the -show expert options-
      button, at the left side of the variable entry field. Then, they will be
      shown in yellow.
    * A {file} or {dir} label on the comment line (#) marks the option as a
      Filename or Directory, and will add a corresponding Browse-button to the GUI
      Note that this button return absolute paths
    * A {list}|option A|option B|option C| label on the comment line (#) marks 
      the option as a radio-list button. The selected variable should be one of the options indicated.
      The number of different options is not limited.
    * A {hidden} label on the comment line (#) marks the option as -hidden-

Optional:

    * A {please cite} label on a comment line (starting with a #) will display
      a message at the top of the protocol stating -If you publish results obtained with
      this protocol, please cite-, followed by the text on rest of the comment line.
      If more than one citation lines are present, they will all be displayed.
      DONT use very long citations, as this will results in an ugly gui.
    * Include a {section} label on a comment line (starting with a #) to separate
      variables by a blue line + the corresponding title in the GUI 

"""
FontName = "Helvetica "
TextSectionColor = "blue4"
TextCitationColour = "dark olive green"
BackgroundColour = "white"
LabelBackgroundColor = BackgroundColour
HighlightBackgroundColour = BackgroundColour
ButtonBackgroundColor = "LightBlue"
ButtonActiveBackgroundColor = "LightSkyBlue"
EntryBackgroundColour = "lemon chiffon" 
ExpertLabelBackgroundColor = "light salmon"
ListSelectColour = "DeepSkyBlue4"
BooleanSelectColour = "DeepSkyBlue4"
MaxHeight = 600
MaxWidth = 800
WrapLenght = MaxWidth / 2

# A scrollbar that hides itself if it's not needed.
class AutoScrollbar(Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Scrollbar.set(self, lo, hi)
        
class ProtocolVariable():
    def __init__(self):
        self.name = None
        self.value = None
        self.comment = None
        self.help = None
        self.tags = {}
        self.condition_name = None
        self.condition_value = None
    
    def setTags(self, tags):
        for k, v in tags:
            self.tags[k] = v
            
    def isExpert(self):
        return 'expert' in self.tags.keys()
    
    def isSection(self):
        return 'section' in self.tags.keys()
    
class ProtocolWidget():
    def __init__(self, master, var):
        self.master = master
        # Store real tk widgets
        self.widgetlist = []
        self.variable = var
    
def createWidget(self, var):
    w = ProtocolWidget(self.frame, var)
    self.widgetlist.append(w)
    
    for k, v in var.tags.iteritems():
        print "tag %s -> %s" % (k, v)
        if k == 'section':
            self.is_section = True
        elif k == 'file':
            self.is_file = True
        elif k == 'dir':
            self.is_dir = True
        elif k == 'list':
            self.is_list = True
            self.list_choices = v.split('|')
        elif k == 'condition':
            self.condition = v
        elif k == 'please_cite':
            self.is_cite = True
        else:
            pass
            #Other variables, guess the type from value
        
class ProtocolGUI():
    def __init__(self, script):
        self.variablesDict = {}
        self.widgetsList = []
        self.pre_header_lines = []
        self.header_lines = []
        self.post_header_lines = []
        self.have_publication = False
        self.expert_mode = False
        self.scriptname = script
        self.lastrow = 0
    
    def readProtocolScript(self):
        begin_of_header = False
        end_of_header = False        
        f = open(self.scriptname, 'r')
        for line in f:
            #print "LINE: ", line
            if not begin_of_header:
                self.pre_header_lines.append(line)
            elif not end_of_header:
                #print "LINE: ", line
                self.header_lines.append(line)
            else:
                self.post_header_lines.append(line)                
            if line.find('{begin_of_header}') != -1:
                begin_of_header = True
            if line.find('{end_of_header}') != -1:
                end_of_header = True
        f.close()
        
        if not begin_of_header:
            raise Exception('{begin_of_header} tag not found in protocol script: %s' % script)
        if not end_of_header:
            raise Exception('{end_of_header} tag not found in protocol script: %s' % script)
                
    def parseHeader(self):
        #REGURLAR EXPRESSION TO PARSE VARIABLES DEFINITION
        import re
        #Comment regex, match lines starting by # and followed by tags with values
        #of the form {tag}(value) and ending with the comment for the GUI    
        reComment = re.compile('#\s*((?:{\s*\w+\s*}(?:\([^)]*\))?)*)?\s*(.*)')
        #This take all tags and values from previous one
        reTags = re.compile('(?:{\s*(\w+)\s*}(?:\(([^)]*)\))?)')
        #This is the regular expression of a Variable
        #possible values are: True, False, String with single and double quotes and a number(int or float) 
        reVariable = re.compile('(\w+)\s*=\s*(True|False|".*"|\'.*\'|\d+|)')
        self.variablesDict = {}
        self.widgetsList = []
        
        index = 0;
        count = len(self.header_lines)
        while index < count:
            line = self.header_lines[index].strip()
            index += 1
            #Parse the comment line
            match = reComment.search(line)
            if match:
                v = ProtocolVariable()
                v.comment = match.group(2)
                #w = ProtocolWidget(match.group(2), self)
                #self.widgetsList.append(w)
                #print match.groups()
                if match.group(1) != '':
                    tags = reTags.findall(match.group(1))
                    v.setTags(tags)
                    print 'tags', tags
                    print 'v.tags', v.tags
                    
                if not v.isSection():
                    #This is a variable, try to get help string
                    helpStr = ''
                    if index < count and self.header_lines[index].startswith('"""'):
                        while index < count and not helpStr.endswith('"""\n'):
                            line = self.header_lines[index]
                            helpStr += line
                            index += 1
                        v.help = helpStr
                        
                    if index < count:
                        line = self.header_lines[index].strip()
                        match2 = reVariable.match(line)
                        if match2:
                            v.name, v.value = (match2.group(1), match2.group(2))
                            #w.setVariable(match2.group(1), match2.group(2))
                            self.variablesDict[v.name] = v.value
                            index += 1
                createWidget(self, v)            
                
        
            
    def prepareCanvas(self):
        # Stuff to make the scrollbars work
        vscrollbar = AutoScrollbar(self.master)
        vscrollbar.grid(row=0, column=1, sticky=N + S)
        hscrollbar = AutoScrollbar(self.master, orient=HORIZONTAL)
        hscrollbar.grid(row=1, column=0, sticky=E + W)
        self.canvas = Canvas(self.master, background=BackgroundColour,
                        yscrollcommand=vscrollbar.set,
                        xscrollcommand=hscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky=N + S + E + W)
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        self.frame = Frame(self.canvas, background=BackgroundColour)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)
            
    def createCanvas(self):
        # Launch the window
        self.canvas.create_window(0, 0, anchor=NW, window=self.frame)
        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all")) 
        
    def resize(self):
        height = self.frame.winfo_reqheight() + 25
        width = self.frame.winfo_reqwidth() + 25
        if height > MaxHeight:
           height = MaxHeight
        if width > MaxWidth:
           width = MaxWidth
        self.master.geometry("%dx%d%+d%+d" % (width, height, 0, 0))
    
    def addSeparator(self, row):
        self.l1 = Label(self.frame, text="", bg=LabelBackgroundColor)
        self.l1.grid(row=row)
        self.l2 = Frame(self.frame, height=2, bd=1, bg=TextSectionColor, relief=RIDGE)
        self.l2.grid(row=row + 1, column=0, columnspan=self.columnspantextlabel + 3, sticky=EW)
        self.l3 = Label(self.frame, text="", bg=LabelBackgroundColor)
        self.l3.grid(row=row + 2)
    
    def fillHeader(self):
        import os, sys
        self.morehelp = StringVar()
        self.whichfile = StringVar()
        # Script title
        programname = self.scriptname.replace('.py', '')
        self.master.title(programname)
        headertext = 'GUI for Xmipp %s \n Executed in directory: %s' % (programname, os.getcwd())
        self.l1 = Label(self.frame, text=headertext, fg=TextSectionColor, bg=LabelBackgroundColor)
        self.l1.configure(wraplength=WrapLenght)
        self.l1.grid(row=0, column=0, columnspan=6, sticky=E+W)
        if (self.have_publication):
            headertext = "If you publish results obtained with this protocol, please cite:"
            for pub in self.publications:
                headertext += '\n' + pub.replace('\n', '')
            self.l2 = Label(self.frame, text=headertext, fg=TextCitationColour, bg=LabelBackgroundColor)
            self.l2.configure(wraplength=WrapLenght)
            self.l2.grid(row=self.getRow(), column=0, columnspan=5, sticky=EW)
        self.addSeparator(self.getRow())
            
    def fillWidgets(self):
        for w in self.widgetsList:
            w.addWidgets()
    
    def addButton(self, text, cmd, underline, row, col, sticky):
        btn = Button(self.frame, text=text, command=cmd, underline=underline,
                     bg=ButtonBackgroundColor, activebackground=ButtonActiveBackgroundColor)
        btn.grid(row=row, column=col, sticky=sticky)
        
    def close(self, event=""):
        self.master.destroy()
    
    def toggleExpertMode(self, event=""):
        pass
    
    def save(self, event=""):
        pass
    
    def saveExecute(self):
        pass
    
    def getRow(self):
        row = self.lastrow
        self.lastrow += 1
        return row
    
    def fillButtons(self):
        row = self.getRow()
        self.addSeparator(row)
        row += 3
        self.addButton("Close", self.close, 0, row, 0, W)
        if self.expert_mode:
            text2 = "Hide Expert Options"
        else:
            text2 = "Show Expert Options"
        self.addButton(text2, self.toggleExpertMode, 12, row, 1, EW)
        self.addButton("Save", self.save, 0, row, 3, W)
        self.addButton("Save & Execute", self.saveExecute, 7, row, 4, W)
        
    def addBindings(self):
        self.master.bind('<Alt_L><c>', self.close)
        self.master.bind('<Alt_L><o>', self.toggleExpertMode)
        self.master.bind('<Alt_L><s>', self.save)
        self.master.bind('<Alt_L><e>', self.saveExecute)
        self.master.bind('<Alt_L><r>', self.saveExecute)
        
    def launchGUI(self):
        
        self.master = Tk()
        self.fontsize = 9
        self.columnspantextlabel = 3
        self.columntextentry = 3
        
        self.prepareCanvas() 
        self.fillHeader()
        #self.fillWidgets()
                # Add bottom row buttons
        self.fillButtons()
        self.addBindings()
        self.createCanvas() 
        self.resize()        
        self.master.mainloop()    
        
    
if __name__ == '__main__':
    script = sys.argv[1]  
    gui = ProtocolGUI(script)
    gui.readProtocolScript()
    gui.parseHeader()
    gui.launchGUI()
    #print gui.variablesDict 
    
            
