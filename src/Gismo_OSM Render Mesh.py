# OSM render mesh
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# Component icon based on free OSM icon from: <https://icons8.com/web-app/13398/osm>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to create a render mesh from the 3d shapes generated by the "OSM 3D" component.
The component will also create the texture image (material diffuse map file) for the render mesh.
-
Provided by Gismo 0.0.1
    
    input:
        _OSMobjectIndex: An integer which represents an OSM object type.
                         Use "OSM object" component to generate it.
        _threeDeeShapes: Plug in the shapes from the Gismo OSM 3D "threeDeeShapes" output
        _threeDeeKeys: Plug in the keys from the Gismo OSM 3D "threeDeeKeys" output.
        _threeDeeValues: Plug in the values from the Gismo OSM 3D "threeDeeValues" output.
        defaultColor_: This color will be used if supplied _keys and _values do not contain any color information.
                       -
                       If not supplied, the following default color will be used: R=217,G=217,B=217 (grey85).
        textureImageName_: Name of the "textureImagePath" output.
                           -
                           If nothing supplied, "textureImage" will be used as default.
        textureImageFolder_: Folder where "textureImagePath" output will be saved.
                             -
                             If nothing supplied, ".../gismo/OSM_3D" will be used as default.
        bakeIt_: Set to "True" to bake the "textureImagePath" output geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        renderMesh: Render mesh created from _threeDeeShapes.
        textureImagePath: File path to texture image (material diffuse map file) for the renderMesh.
"""

ghenv.Component.Name = "Gismo_OSM Render Mesh"
ghenv.Component.NickName = "OSMrenderMesh"
ghenv.Component.Message = "VER 0.0.1\nJAN_30_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.1\nJAN_29_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import random
import Rhino
import time
import os
import gc


def checkInputData(threeDeeShapes, threeDeeKeys, threeDeeValues, defaultColor, textureImageName, textureImageFolder):
    
    # check inputs
    if (threeDeeShapes.DataCount == 0):
        OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
        validInputData = False
        printMsg = "Please connect the \"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input."
        return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
    
    elif (len(threeDeeShapes.Branches) == 1) and (threeDeeShapes.Branches[0][0] == None):
        # this happens when "OSM 3D" component's "_runIt" input is set to "False"
        OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeShapes\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
    
    
    
    if (len(threeDeeShapes.Branches[0]) == 1) and (type(threeDeeShapes.Branches[0][0]) == Rhino.Geometry.Mesh):
        # if a mesh from "Terrain analysis" component is inputted into the "_threeDeeShapes", then "_threeDeeKeys" and "_threeDeeValues" values are not needed
        OSM3DrenderMesh = False
    else:
        # a mesh from "Terrain analysis" component is NOT inputted into the "_threeDeeShapes", but instead the "threeDeeShapes" output geometry from "OSM 3D" component is inputted. In this case data needs to ALSO be supplied to the "_threeDeeKeys" and "_threeDeeValues" inputs.
        OSM3DrenderMesh = True
        
        if (len(threeDeeKeys) == 0):
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "Please connect the \"threeDeeKeys\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeKeys\" input."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
        
        elif (len(threeDeeKeys) == 1) and (threeDeeKeys[0] == None):
            # this happens when "OSM 3D" component's "_runIt" input is set to "False"
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "There is no data supplied to the \"_threeDeeKeys\" input.\n" + \
                       " \n" + \
                       "Please connect the \"threeDeeKeys\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeKeys\" input.\n" + \
                       "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
        
        
        if (threeDeeValues.DataCount == 0):
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "Please connect the \"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
        
        elif (len(threeDeeValues.Branches) == 1) and (threeDeeValues.Branches[0][0] == None):
            # this happens when "OSM 3D" component's "_runIt" input is set to "False"
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "There is no data supplied to the \"_threeDeeValues\" input.\n" + \
                       " \n" + \
                       "Please connect the \"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input.\n" + \
                       "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
        
        
        if len(threeDeeShapes.Paths) != len(threeDeeValues.Paths):
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "The number of tree branches inputted to the \"_threeDeeShapes\" and \"_threeDeeValues\" inputs do not match.\n" + \
                       " \n" + \
                       "Make sure that you connected:\n" + \
                       "\"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input. And:\n" + \
                       "\"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
        
    
    if (defaultColor == None):
        defaultColor = System.Drawing.Color.FromArgb(217,217,217)
    
    if (textureImageName == None):
        textureImageName = "textureImage"
    else:
        textureImageName = gismo_preparation.cleanString(textureImageName)  # removing "/", "\", " "
    textureImageName = textureImageName + "_%s" % int(time.time())  # always add time.time() to avoid replacing the "textureImagePath"
    
    if (textureImageFolder == None):
        gismoFolder_ = sc.sticky["gismo_gismoFolder"]
        textureImageFolder = os.path.join(gismoFolder_, "osm_3D")  # default: "gismoFolder_\osm_3D"
        textureImageFolder_folderCreated = gismo_preparation.createFolder(textureImageFolder)
    else:
        # something inputted into "textureImageFolder_"
        textureImageFolder_folderCreated = gismo_preparation.createFolder(textureImageFolder)
        if (textureImageFolder_folderCreated == False):
            OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
            validInputData = False
            printMsg = "Supplied \"textureImageFolder_\" is invalid.\nPlease input a valid folder path."
            return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
    textureImage_filePath = os.path.join(textureImageFolder, textureImageName + ".png")  # material diffuse map file
    
    
    # check the "shapeType_" input value set in the "OSM 3D" component. This value will always exist, as "OSM 3D" component will be ran before the "OSM 3d" component
    shapeType = sc.sticky["OSMshapes_shapeType"]
    if shapeType == 1:
        OSM3DrenderMesh = defaultColor = textureImageName = textureImageFolder = textureImage_filePath = None
        validInputData = False
        printMsg = "This component supports only creation of 3d buildings and trees. So \"shapeType_\" input of \"OSM 3D\" component needs to be set to either 0 or 2."
        return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg
    
    
    del threeDeeShapes; del threeDeeKeys; del threeDeeValues  # delete local variables
    validInputData = True
    printMsg = "ok"
    
    return OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg


def US_vs_UK_englishNames(name):
    if name == "grey":
        return "gray"
    else:
        return name


def main(shapesDataTree, keys, valuesDataTree, OSM3DrenderMesh, defaultColor, textureImageName, textureImage_filePath):
    
    meshParam = Rhino.Geometry.MeshingParameters()
    meshParam.SimplePlanes = True
    
    if (OSM3DrenderMesh == True):
        # initial values
        buildingColor_keyIndex = None
        roofColor_keyIndex = None
        treeColor_keyIndex = None
        grassColor_keyIndex = None
        for keyIndex,key in enumerate(keys):
            if (key == "building:colour"):  # short name: "building_c"
                buildingColor_keyIndex = keyIndex
            elif (key == "roof:colour"):  # short name: "roof_colou"
                roofColor_keyIndex = keyIndex
            elif (key == "natural"):
                treeColor_keyIndex = keyIndex
            elif (key == "leisure"):
                grassColor_keyIndex = keyIndex
        
        allMeshesSeparated = []
        if (buildingColor_keyIndex != None) or (roofColor_keyIndex != None) or (treeColor_keyIndex != None) or (grassColor_keyIndex != None):
            shapesLL = shapesDataTree.Branches
            valuesLL = valuesDataTree.Branches
            
            # initial values
            valueBuildingColor = ""
            valueRoofColor = ""
            valueTree = ""
            valueGrass = ""
            for branchIndex,shapesL in enumerate(shapesLL):
                shapes2L = []
                roofsL = []
                shapesLColor = None  # initial value
                roofColor = None  # initial value
                if (len(shapesL) != 0):  # some shape may have been removed with the "OSM ids" component
                    if (buildingColor_keyIndex != None):
                        valueBuildingColor = valuesLL[branchIndex][buildingColor_keyIndex]
                    if (roofColor_keyIndex != None):
                        valueRoofColor = valuesLL[branchIndex][roofColor_keyIndex]
                    if (treeColor_keyIndex != None):
                        valueTree = valuesLL[branchIndex][treeColor_keyIndex]
                    if (grassColor_keyIndex != None):
                        valueGrass = valuesLL[branchIndex][grassColor_keyIndex]
                    
                    if (valueBuildingColor != ""):
                        valueBuildingColor_corrected = US_vs_UK_englishNames(valueBuildingColor)
                        shapesLColor = System.Drawing.ColorTranslator.FromHtml(valueBuildingColor_corrected)  # if building:color is in Hexadecimal format, convert it to RGB
                    elif (valueTree == "tree"):
                        randomGreenColor = random.randint(75,140)
                        shapesLColor = System.Drawing.Color.FromArgb(0,randomGreenColor,0)
                    elif (valueGrass == "park") or (valueGrass == "garden"):
                        randomGreenColor = random.randint(100,190)
                        shapesLColor = System.Drawing.Color.FromArgb(0,randomGreenColor,0)
                    else:
                        # this is for buildings only, not trees, parks and gardens
                        shapesLColor = defaultColor
                    
                    if (valueRoofColor != ""):
                        valueRoofColor_corrected = US_vs_UK_englishNames(valueRoofColor)
                        roofColor = System.Drawing.ColorTranslator.FromHtml(valueRoofColor_corrected)  # if roof:color is in Hexadecimal format, convert it to RGB
                    elif (valueRoofColor == "") and (valueBuildingColor != ""):
                        # if there is no valid "roof:colour", but there is "building:colour", then use the "building:colour" value as "roof:colour" value
                        roofColor = shapesLColor
                    
                    # mesh the shapesL (building with roof included, or tree, or grass)
                    meshes = Rhino.Geometry.Mesh.CreateFromBrep(shapesL[0], meshParam)
                    joinedMesh = Rhino.Geometry.Mesh()
                    for mesh in meshes:
                        joinedMesh.Append(mesh)
                    shapes2L = [joinedMesh]
                    
                    # color the mesh (colorTheShapesL = True)
                    shapes2L[0].VertexColors.Clear()
                    mesh_verticesCount = shapes2L[0].Vertices.Count
                    for i in xrange(mesh_verticesCount):
                        shapes2L[0].VertexColors.Add(shapesLColor)
                    
                    
                    if (roofColor != None):
                        # roof
                        upperShapesLfaceBrep = shapesL[0].Faces[0].DuplicateFace(False)
                        upperShapesLfaceBrep.Flip()  # if it isn't fliped the upperShapesLface_extruded is invalid
                        
                        nakedOnly = False
                        shapesL_randomCrvs = upperShapesLfaceBrep.DuplicateEdgeCurves(nakedOnly)
                        shapesL_startPt = shapesL_randomCrvs[0].PointAtStart
                        extrusionVec = Rhino.Geometry.Vector3d(0,0,0.01)
                        extrudeCrv = Rhino.Geometry.Line(shapesL_startPt, shapesL_startPt + extrusionVec).ToNurbsCurve()
                        cap = True
                        upperShapesLface_extruded = Rhino.Geometry.BrepFace.CreateExtrusion(upperShapesLfaceBrep.Faces[0], extrudeCrv, cap)
                        
                        # mesh the roof
                        meshes = Rhino.Geometry.Mesh.CreateFromBrep(upperShapesLface_extruded, meshParam)
                        joinedMesh = Rhino.Geometry.Mesh()
                        for mesh in meshes:
                            joinedMesh.Append(mesh)
                        roofsL = [joinedMesh]
                        
                        roofsL[0].VertexColors.Clear()
                        mesh_verticesCount = roofsL[0].Vertices.Count
                        for i in xrange(mesh_verticesCount):
                            roofsL[0].VertexColors.Add(roofColor)
                
                
                elif (len(shapesL) == 0):
                    # some shape may have been removed with the "OSM ids" component
                    pass
                
                if len(shapes2L) != 0:
                    allMeshesSeparated.extend(shapes2L)
                if len(roofsL) != 0:
                    allMeshesSeparated.extend(roofsL)
        
        else:
            renderedJoinedMesh = None
            printMsg = "The list of supplied _keys does not contain neither \"building:color\" nor \"roof:color\" keys.\n" + \
                       "These keys are essential so that component could color the inputted shapes."
            level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(level, printMsg)
            print printMsg
            return renderedJoinedMesh
        
        
        # join the "allMeshesSeparated" to "joinedMesh"
        rs.EnableRedraw(False)
        allMeshesSeparated_ids = []
        for mesh in allMeshesSeparated:
            meshId = Rhino.RhinoDoc.ActiveDoc.Objects.AddMesh(mesh)
            allMeshesSeparated_ids.append(meshId)
        
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        numOfSelectedObjs = rs.SelectObjects(allMeshesSeparated_ids)
        
        echo = False
        sucess = rs.Command("NoEcho _-Join _Enter", echo)
        
        select = True
        joinedMesh_id = rs.LastCreatedObjects(select)[0]
        joinedMesh = Rhino.RhinoDoc.ActiveDoc.Objects.Find(joinedMesh_id).Geometry
        
        quiet = True
        deleteSuccess = Rhino.RhinoDoc.ActiveDoc.Objects.Delete(joinedMesh_id, quiet)
        rs.EnableRedraw(True)
        sc.doc = ghdoc
    
    
    elif (OSM3DrenderMesh == False):
        allMeshesSeparated = Rhino.Geometry.Mesh()  # dummy variable, due to need to delete
        allMeshesSeparated_ids = Rhino.Geometry.Mesh()  # dummy variable, due to need to delete
        joinedMesh = shapesDataTree.Branches[0][0]
    
    
    # create render mesh and imageTexture
    renderedJoinedMesh = gismo_createGeometry.createRenderMesh(joinedMesh, textureImage_filePath)
    
    
    
    if bakeIt_:
        
        layerName = "defaultColor=" + "(%s,%s,%s)" % (defaultColor.R, defaultColor.G, defaultColor.B) + "_textureImageName=" + textureImageName
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "RENDER_MESH"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        geometryIds = gismo_preparation.bakeGeometry([renderedJoinedMesh], layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("OSM_RENDER_MESH" + "_" + layerName, geometryIds)
        del geometryIds
    
    # deleting
    del joinedMesh
    del allMeshesSeparated
    del allMeshesSeparated_ids
    gc.collect()
    
    return renderedJoinedMesh


def printOutput(defaultColor, textureImageName, textureImageFolder):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    resultsCompletedMsg = "OSM Render Mesh component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Default color: %s
Texture image name: %s
Texture image folder: %s
    """ % (defaultColor, textureImageName, textureImageFolder)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_createGeometry = sc.sticky["gismo_CreateGeometry"]()
        
        OSM3DrenderMesh, defaultColor, textureImageName, textureImageFolder, textureImage_filePath, validInputData, printMsg = checkInputData(_threeDeeShapes, _threeDeeKeys, _threeDeeValues, defaultColor_, textureImageName_, textureImageFolder_)
        if validInputData:
            if _runIt:
                renderMesh = main(_threeDeeShapes, _threeDeeKeys, _threeDeeValues, OSM3DrenderMesh, defaultColor, textureImageName, textureImage_filePath)
                printOutput(defaultColor, textureImageName, textureImageFolder)
                textureImagePath = textureImage_filePath
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM search component"
        else:
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)