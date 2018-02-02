#!/usr/bin/python3

from pysbs import context, sbsenum, sbsgenerator
import os
import click

# Get input from command line
#############################

# - sbsname : without .sbs extension, with absolute or relative path or, by default, in the current directory
# - graphname : name of the Graph to generate in the .sbs file
# - foldername : with absolute or relative path or, by default, the current directory containing the .png files

@click.command()
@click.option('--sbsname', default = 'result', help='.sbs filename to generate, with no extension. \'result\' by default.')
@click.option('--graphname', default = 'MultiSwitchGraph', help='The included Graph name. \'MultiSwitchGraph\' by default.')
@click.option('--foldername', default = os.getcwd(), help='The input .png images folder name, current by default.')
def createMultiSwitchGraph(sbsname, graphname, foldername):
		
	# Create a list of all the files to include in the Switch
	#########################################################
	filelist = []
	choicevalues = {}
	fullsbsname = os.path.abspath('{}.sbs'.format(sbsname))
	fullfoldername = os.path.abspath(foldername)
	fileindex = 1
	for file in os.listdir(fullfoldername):
		if file.endswith(".png"):
			filelist.append(file)
			choicevalues[fileindex] = file
			fileindex += 1
		
	# Define Base Graph offsets
	###########################
	xOffset = [192,0,0]
	 
	# Init the context
	##################
	myContext = context.Context()
	
	# Substance Creation
	####################
	 
	# Create a new Substance with a graph called graphname
	sbsDoc = sbsgenerator.createSBSDocument(aContext = myContext,
	                    aFileAbsPath = fullsbsname,
	                    aGraphIdentifier = graphname)
	 
	# Graph edition
	###############
	
	# Get the graph created with the document
	usedGraph = sbsDoc.getSBSGraph(aGraphIdentifier = graphname)
	
	# Define its parameter
	aParam = usedGraph.addInputParameter(aIdentifier = '_picChoice',
	                            aWidget = sbsenum.WidgetEnum.DROPDOWN_INT1,
	                            aLabel  = 'Picture Choice')
	aParam.setDropDownList(aValueMap=choicevalues)
	aParam.setDefaultValue(1)
	 
	# - Instance of Multi-Switch from the default package library
	multiSwitchNode = usedGraph.createCompInstanceNodeFromPath(aSBSDocument = sbsDoc,
	                    aPath       = 'sbs://blend_switch.sbs/multi_switch_grayscale',
	                    aParameters = {'input_number':len(filelist), 'input_selection':1})
	                    
	# Link its paramater to the one exposed in the Graph
	aDynFunction = multiSwitchNode.setDynamicParameter('input_selection')
	aDynFunction.setToInputParam(aParentGraph = usedGraph, aInputParamIdentifier = '_picChoice')
	
	
	 
	# - Output node with the usage baseColor
	outputNode = usedGraph.createOutputNode(aIdentifier = 'DemoOutput',
	                    aGUIPos       = multiSwitchNode.getOffsetPosition(xOffset),
	                    aOutputFormat = sbsenum.TextureFormatEnum.DEFAULT_FORMAT,
	                    aUsages       = {sbsenum.UsageEnum.BASECOLOR: sbsenum.ComponentsEnum.RGBA})
	 
	usedGraph.connectNodes(aLeftNode = multiSwitchNode, aRightNode = outputNode)
	
	# Start at first row
	row = 0
	
	# Create a row for each file, connect to the switch
	for picture in filelist:
		# Resource creation
		picRes = sbsDoc.createLinkedResource(aResourcePath = os.path.join(fullfoldername, picture),
	                    aResourceTypeEnum = sbsenum.ResourceTypeEnum.BITMAP)
	                    
		# - Bitmap node that uses the previously created resource
		bitmapNode = usedGraph.createBitmapNode(aSBSDocument = sbsDoc,
							aGUIPos     = multiSwitchNode.getOffsetPosition([-192 * 4, row*192, 0]),
							aResourcePath = picRes.getPkgResourcePath(),
							aParameters   = {sbsenum.CompNodeParamEnum.COLOR_MODE:sbsenum.ColorModeEnum.COLOR})
							
		# - Instance of a Greyscale conversion to transform Bitmap to greyscale
		grayNode = usedGraph.createCompFilterNode(aFilter = sbsenum.FilterEnum.GRAYSCALECONVERSION,
							aGUIPos     = bitmapNode.getOffsetPosition(xOffset),
							aParameters = {sbsenum.CompNodeParamEnum.FLATTEN_ALPHA: 1})
		
		# Connect the nodes between them
		usedGraph.connectNodes(aLeftNode = bitmapNode, aRightNode = grayNode)
		usedGraph.connectNodes(aLeftNode = grayNode, aRightNode = multiSwitchNode, aRightNodeInput = "input_{}".format(row + 1))
		
		# Pass to the following row of image
		row += 1
	
	# Write the document
	sbsDoc.writeDoc()

if __name__ == '__main__':
	createMultiSwitchGraph()
