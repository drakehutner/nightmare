#!/usr/bin/env python


import os

import Tkinter as guitk
from Tkinter import LEFT, RIGHT, TOP, DISABLED, N, E, S, W, NE, SE, SW, NW, CENTER, X, Y, BOTH
import tkFileDialog as fileDiag

# pyTest classes
from test.testState import TestState
from test.testMode import TestSuiteMode
from test.test import Test
from test.testSuite import TestSuite
from test.testRunner import TestRunner
from test.utils import isLambda


class LabeledEntry(guitk.Frame):
	def __init__(self, parent, gui, lbl, var, pos=LEFT, anch=NW):
		"""
		Initialise the labeled entry
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	lbl: String
		@param	lbl: The caption for the label
		
		@type	var: StringVar
		@param	var: The variable holding the content in the entry field
		
		@param	pos: Packing position for both widgets
		@param	anch: Packing anchor for both widgets
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self.label = guitk.Label(self, text=lbl, width=10, justify=LEFT)
		self.entry = guitk.Entry(self, textvariable=var, width=20, justify=LEFT)
		self.label.pack(side=pos, anchor=anch)
		self.entry.pack(side=pos, anchor=anch, fill=X, expand=1)
		

class TestRunButton(guitk.Button):
	"""Button to start one test run"""
	def __init__(self, parent, gui, caption, n, runner):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	caption: String
		@param 	caption: Caption of the button
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.runTest, width=7)
		self._num = n
		self._runner = runner
		self._gui = gui
		
	def runTest(self):
		"""Run the test(s)"""
		self._runner.mode = self._gui._mode.get()
		if self._num == -1:
			self._runner.start(self.finishHandler)
		else:
			self._runner.start(self.finishHandler, self._num)

	def finishHandler(self):
		"""Handler for updating the datagrid after the test run"""
		self._gui.dataGrid.update()
		
		
class TestSaveButton(guitk.Button):
	"""Button to the save the test data"""
	def __init__(self, parent, test, gui):
		"""
		Initialise the button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	test: Test
		@param	test: The test data
		"""
		guitk.Button.__init__(self, parent, text="Save", command=self.saveTest, width=7)
		self._test = test
		self._parentForm = parent
		self._gui = gui
		
	def saveTest(self):
		"""Save the test"""
		name = str(self._parentForm._varname.get())
		descr = str(self._parentForm._vardescr.get())
		cmd = str(self._parentForm._varcmd.get())
		out = str(self._parentForm._expOut.get(1.0, 'end')).strip()
		err = str(self._parentForm._expErr.get(1.0, 'end')).strip()
		ret = str(self._parentForm._varexpRet.get()).strip()
		self._test.name = name
		self._test.descr = descr
		self._test.cmd = cmd
		if out != "":
			self._test.expectStdout = out
		else:
			self._test.expectStdout = None
		if err != "":
			self._test.expectStderr = err
		else:
			self._test.expectStderr = None
		if ret != "":
			self._test.expectRetCode = ret
		else:
			self._test.expectRetCode = None
		self._gui.dataGrid.update()
		

class FileLoaderButton(guitk.Button):
	"""Button for handling file selection"""
	def __init__(self, parent, caption, callback, func=fileDiag.askopenfilename, filetypes=[("All files","*")], defaultExt=""):
		"""
		Initialises the button
		
		@type 	parent: Widget
		@param	parent: Parent widget
		
		@type	caption: String
		@param	caption: Caption for the button
		
		@type	callback: Function
		@param 	callback: Callback function, called after successfull selection
		
		@type	func: Function
		@param	func: Function to be called for file selection
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.selectFile)
		self._callback = callback
		self._func = func
		self._caption = caption
		self._filetypes = filetypes
		self._defaultExt = defaultExt
	
	def selectFile(self):
		"""Eventhandler for button click"""
		if self._func is not None:
			fn = self._func(initialdir=".", filetypes=self._filetypes, defaultextension=self._defaultExt, title=self._caption)
			if fn != "":
				self._callback(fn)

class TestEditButton(guitk.Button):
	"""Button for editing a test"""
	def __init__(self, parent, gui, caption, test, n):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.editTest, width=7)
		self._test = test
		self._gui = gui
		self._num = n
		
	def editTest(self):
		TestEditForm(self, self._num, self._test, self._gui._runner, self._gui)
		
class TestCreateButton(guitk.Button):
	"""Button for creating a new test"""
	def __init__(self, parent, gui, caption, runner):
		"""
		Initialise the test edit button
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	caption: String
		@param	caption: The caption of the button
		
		@type	test: Test
		@param	test: The test to be edited
		
		@type 	n: int
		@param	n: The number of the test
		"""
		guitk.Button.__init__(self, parent, text=caption, command=self.createTest)
		self._gui = gui
		self._runner = runner
		
	def createTest(self):
		"""Eventhandler for button click"""
		test = Test()
		self._runner.getSuite().getTests().append(test)
		self._gui.dataGrid.update()
		self._gui.dataGrid.scroll()
		TestEditForm(self, len(self._runner.getSuite().getTests()), test, self._runner, self._gui)

class TestEditForm(guitk.Toplevel):
	"""Form for editing one test"""
	def __init__(self, parent, n, test, runner, gui):
		"""
		Initialises the form
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	n: int 
		@param	n: Number of the test
		
		@type	test: Test
		@param 	test: The test to be edited
		
		@type	runner: TestRunner
		@param	runner: The test runner
		"""
		guitk.Toplevel.__init__(self, parent)
		self.title("Edit test {}".format(n))
		self._test = test
		self._gui = gui
		# Variables
		self._varname = guitk.StringVar(self, self._test.name)
		self._vardescr = guitk.StringVar(self, self._test.descr)
		self._varcmd = guitk.StringVar(self, self._test.cmd)
		self._varret = guitk.StringVar(self, self._test.retCode)
		self._varexpRet = guitk.StringVar(self, self._test.expectRetCode)
		# Widgets
		guitk.Label(self, text="Name").grid(row=0, column=0, columnspan=2)
		guitk.Entry(self, width=50, textvariable=self._varname).grid(row=1, column=0, columnspan=2, sticky=N+E+S+W)
		guitk.Label(self, text="Description").grid(row=0, column=2, columnspan=4)
		guitk.Entry(self, width=70, textvariable=self._vardescr).grid(row=1, column=2, columnspan=4, sticky=N+E+S+W)
		guitk.Label(self, text="Command").grid(row=2, column=0, columnspan=6)
		guitk.Entry(self, width=120, textvariable=self._varcmd).grid(row=3, column=0, columnspan=6, sticky=N+E+S+W)
		guitk.Label(self, text="Expected stdout").grid(row=4, column=0, columnspan=3)
		self._expOut = guitk.Text(self, width=50, height=5)
		self._expOut.grid(row=5, column=0, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="stdout").grid(row=4, column=3, columnspan=3)
		self._out = guitk.Text(self, width=50, height=5)
		self._out.grid(row=5, column=3, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="Expected Stderr").grid(row=6, column=0, columnspan=3)
		self._expErr = guitk.Text(self, width=50, height=5)
		self._expErr.grid(row=7, column=0, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="stderr").grid(row=6, column=3, columnspan=3)
		self._err = guitk.Text(self, width=50, height=5)
		self._err.grid(row=7, column=3, columnspan=3, sticky=N+E+S+W)
		guitk.Label(self, text="Expected Returncode").grid(row=8, column=0, columnspan=2)
		guitk.Entry(self, width=30, textvariable=self._varexpRet).grid(row=9, column=0, columnspan=2, sticky=N+E+S+W)
		guitk.Label(self, text="Returncode").grid(row=8, column=2, columnspan=2)
		guitk.Entry(self, width=30, textvariable=self._varret, state=DISABLED).grid(row=9, column=2, columnspan=2, sticky=N+E+S+W)
		TestRunButton(self, gui, "Run", n-1, runner).grid(row=9, column=4)
		TestSaveButton(self, test, gui).grid(row=9, column=5)
		# Fill data
		if not isLambda(self._test.expectStdout) and self._test.expectStdout is not None:
			self._expOut.insert(guitk.INSERT, str(self._test.expectStdout))
		if not isLambda(self._test.expectStderr) and self._test.expectStderr is not None:
			self._expErr.insert(guitk.INSERT, str(self._test.expectStderr))
		if self._test.output != "":
			self._out.insert(guitk.INSERT, str(self._test.output))
		if self._test.error != "":
			self._err.insert(guitk.INSERT, str(self._test.error))

class TestRow(guitk.Frame):
	"""The TestRow represents a single row inside the Testgrid"""
	def __init__(self, parent, gui, runner, n, test):
		"""
		Initialise the row
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		
		@type 	n: int
		@param	n: Number of the test
		
		@type	test: Test
		@param	test: The testdata
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self._runner = runner
		self._num = n
		self._test = test
		self._bgcol = "#FFF"
		self._fgcol = "#000"
		self.setColor()
		self._edtBtn = TestEditButton(self, self._gui, "Edit", test, self._num)
		self._edtBtn.pack(side=LEFT)
		self._checkBtn = guitk.Checkbutton(self, command=self.clickCheck)
		self._checkBtn.pack(side=LEFT)
		self._checkBtn.select()
		self._lblNum = guitk.Label(self, text="{:02}".format(n), bg=self._bgcol, fg=self._fgcol, width=3)
		self._lblNum.pack(side=LEFT)
		self._lblName = guitk.Label(self, text=test.name, bg=self._bgcol, fg=self._fgcol, width=20)
		self._lblName.pack(side=LEFT)
		self._lblDescr = guitk.Label(self, text=test.descr, bg=self._bgcol, fg=self._fgcol, width=40)
		self._lblDescr.pack(side=LEFT, expand=1, fill=X)
		
	def setColor(self):
		"""Set colors based on TestState"""
		if self._test.state == TestState.Success:
			self._bgcol = "#0D0"
			self._fgcol = "#000"
		elif self._test.state == TestState.Fail:
			self._bgcol = "#D00"
			self._fgcol = "#FFF"
		elif self._test.state == TestState.Error:
			self._bgcol = "#DD0"
			self._fgcol = "#000"
		elif self._test.state == TestState.Waiting:
			self._bgcol = "#FFF"
			self._fgcol = "#000"
		elif self._test.state == TestState.Disabled:
			self._bgcol = "#FFF"
			self._fgcol = "#888"
	
	def update(self):
		"""Updates the widgets"""
		self.setColor()
		self._lblNum.config(fg=self._fgcol, bg=self._bgcol)
		self._lblName.config(fg=self._fgcol, bg=self._bgcol, text=self._test.name)
		self._lblDescr.config(fg=self._fgcol, bg=self._bgcol, text=self._test.descr)
		if self._test.state == TestState.Disabled:
			self._checkBtn.deselect()
		else:
			self._checkBtn.select()
		
	def clickCheck(self):
		"""Eventhandler for checkbutton click"""
		if self._test.state == TestState.Disabled:
			self._test.state = TestState.Waiting
			self._checkBtn.select()
		else:
			self._test.state = TestState.Disabled
			self._checkBtn.deselect()
		self.update()
		
		
class TestGrid(guitk.Frame):
	"""A TestGrid displays all tests and their result."""
	def __init__(self, parent, gui, runner):
		"""
		Initialise the grid
		
		@type	parent: Widget
		@param	parent: Parent widget
		
		@type	gui: TK
		@param	gui: The main window
		
		@type	runner: TestRunner
		@param	runner: The testrunner holding the test data
		"""
		guitk.Frame.__init__(self, parent)
		self._gui = gui
		self._runner = runner
		self._rows = []
		self.createHead()
		self._visible = (0,9)
	
	def toggleAll(self):
		"""Eventhandler for header checkbutton"""
		self._runner.getSuite().setAll(disabled=self._toggleAllVar.get())
		self._gui.dataGrid.update()
	
	def createHead(self):
		"""Create the head of the grid"""
		head = guitk.Frame(self)
		guitk.Button(head, text="+", command=self.scrollUp, width=3).pack(side=LEFT)
		guitk.Button(head, text="-", command=self.scrollDown, width=3).pack(side=LEFT)
		self._toggleAllVar = guitk.IntVar(head)
		self._toggleAll = guitk.Checkbutton(head, onvalue=False, offvalue=True, command=self.toggleAll, variable=self._toggleAllVar)
		self._toggleAll.select()
		self._toggleAll.pack(side=LEFT)
		guitk.Label(head, text="#", width=3).pack(side=LEFT)
		guitk.Label(head, text="Name", width=20).pack(side=LEFT)
		guitk.Label(head, text="Description", width=40).pack(side=LEFT, expand=1, fill=X)
		head.pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
	
	def scrollUp(self):
		"""Scroll the grid one row up"""
		lower, upper = self._visible
		if upper < len(self._rows)-1:
			lower = lower + 1
			upper = upper + 1
			self._visible = lower, upper
			self.scroll()
	
	def scrollDown(self):
		"""Scroll the grid one row down"""
		lower, upper = self._visible
		if lower > 0:
			lower = lower - 1
			upper = upper - 1
			self._visible = lower, upper
			self.scroll()
	
	def addRow(self, test):
		"""
		Add a row to the gridd
		
		@type 	test: Test
		@param	test: Test with data for the row
		"""
		row = TestRow(self, self._gui, self._runner, len(self._rows)+1, test)
		self._rows.append(row)
	
	def update(self):
		"""Update the grid"""
		i = 0
		for t in self._runner.getSuite().getTests():
			if i >= len(self._rows):
				self.addRow(t)
			else:
				self._rows[i].update()
			i = i + 1
			
	def scroll(self):
		"""Scroll through the grid"""
		lower, upper = self._visible
		if upper > len(self._rows):
			upper = len(self._rows)-1
		for row in self._rows:
			row.pack_forget()
		for i in range(lower, upper+1):
			self._rows[i].pack(side=TOP, expand=1, fill=BOTH, anchor=NW)
			
	def clear(self):
		"""remove all rows from the grid"""
		for row in self._rows:
			row.pack_forget()
			row.destroy()
		self._rows = []
		
			
class TestRunnerGui():
	"""Graphical User Interface"""
	
	def _handleSuiteLoad(self, fn):
		"""
		Load a testsuite
		
		@type	fn: String
		@param 	fn: The filename
		"""
		dut = os.path.abspath(self._DUT.get())
		os.chdir(os.path.dirname(fn))
		self._DUT.set(os.path.relpath(dut))
		#print os.getcwd()
		self._runner.suite = self._suite.get()
		self._runner.file = os.path.relpath(fn)
		self._runner.mode = self._mode.get()
		self._runner.loadSuite()
		if self._runner.DUT is not None:
			self._DUT.set(self._runner.DUT)
		self._tests.set(self._runner.countTests())
		self._filename.set(os.path.relpath(fn))
		self.dataGrid.clear()
		self.dataGrid.update()
		self.dataGrid.scroll()
		
	def _handleSelectDUT(self, fn):
		"""
		Select a device under test
		
		@type	fn: String
		@param 	fn: The device under test (DUT)
		"""
		self._runner.setDUT(fn)
		self._DUT.set(os.path.relpath(fn))
		
	def _handleSuiteSave(self, fn):
		"""
		Save the testsuite into a file
		
		@type	fn: String
		@param 	fn: The filename
		"""
		fHnd = open(fn,"w")
		fHnd.write("#!/usr/bin/env python\n\n")
		fHnd.write("# pyTest - Testbench\n")
		fHnd.write("# Saved at {}\n".format(time.strftime("%H:%M:%S")))
		fHnd.write("# \n\n")
		#fHnd.write("# Author: {}\n".format())
		if self._runner.DUT is not None:
			fHnd.write("# Device Under Test\n")
			fHnd.write("DUT = \"{}\"\n\n".format(os.path.relpath(self._runner.DUT)))
		fHnd.write("# Test definitions\n")
		fHnd.write("{} = [\n".format(self._suite.get()))
		tests = []
		for test in self._runner.getSuite().getTests():
			tests.append("\t{}".format( test.toString()))
		fHnd.write(",\n".join(tests))
		fHnd.write("\n]\n")
		fHnd.close()
	
	def __init__(self):
		"""Initialise the gui"""
		self._runner = TestRunner()
		self._runner.parseArgv()
		self._whnd = guitk.Tk()
		self._whnd.title("pyTest GUI")
		
		# Frames
		cfgFrame = guitk.Frame(self._whnd)
		suiteFrame = guitk.LabelFrame(cfgFrame, text="Suite")
		suiteInfoFrame = guitk.Frame(suiteFrame)
		actionFrame = guitk.LabelFrame(cfgFrame, text="Mode")
		# Variables
		self._suite = guitk.StringVar(suiteInfoFrame, self._runner.suite)
		self._tests = guitk.StringVar(suiteInfoFrame, self._runner.testCount)
		self._filename = guitk.StringVar(suiteInfoFrame, "")
		self._DUT = guitk.StringVar(suiteInfoFrame, "")
		self._mode = guitk.IntVar(actionFrame, TestSuiteMode.BreakOnFail)
		# Suite info
		self._suiteFile = LabeledEntry(suiteInfoFrame, self, lbl="File", var=self._filename)
		self._suiteFile.entry.configure(state=DISABLED)
		self._suiteName = LabeledEntry(suiteInfoFrame, self, lbl="Name", var=self._suite)
		self._suiteTests = LabeledEntry(suiteInfoFrame, self, lbl="Tests", var=self._tests)
		self._suiteTests.entry.configure(state=DISABLED)
		self._DUTName = LabeledEntry(suiteInfoFrame, self, lbl="DUT", var=self._DUT)
		self._DUTName.entry.configure(state=DISABLED) 
		self._loadSuite = FileLoaderButton(suiteFrame, "Load Testsuite", self._handleSuiteLoad, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._saveSuite = FileLoaderButton(suiteFrame, "Save Testsuite", self._handleSuiteSave, fileDiag.asksaveasfilename, filetypes=[("Python Script","*.py"), ("pyTest Testbench","*.test.py")], defaultExt=".test.py")
		self._addTest = TestCreateButton(suiteFrame, self, "Add Test", self._runner)
		self._loadDUT = FileLoaderButton(actionFrame, "Select DUT", self._handleSelectDUT)
		self._runBtn = TestRunButton(actionFrame, self, caption="Run All", n=-1, runner=self._runner)
		# Pack all widgets
		
		self._loadDUT.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._runBtn.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		guitk.Radiobutton(actionFrame, text="Continuous", variable=self._mode, value=TestSuiteMode.Continuous).pack()
		guitk.Radiobutton(actionFrame, text="Halt on Fail", variable=self._mode, value=TestSuiteMode.BreakOnFail).pack()
		guitk.Radiobutton(actionFrame, text="Halt on Error", variable=self._mode, value=TestSuiteMode.BreakOnError).pack()
		
		self._loadSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._saveSuite.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		self._DUTName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteFile.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteName.pack(side=TOP, expand=1, fill=X, anchor=NW)
		self._suiteTests.pack(side=TOP, expand=1, fill=X, anchor=NW)
		suiteInfoFrame.pack(side=LEFT, expand=1, fill=X, anchor=NW)
		self._addTest.pack(side=LEFT, expand=1, fill=Y, anchor=NW)
		suiteFrame.pack(side=LEFT, anchor=NW)
		actionFrame.pack(side=RIGHT, anchor=NE)
		cfgFrame.pack(side=TOP, expand=1, fill=X, anchor=N)
		# create and pack datagrid
		self.dataGrid = TestGrid(self._whnd, self, self._runner)
		self.dataGrid.pack(side=TOP, expand=1, fill=X, anchor=NW)
		
		self._whnd.mainloop()
