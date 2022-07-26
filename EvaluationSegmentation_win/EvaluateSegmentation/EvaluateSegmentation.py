import os
import unittest
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import SimpleITK as sitk
import numpy as np
import shutil
#
# EvaluateSegmentation
#

class EvaluateSegmentation(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "EvaluateSegmentation"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Mehran Azimbagirad"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#EvaluateSegmentation">module documentation</a>.
"""
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

    # Additional initialization step after application startup is complete
    slicer.app.connect("startupCompleted()", registerSampleData)


def registerSampleData():
  """
  Add data sets to Sample Data module.
  """

  import SampleData
  iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

  # EvaluateSegmentation1
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='EvaluateSegmentation',
    sampleName='EvaluateSegmentation1',
    # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
    # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
    thumbnailFileName=os.path.join(iconsPath, 'EvaluateSegmentation1.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
    fileNames='EvaluateSegmentation1.nrrd',
    # Checksum to ensure file integrity. Can be computed by this command:
    #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
    checksums = 'SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
    # This node name will be used when the data set is loaded
    nodeNames='EvaluateSegmentation1'
  )

  # EvaluateSegmentation2
  SampleData.SampleDataLogic.registerCustomSampleDataSource(
    # Category and sample name displayed in Sample Data module
    category='EvaluateSegmentation',
    sampleName='EvaluateSegmentation2',
    thumbnailFileName=os.path.join(iconsPath, 'EvaluateSegmentation2.png'),
    # Download URL and target file name
    uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
    fileNames='EvaluateSegmentation2.nrrd',
    checksums = 'SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
    # This node name will be used when the data set is loaded
    nodeNames='EvaluateSegmentation2'
  )
class EvaluateSegmentationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  def __init__(self, parent=None):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.__init__(self, parent)
    VTKObservationMixin.__init__(self)  # needed for parameter node observation
    self.logic = None
    self._parameterNode = None
    self._updatingGUIFromParameterNode = False

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    ScriptedLoadableModuleWidget.setup(self)

    # Load widget from .ui file (created by Qt Designer).
    uiWidget = slicer.util.loadUI(self.resourcePath('UI/EvaluateSegmentation.ui'))
    self.layout.addWidget(uiWidget)
    self.ui = slicer.util.childWidgetVariables(uiWidget)

    uiWidget.setMRMLScene(slicer.mrmlScene)
    # in batch mode, without a graphical user interface.
    self.logic = EvaluateSegmentationLogic()
    # Connections
    # These connections ensure that we update parameter node when scene is closed
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
    self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)
#******************************************************* 1 **********************************************************************
    # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
    # (in the selected parameter node).
    self.ui.RefLabel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.TestLabel.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.DirectoryButton.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    self.ui.tableWidget.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
    #self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
    #self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
    #self.ui.invertedOutputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

    # Buttons
    self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

    # Make sure parameter node is initialized (needed for module reload)
    self.initializeParameterNode()

  def cleanup(self):
    """
    Called when the application closes and the module widget is destroyed.
    """
    self.removeObservers()

  def enter(self):
    """
    Called each time the user opens this module.
    """
    # Make sure parameter node exists and observed
    self.initializeParameterNode()

  def exit(self):
    """
    Called each time the user opens a different module.
    """
    # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
    self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

  def onSceneStartClose(self, caller, event):
    """
    Called just before the scene is closed.
    """
    # Parameter node will be reset, do not use it anymore
    self.setParameterNode(None)

  def onSceneEndClose(self, caller, event):
    """
    Called just after the scene is closed.
    """
    # If this module is shown while the scene is closed then recreate a new parameter node immediately
    if self.parent.isEntered:
      self.initializeParameterNode()

  def initializeParameterNode(self):
    """
    Ensure parameter node exists and observed.
    """
    # Parameter node stores all user choices in parameter values, node selections, etc.
    # so that when the scene is saved and reloaded, these settings are restored.

    self.setParameterNode(self.logic.getParameterNode())

    # Select default input nodes if nothing is selected yet to save a few clicks for the user
    if not self._parameterNode.GetNodeReference("InputVolume1") :
      firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
      if firstVolumeNode:
        self._parameterNode.SetNodeReferenceID("InputVolume1", firstVolumeNode.GetID())

  def setParameterNode(self, inputParameterNode):
    """
    Set and observe parameter node.
    Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
    """

    if inputParameterNode:
      self.logic.setDefaultParameters(inputParameterNode)

    # Unobserve previously selected parameter node and add an observer to the newly selected.
    # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
    # those are reflected immediately in the GUI.
    if self._parameterNode is not None:
      self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
    self._parameterNode = inputParameterNode
    if self._parameterNode is not None:
      self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    # Initial GUI update
    self.updateGUIFromParameterNode()

  def updateGUIFromParameterNode(self, caller=None, event=None):
    """
    This method is called whenever parameter node is changed.
    The module GUI is updated to show the current state of the parameter node.
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
    self._updatingGUIFromParameterNode = True
#******************************************************* 2 **********************************************************************

    # Update node selectors and sliders
    self.ui.RefLabel.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume1"))
    self.ui.TestLabel.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume2"))
    #self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
    #self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
    #self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
    #self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")
    self.ui.DirectoryButton.directory=self._parameterNode.GetParameter("dir_path")
    #self.ui.tableWidget=self._parameterNode.GetNodeReference("results")
    # Update buttons states and tooltips
    if self._parameterNode.GetNodeReference("InputVolume1") and self._parameterNode.GetNodeReference("InputVolume2"):
      self.ui.applyButton.toolTip = "Compute similarity metrics"
      self.ui.applyButton.enabled = True
    else:
      self.ui.applyButton.toolTip = "Select input and output volume nodes"
      self.ui.applyButton.enabled = False

    # All the GUI updates are done
    self._updatingGUIFromParameterNode = False

  def updateParameterNodeFromGUI(self, caller=None, event=None):
    """
    This method is called when the user makes any change in the GUI.
    The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
    """

    if self._parameterNode is None or self._updatingGUIFromParameterNode:
      return

    wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
#******************************************************* 3 **********************************************************************

    self._parameterNode.SetNodeReferenceID("InputVolume1", self.ui.RefLabel.currentNodeID)
    self._parameterNode.SetNodeReferenceID("InputVolume2", self.ui.TestLabel.currentNodeID)
    #self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
    #self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
    #self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
    #self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)
    self._parameterNode.SetParameter("dir_path", self.ui.DirectoryButton.directory)
    #self._parameterNode.setMRMLTableViewNode("results", self.ui.tableWidget.currentNodeID)
    self._parameterNode.EndModify(wasModified)

  def onApplyButton(self):
    """
    Run processing when user clicks "Apply" button.
    """
    try:
#******************************************************* 4 **********************************************************************

      # Compute output
      self.logic.process(self.ui.RefLabel.currentNode(),self.ui.TestLabel.currentNode(), self.ui.DirectoryButton.directory,self.ui.tableWidget)

      

    except Exception as e:
      slicer.util.errorDisplay("Failed to compute results: "+str(e))
      import traceback
      traceback.print_exc()


#
# EvaluateSegmentationLogic
#

class EvaluateSegmentationLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self):
    """
    Called when the logic class is instantiated. Can be used for initializing member variables.
    """
    ScriptedLoadableModuleLogic.__init__(self)

  def setDefaultParameters(self, parameterNode):
    """
    Initialize parameter node with default settings.
    """
    #if not parameterNode.GetParameter("Threshold"):
    #  parameterNode.SetParameter("Threshold", "100.0")
    #if not parameterNode.GetParameter("Invert"):
    #  parameterNode.SetParameter("Invert", "false")
#******************************************************* 5 **********************************************************************

  def process(self, RefLabel,TestLabel, directory,tableNode):


    if not RefLabel or not TestLabel:
      raise ValueError("Input or output volume is invalid")

    import time
    startTime = time.time()
    logging.info('Processing started')

    # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
    # cliParams = {
    #   'InputVolume1': RefLabel.GetID(),
    #   'InputVolume2': TestLabel.GetID(),
    #   'OutputVolume': outputVolume.GetID(),
    #   'ThresholdValue' : imageThreshold,
    #   'ThresholdType' : 'Above' if invert else 'Below'
    #   }
    #cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
    # We don't need the CLI module node anymore, remove it to not clutter the scene with it
    #slicer.mrmlScene.RemoveNode(cliNode)
    #execPath = os.path.join(os.path.dirname(__file__), 'Resources/EvaluateSegmentation.exe')
    try:
        shutil.rmtree(os.path.dirname(__file__)+'/temp')
        shutil.rmtree(os.path.dirname(__file__)+'/temp')
    except:
        os.mkdir(os.path.dirname(__file__)+'/temp')
    execPath = os.path.dirname(__file__)+'/Resources/EvaluateSegmentation.exe'
    #print(execPath+'EvaluateSegmentation.exe -h')
    progressbar = slicer.util.createProgressDialog(autoClose=True)
    progressbar.value = 50
    progressbar.labelText = "similarity calculation started ..."
    #os.system(execPath+'EvaluateSegmentation.exe')#+str(config)+" filename"
    ref_label=extract_image(RefLabel,os.path.dirname(__file__)+'/temp')
    test_label=extract_image(TestLabel,os.path.dirname(__file__)+'/temp')
    commandLine = [execPath, ref_label,test_label,'-xml',directory+'/result.xml']
    print('command line:',commandLine)
    proc = slicer.util.launchConsoleProcess(commandLine, useStartupEnvironment=False)
    slicer.util.logProcessOutput(proc)
    stopTime = time.time()

    #slicer.util.pip_install("pandas")
    slicer.util.pip_install("xmltodict")
    #slicer.util.pip_install("xml")
    xml_file=directory+'/result.xml'
    import xmltodict
    with open(xml_file) as fd:
        dict = xmltodict.parse(fd.read())
    #print('dice keys:',dict)
    #print('\n ***************')
    #print('dice keys:',dict['measurement']['metrics'])
    #df = pd.read_html(xml)
    #print('\n dir (tablewidget): \n',dir(tableNode.item),'\n')
    #tableNode = slicer.vtkMRMLTableNode()
    tableNode.setRowCount(29)
    tableNode.setColumnCount(4)
    tableNode.setItem(0, 0, qt.QTableWidgetItem("Metrics"))
    tableNode.setItem(0, 1, qt.QTableWidgetItem("Full name"))
    tableNode.setItem(0, 2, qt.QTableWidgetItem("Value"))
    tableNode.setItem(0, 3, qt.QTableWidgetItem("Unit"))
    tableNode.item(0, 0).setBackground(qt.QColor(200, 200, 200))
    tableNode.item(0, 1).setBackground(qt.QColor(200, 200, 200))
    tableNode.item(0, 2).setBackground(qt.QColor(200, 200, 200))
    tableNode.item(0, 3).setBackground(qt.QColor(200, 200, 200))
    row_ind=1
    dict['measurement']['metrics']['SNSVTY']['@name']='Sensitivity or Recall or true positive rate)'        
    csv_file=directory+'/result.csv'
    with open(csv_file, 'w') as f:
        for metric in dict['measurement']['metrics']:
            try:
                unit=dict['measurement']['metrics'][metric]['@unit']
            except:
                unit=''  
            #print(metric,'\t',dict['measurement']['metrics'][metric]['@name'],'\t', dict['measurement']['metrics'][metric]['@value'],unit,'\n')  
            f.write("%s,%s,%s,%s\n" % (metric,dict['measurement']['metrics'][metric]['@name'],dict['measurement']['metrics'][metric]['@value'],unit))
            #tableNode.AddEmptyRow()
            #tableNode.SetCellText(row_ind,0,metric)
            tableNode.setItem(row_ind, 0, qt.QTableWidgetItem(metric))
            tableNode.setItem(row_ind, 1, qt.QTableWidgetItem(dict['measurement']['metrics'][metric]['@name']))
            tableNode.setItem(row_ind, 2, qt.QTableWidgetItem(dict['measurement']['metrics'][metric]['@value']))
            if (row_ind<=8 or (row_ind>=16 and row_ind<=20 ) ) and float(dict['measurement']['metrics'][metric]['@value'])>0.9:
                tableNode.item(row_ind, 2).setBackground(qt.QColor(100, 200, 100))
            elif (row_ind<=8 or (row_ind>=16 and row_ind<=20 ) ) and float(dict['measurement']['metrics'][metric]['@value'])<0.9:
                tableNode.item(row_ind, 2).setBackground(qt.QColor(200, 100, 100))
            else:
                tableNode.item(row_ind, 2).setBackground(qt.QColor(220, 220, 220))
            tableNode.setItem(row_ind, 3, qt.QTableWidgetItem(unit))
            row_ind=row_ind+1
        ref_vol=dict['measurement']['metrics']['REFVOL']['@value']
        test_vol=dict['measurement']['metrics']['SEGVOL']['@value']
        AVD=abs(int(ref_vol)-int(test_vol))
        f.write("%s,%s,%s,%s\n" % ('AVD','Absolute Volume Difference',str(AVD),'voxel^3'))
        tableNode.setItem(row_ind, 0, qt.QTableWidgetItem('AVD'))
        tableNode.setItem(row_ind, 1, qt.QTableWidgetItem('Absolute Volume Difference'))
        tableNode.setItem(row_ind, 2, qt.QTableWidgetItem(str(AVD)))
        tableNode.setItem(row_ind, 3, qt.QTableWidgetItem('voxel'))
        tableNode.item(row_ind, 2).setBackground(qt.QColor(220, 220, 220))
    #slicer.mrmlScene.AddNode(tableNode)
    #tableView=slicer.qMRMLTableView()
    #tableView.setMRMLTableNode(tableNode)
    #tableView.show()
    progressbar.value = 100
    logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')
    




class EvaluateSegmentationTest(ScriptedLoadableModuleTest):
  def setUp(self):
    slicer.mrmlScene.Clear()
  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_EvaluateSegmentation1()
  def test_EvaluateSegmentation1(self):

    self.delayDisplay("Starting the test")
    # Get/create input data
    # import SampleData
    # registerSampleData()
    # RefLabel = SampleData.downloadSample('EvaluateSegmentation1')
    # self.delayDisplay('Loaded test data set')

    # inputScalarRange = RefLabel.GetImageData().GetScalarRange()
    # self.assertEqual(inputScalarRange[0], 0)
    # self.assertEqual(inputScalarRange[1], 695)

    # outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
    # threshold = 100
    # Test the module logic
    logic = EvaluateSegmentationLogic()
    self.delayDisplay('Test passed')
#******************** Functions ***************************************
def extract_image(input_label,output_path):
    #print('dir of inputVolume.GetImageData()=',dir(input_label.GetImageData()))
    label = input_label.GetImageData()
    #label=sitk.ReadImage(input_label)
    #label=slicer.util.addVolumeFromArray(input_label.GetID()) 
    #print(type(label))   
    dirs = np.zeros([3,3])
    input_label.GetIJKToRASDirections(dirs)
    dirs=np.multiply(dirs,np.array([[-1,-1,-1],[-1,-1,-1],[1,1,1]]))
    direction=np.reshape(dirs,(1,9)).tolist()
    #print('input_label.GetDirection()======',direction[0])
    #print('type(label)=',type(label))
    origin=input_label.GetOrigin()
    #print(origin[0], type(origin))
    labelArray =slicer.util.array(input_label.GetID())
    resultImage = sitk.GetImageFromArray(labelArray)
    resultImage.SetSpacing(input_label.GetSpacing())
    resultImage.SetOrigin((origin[0]*-1.0, origin[1]*-1.0,origin[2]) )
    resultImage.SetDirection(direction[0])
    l_name=output_path+'/'+input_label.GetName()+'.nii.gz'
    print(l_name)
    sitk.WriteImage(resultImage, l_name)
    #dirs1 = vtk.vtkMatrix4x4()
    #input_label.GetIJKToRASDirectionMatrix(dirs1)
    #print('input_label.GetDirection()======',dirs1)
    return l_name