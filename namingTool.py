import sys
import re
import random
from maya import cmds
from maya.api import OpenMaya as om2
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
     
class MyPushButton(QtWidgets.QPushButton):
    def __init__(self, parent=None):
        super(MyPushButton, self).__init__(parent)
        self.butColor = QtGui.QColor(180, 180, 180)
        self.length = 0.0
        self.lineVis = False
        
    def paintEvent(self, event):
        super(MyPushButton, self).paintEvent(event)
        
        if self.lineVis:
            painter = QtGui.QPainter(self)
            pen = QtGui.QPen(self.butColor)
            pen.setWidth(6)
            painter.setPen(pen)
            painter.drawLine(0, self.height(), self.width() * self.length, self.height())
        
    def showLine(self, value, length):
        self.lineVis = True
        self.length = value / length
        self.update()
        
    def hideLine(self):
        self.lineVis = False
        self.update()

class Utils(object):
    @classmethod
    def mayaMainWindow(cls):
        from maya.OpenMayaUI import MQtUtil
        from shiboken2       import wrapInstance
        if sys.version_info.major >= 3:
            return wrapInstance(int(MQtUtil.mainWindow()), QtWidgets.QMainWindow)
        else:
            return wrapInstance(long(MQtUtil.mainWindow()), QtWidgets.QMainWindow)
    
    @classmethod
    def addUndo(cls, func):
        def undo(*args, **kwargs):
            cmds.undoInfo(openChunk=True)
            func(*args, **kwargs)
            cmds.undoInfo(closeChunk=True)
        return undo    
        
    @classmethod
    def getUniqueName(cls, name, paddingWidth=0, startIndex=1):
        suffixFormat = '{:0' + str(paddingWidth) + 'd}'  
        newName = name + suffixFormat.format(startIndex)
        
        while cmds.objExists(newName):
            startIndex += 1
            newName = name + suffixFormat.format(startIndex)
        return newName
    
    @classmethod    
    def getSelection(cls):
        sel = om2.MGlobal.getActiveSelectionList()
        return [sel.getDagPath(i) 
                if sel.getDependNode(i).hasFn(om2.MFn.kDagNode) 
                else om2.MFnDependencyNode(sel.getDependNode(i)) 
                for i in range(sel.length())]
                
    @classmethod
    def getNodeLongName(cls, obj):
        if isinstance(obj, om2.MFnDependencyNode):
            name = obj.name()
            return name, name
        else:
            longName = obj.fullPathName()
            return longName.split('|')[-1], longName
            
class NamingToolUI(QtWidgets.QDialog):
    NAMINGTOOLIINSTANCE = None 
    @classmethod
    def UIDisplay(cls):
        if not cls.NAMINGTOOLIINSTANCE: 
            cls.NAMINGTOOLIINSTANCE = NamingToolUI()
        
        if cls.NAMINGTOOLIINSTANCE.isHidden(): 
            cls.NAMINGTOOLIINSTANCE.show() 
        else:
            if cls.NAMINGTOOLIINSTANCE.isMinimized():
                cls.NAMINGTOOLIINSTANCE.showNormal()
            cls.NAMINGTOOLIINSTANCE.raise_() 
            cls.NAMINGTOOLIINSTANCE.activateWindow() 
            
    def __init__(self, parent=Utils.mayaMainWindow()):
        super(self.__class__, self).__init__(parent)
        self.geometry = None
        self.setWindowTitle('Naming Tool')
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setFocusPolicy(QtCore.Qt.StrongFocus); self.setFocus()
        if not sys.version_info.major >= 3:
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.createWidgets()
        self.createLayouts()
        self.createConnections()

    def createWidgets(self):
        self.prefixLabel = QtWidgets.QLabel('Prefix')
        self.prefixLineedit = QtWidgets.QLineEdit()
        regex = QtCore.QRegExp('^[a-zA-Z_][a-zA-Z0-9_]*$')
        self.prefixLineedit.setValidator(QtGui.QRegExpValidator(regex, self.prefixLineedit))
        
        self.suffixLabel = QtWidgets.QLabel('Suffix')
        self.suffixLineedit = QtWidgets.QLineEdit()
        
        self.replaceLabel = QtWidgets.QLabel('Replace')
        self.replaceLineedit = QtWidgets.QLineEdit()
        
        self.withLabel = QtWidgets.QLabel('With')
        self.withLineedit = QtWidgets.QLineEdit()
        
        self.matchCaseSwitch = QtWidgets.QCheckBox('Match Case')
        self.okBut = MyPushButton('Replace Name!')
        
        self.line = QtWidgets.QFrame()
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setStyleSheet("border-top: 2px solid #505050;")
        
        self.batchLabel = QtWidgets.QLabel('Batch Rename')
        self.batchLineedit = QtWidgets.QLineEdit()
        self.batchLineedit.setValidator(QtGui.QRegExpValidator(regex, self.batchLineedit))
        
        self.indexPaddingLabel = QtWidgets.QLabel('Index Padding')
        self.indexPaddingSpinBox = QtWidgets.QSpinBox()
        self.indexPaddingSpinBox.setRange(0, 10000)
        self.indexPaddingSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.indexPaddingSpinBox.setMaximumWidth(80)
        
        self.indexStartLabel = QtWidgets.QLabel('Index Start')
        self.indexStartSpinBox = QtWidgets.QSpinBox()
        self.indexStartSpinBox.setRange(0, 10000)
        self.indexStartSpinBox.setAlignment(QtCore.Qt.AlignCenter)
        self.indexStartSpinBox.setMaximumWidth(80)

    def createLayouts(self):
        subLayout = QtWidgets.QGridLayout()
        subLayout.setSpacing(10)
        subLayout.addWidget(self.prefixLabel, 0, 0)
        subLayout.addWidget(self.prefixLineedit, 0, 1)
        subLayout.addWidget(self.suffixLabel, 0, 2)
        subLayout.addWidget(self.suffixLineedit, 0, 3)

        subLayout.addWidget(self.replaceLabel, 1, 0)
        subLayout.addWidget(self.replaceLineedit, 1, 1)
        subLayout.addWidget(self.withLabel, 1, 2)
        subLayout.addWidget(self.withLineedit, 1, 3)
        
        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.addLayout(subLayout)
        mainLayout.addWidget(self.matchCaseSwitch)
        
        mainLayout.addWidget(self.line)
        subLayout2 = QtWidgets.QGridLayout()
        subLayout2.addWidget(self.batchLabel, 0, 0)
        subLayout2.addWidget(self.batchLineedit, 0, 1)
        subLayout2.addWidget(self.indexPaddingLabel, 1, 0)
        subLayout2.addWidget(self.indexPaddingSpinBox, 1, 1)
        subLayout2.addWidget(self.indexStartLabel, 2, 0)
        subLayout2.addWidget(self.indexStartSpinBox, 2, 1)
        mainLayout.addLayout(subLayout2)
        
        mainLayout.addWidget(self.okBut)
        mainLayout.addStretch()
        
    def createConnections(self):
        self.okBut.clicked.connect(self.updateName)
        
    @Utils.addUndo  
    def updateName(self):
        prefixStr    = self.prefixLineedit.text()
        suffixStr    = self.suffixLineedit.text()
        replaceStr   = self.replaceLineedit.text()
        withStr      = self.withLineedit.text()
        switch       = self.matchCaseSwitch.isChecked()
        bName        = self.batchLineedit.text()
        paddingWidth = self.indexPaddingSpinBox.value()
        startIndex   = self.indexStartSpinBox.value()
        self.replaceName(prefixStr, suffixStr, replaceStr, withStr, 
                         switch, bName, paddingWidth, startIndex)
   
    def replaceName(self, prefix='', suffix='', replace='', with_='', 
                    case_sensitive=True, bName='', paddingWidth=0, startIndex=1):

        sel = Utils.getSelection()
        if not sel: return
        updateInterval = max(100, len(sel) // 100)
        
        for index, node in enumerate(sel):
    
            if random.randint(1, updateInterval) == 18:
                self.okBut.showLine(index, len(sel))
                QtWidgets.QApplication.processEvents()
                
            baseName, longName = Utils.getNodeLongName(node)
            
            if prefix or suffix:
                baseName = '{}{}{}'.format(prefix, baseName, suffix)
            
            if replace:
   
                if not case_sensitive:
                    pattern = re.compile(re.escape(replace), re.IGNORECASE)
                    baseName = pattern.sub(with_, baseName)
                else:
                    baseName = baseName.replace(replace, with_)
                    
            if bName:
                baseName = Utils.getUniqueName(bName, paddingWidth, startIndex)

            try:
                isLocked = cmds.lockNode(longName, q=True, l=True)[0]
                if isLocked: cmds.lockNode(longName, l=False)
                newName = cmds.rename(longName, baseName)
                if isLocked: cmds.lockNode(newName, l=True)    
            except:
                om2.MGlobal.displayWarning('New name has no legal characters')
                

        self.okBut.hideLine()
                  
    def showEvent(self, event):
        if self.geometry:
            self.restoreGeometry(self.geometry) 
            
    def closeEvent(self, event):
        if isinstance(self, NamingToolUI):
            super(NamingToolUI, self).closeEvent(event)
            self.geometry = self.saveGeometry()

if __name__ == '__main__':
    NamingToolUI.UIDisplay()
