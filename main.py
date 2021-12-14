from posixpath import dirname
import pygame
from os import path,listdir

class Container():
    """
    Container
    ----
    A general container which holds all the general update/draw/layer variables and methods.
    
    ----
    ----
    ----
    Variables
    ----
    - object_dict: a dict which contains all of the GraphicalObject classes, linked with their names; here's an example: {"player":<GraphicalSprite>}; if an object with an already existing name is created, the oldest gets overwritten
    - updatedList: a list which holds all the objects which have been updated in an update cycle
    - layers: a dict which contains the name references of the objects, layer by layer; the layers with lower values are the ones which get drawn first"""
    def __init__(self,screen:pygame.display,dirpath) -> None:
        self.assets={} #A dictionary which holds all the assets
        assetPath=dirpath+"assets/textures"
        self.loadAssets(assetPath)

        self.screen=screen #The screen which is used to draw the objects
        self.object_dict={} #A dictionary which holds all the objects
        GraphicalBase.container=self #The container which is used throughout the program. MUST be initialized before any other object
        GraphicalBase.first=None
        self.updatedList=[]#The objects updated in an update cycle; is needed in order to not update the same object twice
        self.windowPointedBy=[]#List of objects which point the window and will be updated on resize
        self.layers={}#Dict of all layers by which objects are drawn; references are to the objects' names, so that if they are replaced there should be no trouble; every layer is a list with an int by index
    
    def loadAssets(self,assetpath,subpath="") -> dict:
        """This function should load all assets in a folder and store them neatly in a dict, even though most of the work is done by Container.getAsset()"""
        self.assets=self.loadAsset(assetpath+subpath)
    def loadAsset(self,thisPath):
        """Is used to get an image asset. If this is an image, a pygame.Surface object; if this is a directory, the function is re-run at the path of the function"""
        if path.isfile(thisPath):
            return pygame.image.load(thisPath).convert_alpha()
        elif path.isdir(thisPath):
            outputDict={}
            for element in listdir(thisPath+"/"):
                outputDict[element.replace(".png","")]=self.loadAsset(thisPath+"/"+element)
            return outputDict
    def getAsset(self,assetDirList:list):
        """Returns the image at the assetDirList"""
        currentDict=self.assets
        for element in assetDirList:
            currentDict=currentDict[element]
        return currentDict


    def resize(self,width:int,height:int) -> None:
        """A function which should be run when the video window is resized"""
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        if len(self.windowPointedBy)>0:
            GraphicalBase.first=0
            GraphicalBase.container.updatedList=[]
    def draw(self) -> None:
        """Draws all the objects stored in the object_dict"""
        """for keyname in self.object_dict:
            self.object_dict[keyname].draw()"""
        i=0
        j=0
        while i<len(self.layers):
            if j in self.layers:
                for keyname in self.layers[j]:
                    self.object_dict[keyname].draw()
                i+=1
            j+=1


class Updatable():
    """The superclass for all classes which can be updated and which trigger updates for other objects"""
    def __init__(self,varDict:dict) -> None:
        self.upInit(varDict)

    def upInit(self,varDict:dict) -> None:
        """varDict should be something like {"variableName":<correspondingPointer>}; the variables there inserted are set to their pointer value every time the object is updated"""
        self.pointedBy=[]
        self.pointedVarDict={}
        for key in varDict:
            if varDict[key]!=None:
                self.pointedVarDict[key]=varDict[key]#Only sets the non-None values; should be better for performance

    def initPointers(self) -> None:
        """Should be called after Updatable.upInit() from the subclass, in order to correctly initialize the pointers"""
        for key in self.pointedVarDict:
            self.pointedVarDict[key].initialize(self)

    def beginUpdate(self):
        """Tries to start an update cycle, if one hasn't been started yet"""
        #If this gets changed, the logic in Container.resize() should be changed too
        if GraphicalBase.first==None:
            #print("sas")
            GraphicalBase.first=self
            GraphicalBase.container.updatedList=[]
            self.update()
            GraphicalBase.first=None

    def update(self):
        """This function is called when a graphical parameter which can have influence on other objects is called"""
        if self not in GraphicalBase.container.updatedList:
            GraphicalBase.container.updatedList.append(self)#It's important to have this at the beginning so that the class is not updated after this
            #print(self)
            #print(self.pointedVarDict)
            for key in self.pointedVarDict:
                setattr(self,key,self.pointedVarDict[key].getValue())#Sets all the variables to the value of the corresponding pointers#FIXME: is this really needed?
            for elements in self.pointedBy:
                elements.update()
#Graphical classes
class GraphicalBase():
    """The base which holds static variables for graphical objects"""
    container=Container
    def __init__(self) -> None:
        self.container=None
        self.first=None

class GraphicalObject():
    """Base of all graphical objects; holds its static variables in GraphicalBase"""
    def __init__(self,name:str,pos_functions,size_functions,layer=0,clickable=False) -> None:
        """
        This function provides to correctly intialize a GraphicalObject so that it can later be easily used

        Variables:
        - name: the name given to the object, used to identify it from other functions. It currently must be specified.
        """
        GraphicalBase.container.object_dict[name]=self #Adds the object to the container's object_dict
        #TODO: should add a random name specifier; should prob use a static variable
        self._name=name

        self._x=0
        self._y=0
        self._xSize=0
        self._ySize=0

        print(size_functions[0]())
        print(size_functions[1]())

        self.x_funct=pos_functions[0] if pos_functions[0]!=None else lambda:self._x
        self.y_funct=pos_functions[1] if pos_functions[1]!=None else lambda:self._y
        self.xSize_funct=size_functions[0] if size_functions[0]!=None else lambda:self._xSize
        self.ySize_funct=size_functions[1] if size_functions[1]!=None else lambda:self._ySize

        #Adds in right layer
        if layer not in GraphicalBase.container.layers:
            GraphicalBase.container.layers[layer]=[]
        if self not in GraphicalBase.container.layers[layer]:
            GraphicalBase.container.layers[layer].append(self._name)
    
    #Properties
    @property
    def x(self):
        return self.x_funct()
    @x.setter
    def x(self,value):
        self._x=value
    @property
    def y(self):
        return self.y_funct()
    @y.setter
    def y(self,value):
        self._y=value
    @property
    def xSize(self):
        return self.xSize_funct()
    @xSize.setter
    def xSize(self,value):
        self._xSize=value
    @property
    def ySize(self):
        return self.ySize_funct()
    @ySize.setter
    def ySize(self,value):
        self._ySize=value

    def draw(self):
        """This is where the drawing action should be; needs to be overwritten"""
        pass
    
    def __str__(self):
        #FIXME: still uses old variables
        return "<'name':'"+self._name+"', 'pos':("+str(self.x)+","+str(self.y)+"), 'size':("+str(self.xSize)+","+str(self.ySize)+"), 'pointers':{"+str(self.pointedVarDict)+"}>"

    #TODO: add framed movement

class GraphicalRectangle(GraphicalObject):
    def __init__(self, name: str, rect=pygame.Rect((0,0),(1,1)),layer=0,color=(0,0,0),pos_pointers=(None,None),size_pointers=(None,None),init_update=True) -> None:
        super().__init__(name,pos_pointers,size_pointers,layer=layer)
        self._rect=rect
        self._color=color

        if init_update:
            self.beginUpdate()#TODO: see if this is actually ok
    
    @property
    def x(self):
        return self._rect.left
    @x.setter
    def x(self,value):
        self._rect.left=value
        self.beginUpdate()
    @property
    def y(self):
        return self._rect.top
    @y.setter
    def y(self,value):
        self._rect.top=value
        self.beginUpdate()
    @property
    def xSize(self):
        return self._rect.width
    @xSize.setter
    def xSize(self,value):
        self._rect.width=value
        self.beginUpdate()
    @property
    def ySize(self):
        return self._rect.height
    @ySize.setter
    def ySize(self,value):
        self._rect.height=value
        self.beginUpdate()
    
    def draw(self):
        pygame.draw.rect(surface=GraphicalBase.container.screen,color=self._color,rect=self._rect)

class GraphicalText(GraphicalObject):
    """A quick and easy way to display text"""
    def __init__(self, name: str, pos_pointers, size_pointers, layer=0, wrap=False, clickable=False) -> None:
        #Should look into this: https://stackoverflow.com/questions/50280553/adding-text-to-a-rectangle-that-can-be-resized-and-moved-on-pygame-without-addo
        super().__init__(name, pos_pointers, size_pointers, layer=layer, clickable=clickable)

class GraphicalSprite(GraphicalObject):
    def __init__(self, name: str, image=[],coords=(0,0),layer=0,size=(None,None),pos_pointers=(None,None),size_pointers=(None,None),init_update=True) -> None:
        super().__init__(name,pos_pointers,size_pointers,layer=layer)
        if len(image)>0:
            try:
                self._base_image=GraphicalBase.container.getAsset(image)#Stores the base image; is used in order to prevent messiness when rescaling
            except Exception as e:
                image=[]
        if len(image)==0:#Not an else so that it can be entered if load fails
            self._base_image=GraphicalBase.container.getAsset(["nullimage"])
        self._image=self._base_image

    def draw(self):
        #TODO: add a size setter
        GraphicalBase.container.screen.blit(self._image,(self.x,self.y))

class GraphicalFrame(GraphicalObject):
    """Just a placeholder meant to store values useful for other classes"""
    def __init__(self, name: str, pos=(0,0), size=(1,1), pos_pointers=(None,None), size_pointers=(None,None)) -> None:
        super().__init__(name, pos_pointers, size_pointers, layer=0)
        self._x=pos[0]
        self._y=pos[1]
        self._xSize=size[0]
        self._ySize=size[1]

    #Properties
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,value):
        self._x=value
        self.beginUpdate()
    @property
    def y(self):
        return self._y
    @y.setter
    def y(self,value):
        self._y=value
        self.beginUpdate()
    @property
    def xSize(self):
        return self._xSize
    @xSize.setter
    def xSize(self,value):
        self._xSize=value
        self.beginUpdate()
    @property
    def ySize(self):
        return self._ySize
    @ySize.setter
    def ySize(self,value):
        self._ySize=value
        self.beginUpdate()

#Pointers
class Pointer():
    """The base object for pointers"""
    def __init__(self) -> None:
        self.last=None
    def calculateValue(self):
        pass
    def initialize(self,outer_object):
        pass
    def getValue(self):
        if self not in GraphicalBase.container.updatedList:#Recalculates the value only if it hasn't been calculated in this cycle
            GraphicalBase.container.updatedList.append(self)
            self.last=self.calculateValue()
        return self.last
    def __str__(self) -> str:
        return "->None"
    def __repr__(self) -> str:
        return self.__str__()

#Static pointers
class IntPointer(Pointer):
    def __init__(self, value:int) -> None:
        self.value=value
    def calculateValue(self):
        return self.value
    def __str__(self) -> str:
        return "->"+str(self.value)

#Updatable pointers
class UpIntPointer(Updatable,Pointer):
    """A pointer which points at an int value and which can trigger updates for pointing objects"""
    def __init__(self,value:int) -> None:#Init is ok
        """The value class is the base value"""
        self._value=value
        super().upInit({"value":self})
        super().initPointers()
        self.value=self._value

    @property
    def value(self):
        return self._value
    @value.setter
    def value(self,amount):
        self._value=amount
        self.beginUpdate()

    def calculateValue(self):
        return self.value
    def initialize(self, outer_object):
        self.pointedBy.append(outer_object)
    def getValue(self):
        return self.calculateValue()
    def __str__(self) -> str:
        return "~>"+str(self.value)
#Object pointers
class VariablePointer(Pointer):
    """Returns the value of a variable in a given object; before the value is returned, the object is updated; you can't make self-references, but you can find a way around the problem by modifying the same targeted value"""
    def __init__(self, objectName:str, variable:str) -> None:
        super().__init__()
        self.objectName=objectName
        self.variable=variable
    def calculateValue(self):
        reference(self.objectName).update()#Updates the object in ordere to have correct values
        return getattr(reference(self.objectName),self.variable)
    def initialize(self,outer_object):
        reference(self.objectName).pointedBy.append(outer_object)
    def __str__(self) -> str:
        return "=>("+str(reference(self.objectName).pointedVarDict[self.variable])+")"
#TODO: Add self-reference for variables

class WindowPointer(Pointer):
    """Returns the height or width of the game window"""
    def __init__(self,varInt:int):
        """The varInt should be 0 for width and 1 for height"""
        self.varInt=varInt
    def calculateValue(self):
        if self.varInt==0:
            return GraphicalBase.container.screen.get_width()
        else:
            return GraphicalBase.container.screen.get_height()
    def initialize(self, outer_object):
        GraphicalBase.container.windowPointedBy.append(outer_object)
    def __str__(self) -> str:
        if self.varInt==0:
            return "~>container.screen.get_width()"
        else:
            return "~>container.screen.get_height()"

#Operational pointers
class ComparativePointer(Pointer):
    """Is used to compare two pointers and return a single value"""
    def __init__(self, pointer1:Pointer, pointer2:Pointer) -> None:
        self.pointer1=pointer1
        self.pointer2=pointer2
    def calculateValue(self):
        return self.pointer1.calculateValue()
    def initialize(self, outer_object):#Initializes the inner objects
        self.pointer1.initialize(outer_object)
        self.pointer2.initialize(outer_object)

class SumPointer(ComparativePointer):
    """Returns the sum of the values of the two given pointers"""
    def calculateValue(self):
        return self.pointer1.getValue()+self.pointer2.getValue()
    def __str__(self) -> str:
        return "~>("+str(self.pointer1)+" + "+str(self.pointer2)+")"

class SubPointer(ComparativePointer):
    """Returns the subtraction of the values of the two given pointers"""
    def calculateValue(self):
        return self.pointer1.getValue()-self.pointer2.getValue()
    def __str__(self) -> str:
        return "~>("+str(self.pointer1)+" - "+str(self.pointer2)+")"

class DivPointer(ComparativePointer):
    """Returns the division of the values of the two given pointers; Pointer1/Pointer2"""
    def calculateValue(self):
        return self.pointer1.getValue()/self.pointer2.getValue()
    def __str__(self) -> str:
        return "~>("+str(self.pointer1)+" / "+str(self.pointer2)+")"

class MultPointer(ComparativePointer):
    """Returns the multiplication of the values of the two given pointers; Pointer1*Pointer2"""
    def calculateValue(self):
        return self.pointer1.getValue()*self.pointer2.getValue()
    def __str__(self) -> str:
        return "~>("+str(self.pointer1)+" * "+str(self.pointer2)+")"

#Confrontative pointers
class MaxPointer(ComparativePointer):
    """Returns the pointer with the bigger value between the two given"""
    def calculateValue(self):
        if self.pointer1.getValue()>=self.pointer2.getValue():
            return self.pointer1.getValue()
        else:
            return self.pointer2.getValue()
    def __str__(self) -> str:
        return "~>max("+str(self.pointer1)+" , "+str(self.pointer2)+")"

#Functions
def reference(objectName:str) -> GraphicalObject:
    """Returns the object with the name corresponding to objectName"""
    return GraphicalBase.container.object_dict[objectName]