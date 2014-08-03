#!/usr/bin/python
# -*- coding: latin-1 -*-

# Newer Credits Editor - Edits NewerSMBW's StaffRoll.bin
# Version 1.1
# Copyright (C) 2013-2014 RoadrunnerWMC

# This file is part of Newer Credits Editor.

# Newer Credits Editor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Newer Credits Editor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Newer Credits Editor.  If not, see <http://www.gnu.org/licenses/>.



# newer_credits_editor.py
# This is the main executable for Newer Credits Editor


################################################################
################################################################


version = '1.1'

from PyQt5 import QtCore, QtGui, QtWidgets
import sys




################################################################
################################################################
################################################################
########################### Commands ###########################

class Command():
    """Base class for all commands"""
    def __init__(self):
        self.name = ''
        self.description = ''
        self.widgets = []
        self.Layout = QtWidgets.QVBoxLayout()

    def fromData(self, data):
        """Sets settings based on some data"""
        pass
    
    def toData(self):
        """Returns data based on current settings"""
        return ()

    def toPyObject(self):
        """Py2 / Py3 compatibility"""
        return self

    def GenerateLayout(self):
        """Creates a layout from self.widgets"""        
        if len(self.widgets) > 0:
            L = QtWidgets.QFormLayout()
            for name, W in self.widgets:
                L.addRow(name, W)
            self.Layout = L
        else: self.Layout = GetNullLayout()


class Com_stop(Command):
    """Command which indicates EOF"""
    def __init__(self):
        Command.__init__(self)
        self.GenerateLayout()
        # Isn't displayed in the editor so
        # it doesn't need a name, description or widgets
    
class Com_delay(Command):
    """Command which indicates a delay"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Wait'
        self.description = 'Causes a delay before the next command is processed'

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFFFF)
        self.widgets = []
        self.widgets.append(('Time (in frames):', W))
        self.GenerateLayout()

    def fromData(self, data):
        delay = (data[0] << 8) | data[1]
        self.widgets[0][1].setValue(delay)

    def toData(self):
        delay = self.widgets[0][1].value()
        a = (delay >> 8) & 0xFF
        b = delay & 0xFF
        return (a, b)
        
    
class Com_switch_scene(Command):
    """Command which indicates a scene switch"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Switch Scene'
        self.description = 'Causes the level to switch to another zone'

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets = []
        self.widgets.append(('Scene ID:', W))
        self.GenerateLayout()

    def fromData(self, data):
        self.widgets[0][1].setValue(data[0])

    def toData(self):
        L = []
        L.append(self.widgets[0][1].value())
        return L
    
class Com_switch_scene_and_wait(Command):
    """Command which indicates a scene switch and then wait"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Switch Scene and Wait'
        self.description = 'Causes the level to switch to another zone and then wait'

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets = []
        self.widgets.append(('Scene ID:', W))
        self.GenerateLayout()

    def fromData(self, data):
        self.widgets[0][1].setValue(data[0])

    def toData(self):
        L = []
        L.append(self.widgets[0][1].value())
        return L

class Com_show_scores(Command):
    """Command which causes the scores to be displayed"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Show Coin Counters'
        self.description = 'Causes the coin counters to become visible'
        self.GenerateLayout()
        # no settings = no widgets

class Com_show_text(Command):
    """Command which causes the current text to be displayed"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Show Text'
        self.description = 'Causes the current text to fade onto the screen'
        self.GenerateLayout()
        # no settings = no widgets

class Com_hide_text(Command):
    """Command which causes the current text to be hidden"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Hide Text'
        self.description = 'Causes the current text to fade away'
        self.GenerateLayout()
        # no settings = no widgets

class Com_set_text(Command):
    """Command which sets the current text"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Set Text'
        self.description = 'Changes the current text'

        W = QtWidgets.QLineEdit()
        X = QtWidgets.QPlainTextEdit()
        X.setLineWrapMode(X.NoWrap)
        self.widgets = (('Title:', W), ('Text:', X))
        self.GenerateLayout()

    def fromData(self, data):
        LenOfTitle = data[0]
        NumOfLines = data[1]
        
        title = ''
        i = 2
        while i < LenOfTitle + 2:
            title += chr(data[i])
            i += 1
        title = title[:-1] # ?

        text = ''
        while True:
            if data[i] != 0: text += chr(data[i])
            else: break
            i += 1

        self.widgets[0][1].setText(title)
        self.widgets[1][1].setPlainText(text)

    def toData(self):
        new = []
        title = str(self.widgets[0][1].text())
        text = str(self.widgets[1][1].toPlainText())

        new.append(len(title)+1)
        new.append(text.count('\n')+1)

        for char in title:
            if char != chr(0): new.append(ord(char))
        new.append(0)
        for char in text:
            if char != chr(0): new.append(ord(char))
        new.append(0)

        return tuple(new)

class Com_show_title(Command):
    """Command which causes the title to be displayed"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Show Titlescreen Logo'
        self.description = 'Causes the titlescreen logo to become visible'
        self.GenerateLayout()
        # no settings = no widgets

class Com_hide_title(Command):
    """Command which causes the title to be hidden"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Hide Titlescreen Logo'
        self.description = 'Hides the titlescreen logo'
        self.GenerateLayout()
        # no settings = no widgets

class Com_play_title_anim(Command):
    """Command which causes the title anim to be played"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Play Titlescreen Logo Animation'
        self.description = 'Plays a titlescreen logo animation'

        W = QtWidgets.QSpinBox()
        W.setMaximum(0xFF)
        self.widgets = []
        self.widgets.append(('Animation ID:', W))
        self.GenerateLayout()

    def fromData(self, data):
        self.widgets[0][1].setValue(data[0])

    def toData(self):
        L = []
        L.append(self.widgets[0][1].value())
        return L

class Com_enable_ending_mode(Command):
    """Command which causes the ending mode to be enabled"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Enable Ending Mode'
        self.description = 'Enables the ending mode. The ending mode disables Wii remote player control.'
        self.GenerateLayout()
        # no settings = no widgets

class Com_spawn_zoom(Command):
    """Command which does something unknown"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Spawn Zoom'
        self.description = 'Unknown function'
        self.GenerateLayout()
        # no settings = no widgets

class Com_player_win_anims(Command):
    """Command which causes the player win animations to be played"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Play Player Win Animations'
        self.description = 'Plays an animation for the player with the most coins'
        self.GenerateLayout()
        # no settings = no widgets

class Com_destroy_zoom(Command):
    """Command which does something unknown"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Destroy Zoom'
        self.description = 'Unknown function'
        self.GenerateLayout()
        # no settings = no widgets

class Com_players_look_up(Command):
    """Command which causes the players to look up"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Players Look Up'
        self.description = 'Causes all players to look upward'
        self.GenerateLayout()
        # no settings = no widgets

class Com_the_end(Command):
    """Command which causes 'The End' to be displayed"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Display \'The End\''
        self.description = 'Causes \'The End\' to appear on the screen'
        self.GenerateLayout()
        # no settings = no widgets

class Com_exit_stage(Command):
    """Command which causes the stage to be exited"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Exit Stage'
        self.description = 'Exits the stage'
        self.GenerateLayout()
        # no settings = no widgets

class Com_hide_the_end(Command):
    """Command which causes 'The End' to be hidden"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Hide \'The End\''
        self.description = 'Causes \'The End\' to fade away'
        self.GenerateLayout()
        # no settings = no widgets

class Com_begin_fireworks(Command):
    """Command which causes fireworks to begin"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'Begin Fireworks'
        self.description = 'Causes fireworks to begin in the background'
        self.GenerateLayout()
        # no settings = no widgets

class Com_end_fireworks(Command):
    """Command which causes fireworks to end"""
    def __init__(self):
        Command.__init__(self)
        self.name = 'End Fireworks'
        self.description = 'Causes the background fireworks to end'
        self.GenerateLayout()
        # no settings = no widgets


CommandsById = (
    Com_stop, # 0x00 (0)
    Com_delay, # 0x01 (1)
    Com_switch_scene, # 0x02 (2)
    Com_switch_scene_and_wait, # 0x03 (3)
    Com_show_scores, # 0x04 (4)
    Com_show_text, # 0x05 (5)
    Com_hide_text, # 0x06 (6)
    Com_set_text, # 0x07 (7)
    Com_show_title, # 0x08 (8)
    Com_hide_title, # 0x09 (9)
    Com_play_title_anim, # 0x0A (10)
    Com_enable_ending_mode, # 0x0B (11)
    Com_spawn_zoom, # 0x0C (12)
    Com_player_win_anims, # 0x0D (13)
    Com_destroy_zoom, # 0x0E (14)
    Com_players_look_up, # 0x0F (15)
    Com_the_end, # 0x10 (16)
    Com_exit_stage, # 0x11 (17)
    Com_hide_the_end, # 0x12 (18)
    Com_begin_fireworks, # 0x13 (19)
    Com_end_fireworks, # 0x14 (20)
    )


def CommandFromData(data):
    """Returns an command from data"""
    com = CommandsById[data[0]]()
    com.fromData(data[1:])
    return com


class NewerStaffRollBin():
    """Class which represents NewerStaffRoll.bin"""
    def __init__(self, data=None):
        """Initialises the NewerStaffRollBin"""
        self.Commands = []
        if data != None: self.InitFromData(data)

    def InitFromData(self, data):
        """Initialises the NewerStaffRollBin from raw file data"""

        # No headers. Iterate over the data until we've reached the EOF com
        commands = []
        i = 0
        while True:
            # Get the command data
            datalen = data[i] - 1
            i += 1
            comdata = data[i:i+datalen]
            i += datalen
            
            # Make an command
            com = CommandFromData(comdata)
            if isinstance(com, Com_stop): break
            else: commands.append(com)
            
        # Assign to self.commands
        self.Commands = commands
        

    def save(self):
        """Converts self.commands to bytes that can be saved"""
        data = []
        coms = list(self.Commands)
        coms.append(Com_stop())
        for com in coms:
            comdata = com.toData()
            data.append(len(comdata)+2)
            
            id = None
            for comType in CommandsById:
                if isinstance(com, comType): id = CommandsById.index(comType)
            data.append(id)

            for i in comdata:
                if not isinstance(i, int): print(i)
                data.append(i)

        if sys.version[0] == '2':
            new = ''
            for i in data: new += chr(i)
            return new
        else: return bytes(data)



################################################################
################################################################
################################################################
######################### UI Classes ###########################


# Credits Viewer
class CreditsViewer(QtWidgets.QWidget):
    """Widget that allows you to view credits data"""

    # Drag-and-Drop Picker
    class DNDPicker(QtWidgets.QListWidget):
        """A list widget which calls a function when an item's been moved"""
        def __init__(self, handler):
            QtWidgets.QListWidget.__init__(self)
            self.handler = handler
            self.setDragDropMode(QtWidgets.QListWidget.InternalMove)
        def dropEvent(self, event):
            QtWidgets.QListWidget.dropEvent(self, event)
            self.handler()

    # Init
    def __init__(self):
        """Initialises the widget"""
        QtWidgets.QWidget.__init__(self)
        self.file = None

        # Create the command picker widgets
        PickerBox = QtWidgets.QGroupBox('Commands')
        self.picker = self.DNDPicker(self.HandleDragDrop)
        self.picker.setMinimumWidth(384)
        self.ABtn = QtWidgets.QPushButton('Add')
        self.RBtn = QtWidgets.QPushButton('Remove')

        # Add some tooltips
        self.ABtn.setToolTip('<b>Add:</b><br>Adds an command after the currently selected command')
        self.RBtn.setToolTip('<b>Remove:</b><br>Removes the currently selected command')

        # Connect them to handlers
        self.picker.currentItemChanged.connect(self.HandleComSel)
        self.ABtn.clicked.connect(self.HandleA)
        self.RBtn.clicked.connect(self.HandleR)

        # Disable them for now
        self.picker.setEnabled(False)
        self.ABtn.setEnabled(False)
        self.RBtn.setEnabled(False)

        # Set up the QGroupBox layout
        L = QtWidgets.QGridLayout()
        L.addWidget(self.picker, 0, 0, 1, 2)
        L.addWidget(self.ABtn, 1, 0)
        L.addWidget(self.RBtn, 1, 1)
        PickerBox.setLayout(L)

        # Create the command editor
        self.ComBox = QtWidgets.QGroupBox('Command')
        self.edit = CommandEditor()
        self.edit.dataChanged.connect(self.HandleComDatChange)
        L = QtWidgets.QVBoxLayout()
        L.addWidget(self.edit)
        self.ComBox.setLayout(L)
        
        # Make the main layout
        L = QtWidgets.QHBoxLayout()
        L.addWidget(PickerBox)
        L.addWidget(self.ComBox)
        self.setLayout(L)

    def setFile(self, file):
        """Changes the file to view"""
        self.file = file
        self.picker.clear()
        self.SetComEdit(CommandEditor()) # clears it

        # Enable widgets
        self.picker.setEnabled(True)
        self.ABtn.setEnabled(True)
        self.RBtn.setEnabled(False)

        # Add commands
        for com in file.Commands:
            item = QtWidgets.QListWidgetItem() # self.UpdateNames will add the name
            item.setData(QtCore.Qt.UserRole, com)
            self.picker.addItem(item)

        self.UpdateNames()

    def saveFile(self):
        """Returns the file in saved form"""
        return self.file.save() # self.file does this for us
    
    def UpdateNames(self):
        """Updates item names in the msg picker"""
        for item in self.picker.findItems('', QtCore.Qt.MatchContains):
            com = item.data(QtCore.Qt.UserRole)

            # Pick text and tooltips
            text = com.name
            tooltip = '<b>' + com.name + ':</b><br>' + com.description
            if isinstance(com, Com_set_text):
                text += ' (to "' + com.widgets[0][1].text() + '")'
            elif isinstance(com, Com_delay):
                f = str(com.widgets[0][1].value())
                text += ' (for ' + f + (' frames)' if f != '1' else ' frame)')
            elif isinstance(com, Com_switch_scene) or isinstance(com, Com_switch_scene_and_wait):
                text += ' (to Scene ID ' + str(com.widgets[0][1].value()) + ')'
            elif isinstance(com, Com_play_title_anim):
                text += ' ' + str(com.widgets[0][1].value())

            # Set text
            item.setText(text)
            item.setToolTip(tooltip)

    def HandleDragDrop(self):
        """Handles dragging and dropping"""
        # First, update the file
        newCommands = []
        for item in self.picker.findItems('', QtCore.Qt.MatchContains):
            com = item.data(QtCore.Qt.UserRole)
            newCommands.append(com)
        self.file.Commands = newCommands

        # Then, update the names
        self.UpdateNames()

    def HandleComDatChange(self):
        """Handles changes to the current message data"""
        self.UpdateNames()
        
    def HandleComSel(self):
        self.SetComEdit(CommandEditor()) # clears it
        
        # Get the current item (it's None if nothing's selected)
        currentItem = self.picker.currentItem()

        # Update the Remove btn
        self.RBtn.setEnabled(currentItem != None)

        # Get the command
        if currentItem == None: return
        com = currentItem.data(QtCore.Qt.UserRole)

        # Set up the command editor
        e = CommandEditor(com)
        self.SetComEdit(e)
        
    def HandleA(self):
        """Handles the user clicking Add"""
        com = GetUserPickedCommand()
        if com == None: return
        com = com()

        # Add it to self.file and self.picker
        self.file.Commands.append(com)
        item = QtWidgets.QListWidgetItem()
        item.setData(QtCore.Qt.UserRole, com)
        self.picker.addItem(item)
        self.picker.scrollToItem(item)
        self.picker.setItemSelected(item, True)

        self.UpdateNames()
    
    def HandleR(self):
        """Handles the user clicking Remove"""
        item = self.picker.currentItem()
        com = item.data(QtCore.Qt.UserRole)

        # Remove it from file and the picker
        self.file.Commands.remove(com)
        self.picker.takeItem(self.picker.row(item))

        # Clear the selection
        self.SetComEdit(CommandEditor())
        self.picker.clearSelection()
        self.RBtn.setEnabled(False)

        self.UpdateNames()

    def SetComEdit(self, e):
        """Changes the current CommandEditor"""
        x = self.ComBox.layout().takeAt(0)
        if x != None: x.widget().delete()
        w = x.widget()
        del w
        
        self.ComBox.layout().addWidget(e)
        e.dataChanged.connect(self.HandleComDatChange)
        self.ComBox.update()



# Command Editor Widget
# NOTE: Due to Qt's limitations, this works differently
# than it did in my other tools. A new instance of this
# is created every time the selection changes.
class CommandEditor(QtWidgets.QWidget):
    """Widget that allows you to edit an command"""
    dataChanged = QtCore.pyqtSignal()
    def __init__(self, com = Command()):
        """Initialises the CommandEditor"""
        QtWidgets.QWidget.__init__(self)
        self.com = com

        # Set the layout
        self.setLayout(self.com.Layout)
        self.setMinimumWidth(384)

        # Connect each widget to the handler
        for i in range(self.com.Layout.count()):
            w = self.com.Layout.itemAt(i).widget()

            connectors = {
                QtWidgets.QSpinBox: 'valueChanged',
                QtWidgets.QLineEdit: 'textEdited',
                QtWidgets.QPlainTextEdit: 'textChanged',
                }
            for name in connectors:
                if isinstance(w, name):
                    exec('w.%s.connect(self.HandleDataChanged)' % connectors[name])
        

    def delete(self):
        """Prepares to be deleted"""
        self.hide()

    def HandleDataChanged(self):
        """Handles data changes"""
        self.dataChanged.emit()


# Get Null Layout
def GetNullLayout():
    """Returns a layout with only 'No settings'"""
    NA = QtWidgets.QLabel('<i>No settings</i>')
    NA.setEnabled(False)
    L = QtWidgets.QVBoxLayout()
    L.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
    L.addWidget(NA)
    return L



# Command Picker Dialog
def GetUserPickedCommand():
    """Returns a command picked by the user"""
    dlg = CommandPickDlg()
    if dlg.exec_() != QtWidgets.QDialog.Accepted: return

    return dlg.combo.itemData(dlg.combo.currentIndex())

class CommandPickDlg(QtWidgets.QDialog):
    """Dialog that lets the user pick a command type"""
    def __init__(self):
        """Initialises the dialog"""
        QtWidgets.QDialog.__init__(self)

        # Make a label
        label = QtWidgets.QLabel('Pick the type of command<br>you would like to insert:')

        # Make a combobox and add entries
        self.combo = QtWidgets.QComboBox()
        items = []
        for com in CommandsById:
            if com == Com_stop: continue
            self.combo.addItem(com().name, com)

        # Make a buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Add a layout
        L = QtWidgets.QVBoxLayout()
        L.addWidget(label)
        L.addWidget(self.combo)
        L.addWidget(buttonBox)
        self.setLayout(L)

################################################################
################################################################
################################################################
######################### Main Window ##########################


class MainWindow(QtWidgets.QMainWindow):
    """Main window"""
    def __init__(self):
        """Initialises the window"""
        QtWidgets.QMainWindow.__init__(self)
        self.fp = None # file path

        # Create the viewer
        self.view = CreditsViewer()
        self.setCentralWidget(self.view)

        # Create the menubar and a few actions
        self.CreateMenubar()

        # Set window title and show the window
        self.setWindowTitle('Newer Credits Editor')
        self.show()

    def CreateMenubar(self):
        """Sets up the menubar"""
        m = self.menuBar()

        # File Menu
        f = m.addMenu('&File')

        newAct = f.addAction('New File...')
        newAct.setShortcut('Ctrl+N')
        newAct.triggered.connect(self.HandleNew)

        openAct = f.addAction('Open File...')
        openAct.setShortcut('Ctrl+O')
        openAct.triggered.connect(self.HandleOpen)

        self.saveAct = f.addAction('Save File')
        self.saveAct.setShortcut('Ctrl+S')
        self.saveAct.triggered.connect(self.HandleSave)
        self.saveAct.setEnabled(False)

        self.saveAsAct = f.addAction('Save File As...')
        self.saveAsAct.setShortcut('Ctrl+Shift+S')
        self.saveAsAct.triggered.connect(self.HandleSaveAs)
        self.saveAsAct.setEnabled(False)

        f.addSeparator()

        exitAct = f.addAction('Exit')
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.HandleExit)

        # Help Menu
        h = m.addMenu('&Help')

        aboutAct= h.addAction('About...')
        aboutAct.setShortcut('Ctrl+H')
        aboutAct.triggered.connect(self.HandleAbout)


    def HandleNew(self):
        """Handles creating a new file"""
        f = NewerStaffRollBin()
        self.view.setFile(f)
        self.saveAsAct.setEnabled(True)

    def HandleOpen(self):
        """Handles file opening"""
        fp = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        if fp == '': return
        self.fp = fp

        # Open the file
        file = open(fp, 'rb')
        data = file.read()
        file.close()

        if sys.version[0] == '2': # Py2
            # convert the str to a list
            new = []
            for char in data: new.append(ord(char))
            data = new
        
        M = NewerStaffRollBin(data)

        # Update the viewer with this data
        self.view.setFile(M)

        # Enable saving
        self.saveAct.setEnabled(True)
        self.saveAsAct.setEnabled(True)

    def HandleSave(self):
        """Handles file saving"""
        data = self.view.saveFile()

        # Open the file
        file = open(self.fp, 'wb')
        if sys.version[0] == '2': file.write(data)
        else: file.write(data)
        file.close()

    def HandleSaveAs(self):
        """Handles saving to a new file"""
        fp = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'Binary Files (*.bin);;All Files (*)')[0]
        if fp == '': return
        self.fp = fp

        # Save it
        self.HandleSave()

        # Enable saving
        self.saveAct.setEnabled(True)

    def HandleExit(self):
        """Exits"""
        raise SystemExit

    def HandleAbout(self):
        """Shows the About dialog"""
        try: readme = open('readme.md', 'r').read()
        except: readme = 'Newer Credits Editor %s by RoadrunnerWMC\n(No readme.md found!)\nLicensed under GPL 3' % version

        txtedit = QtWidgets.QPlainTextEdit(readme)
        txtedit.setReadOnly(True)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(txtedit)
        layout.addWidget(buttonBox)

        dlg = QtWidgets.QDialog()
        dlg.setLayout(layout)
        dlg.setModal(True)
        dlg.setMinimumWidth(384)
        buttonBox.accepted.connect(dlg.accept)
        dlg.exec_()


################################################################
################################################################
################################################################
############################ Main() ############################


# Main function
def main():
    """Main startup function"""
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
main()
