from posixpath import dirname
import pygame
from os import path

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
    def __init__(self,screen:pygame.display) -> None:
        self.screen=screen
        self.object_dict={}
        GraphicalBase.container=self
        GraphicalBase.first=None
        self.updatedList=[]#The objects updated in an update cycle; is needed in order to not update the same object twice
        self.windowPointedBy=[]#List of objects which point the window and will be updated on resize
        self.layers={}#Dict of all layers by which objects are drawn; references are to the objects' names, so that if they are replaced there should be no trouble; every layer is a list with an int by index
    def resize(self,width:int,height:int) -> None:
        """A function which should be run when the video window is resized"""
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        if len(self.windowPointedBy)>0:
            GraphicalBase.first=0
            GraphicalBase.container.updatedList=[]
            for graphicalObject in self.windowPointedBy:
                graphicalObject.update()
                #print(graphicalObject)

            GraphicalBase.first=None
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

    def loadAssets(self,path) -> None:
        """This function should load all assets in a folder and store them neatly in a dict"""
        pass


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
                setattr(self,key,self.pointedVarDict[key].getValue())#Sets all the variables to the value of the corresponding pointers
            for elements in self.pointedBy:
                elements.update()
#Graphical classes
class GraphicalBase():
    """The base which holds static variables for graphical objects"""
    def __init__(self) -> None:
        self.container=None
        self.first=None

class GraphicalObject(Updatable):
    """Base of all graphical objects; holds its static variables in GraphicalBase"""
    def __init__(self,name:str,pos_pointers,size_pointers,layer=0) -> None:
        GraphicalBase.container.object_dict[name]=self
        super().__init__({"x":pos_pointers[0],"y":pos_pointers[1],"xSize":size_pointers[0],"ySize":size_pointers[1]})
        self.initPointers()
        #TODO: should add a random name specifier; should prob use a static variable
        self._name=name
        self.pointedBy=[]
        self.sizePointers=size_pointers
        self.posPointers=pos_pointers

        #Adds in right layer
        if layer not in GraphicalBase.container.layers:
            GraphicalBase.container.layers[layer]=[]
        if self not in GraphicalBase.container.layers[layer]:
            GraphicalBase.container.layers[layer].append(self._name)

        """if self.posPointers[0]!=None:
            self.posPointers[0].initialize(self)
        if self.posPointers[1]!=None:
            self.posPointers[1].initialize(self)

        if self.sizePointers[0]!=None:#Initialization in order to fill the pointedBy list
            self.sizePointers[0].initialize(self)
        if self.sizePointers[1]!=None:
            self.sizePointers[1].initialize(self)"""
    
    #Properties
    @property
    def x(self):
        return None
    @x.setter
    def x(self,value):
        self.beginUpdate()
    @property
    def y(self):
        return None
    @y.setter
    def y(self,value):
        self.beginUpdate()
    @property
    def xSize(self):
        return None
    @xSize.setter
    def xSize(self,value):
        self.beginUpdate()
    @property
    def ySize(self):
        return None
    @ySize.setter
    def ySize(self,value):
        self.beginUpdate()

    def draw(self):
        """This is where the drawing action should be"""
        pass

    """def beginUpdate(self):
        #If this gets changed, the logic in Container.resize() should be changed too
        if GraphicalBase.first==None:
            GraphicalBase.first=self
            GraphicalBase.container.updatedList=[]
            self.update()
            GraphicalBase.first=None

    def update(self):
        #This function is called when a graphical parameter which can have influence on other objects is called
        if self not in GraphicalBase.container.updatedList:
            GraphicalBase.container.updatedList.append(self)#It's important to have this at the beginning so that the class is not updated after this
            #print(self)
            if self.posPointers[0]!=None:#x pos
                self.x=self.posPointers[0].getValue()
            if self.posPointers[1]!=None:#y pos
                self.y=self.posPointers[1].getValue()
            if self.sizePointers[0]!=None:#x size
                self.xSize=self.sizePointers[0].getValue()
            if self.sizePointers[1]!=None:#y size
                self.ySize=self.sizePointers[1].getValue()
            for elements in self.pointedBy:
                elements.update()"""
    
    def __str__(self):
        return "<'name':'"+self._name+"', 'pos':("+str(self.x)+","+str(self.y)+"), 'size':("+str(self.xSize)+","+str(self.ySize)+")>"

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

class GraphicalSprite(GraphicalObject):
    def __init__(self, name: str, image=pygame.image.load(path.dirname(__file__)+"/nullimage.png"),coords=(0,0),layer=0,size=(None,None),pos_pointers=(None,None),size_pointers=(None,None),init_update=True) -> None:#TODO: add a way to handle size
        super().__init__(name,pos_pointers,size_pointers,layer=layer)
        self._base_image=image#Stores the base image; is used in order to prevent messiness when rescaling
        self._image=image
        self._coords=coords#TODO: add a way to handle coords

        if size[0]!=None:
            self.xSize=size[0]
            init_update=False
        if size[1]!=None:
            self.ySize=size[1]
            init_update=False

        if init_update:
            self.beginUpdate()#TODO: see if this is actually ok

    @property
    def x(self):
        return self._coords[0]
    @x.setter
    def x(self,value):
        self._coords=(value,self._coords[1])
        self.beginUpdate()
    @property
    def y(self):
        return self._coords[1]
    @y.setter
    def y(self,value):
        self._coords=(self._coords[0],value)
        self.beginUpdate()
    @property
    def xSize(self):
        return self._image.get_width()
    @xSize.setter
    def xSize(self,value):
        self._image=pygame.transform.scale(self._base_image,(value,self.ySize))
        self.beginUpdate()
    @property
    def ySize(self):
        return self._image.get_height()
    @ySize.setter
    def ySize(self,value):
        self._image=pygame.transform.scale(self._base_image,(self.xSize,value))
        self.beginUpdate()

    def draw(self):
        GraphicalBase.container.screen.blit(self._image,self._coords)
#TODO: smarter constructors

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

#Static pointers
class IntPointer(Pointer):
    def __init__(self, value:int) -> None:
        self.value=value
    def calculateValue(self):
        return self.value

#Updatable pointers
class UpIntPointer(Updatable,Pointer):
    """A pointer which points at an int value and which can trigger updates for pointing objects"""
    def __init__(self,value:int) -> None:#Init is ok
        """The value class is the base value"""
        self._value=value
        super().upInit({"value":self})
        self._value=self.pointedVarDict["value"].getValue()#Sets value for inner value, in case it gets called before stuff happens
        super().initPointers()

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

#Object pointers
class VariablePointer(Pointer):
    """Returns the value of a variable in a given object; before the value is returned, the object is updated; you can't make self-references, but you can find a way around the problem by modifying the same targeted value"""
    def __init__(self, object:GraphicalObject, variable:str) -> None:
        super().__init__()
        self.object=object
        self.variable=variable
    def calculateValue(self):
        self.object.update()#Updates the object in ordere to have correct values
        return getattr(self.object,self.variable)
    def initialize(self,outer_object):
        self.object.pointedBy.append(outer_object)
#TODO: Add self-reference for variables
#TODO: Add a better way to refer to objects
#TODO: Add a way to refer to an object variable; should prob do this with GraphicalBase and with setattr/getattr; there should be a store of dynamic pointers which update all the related objects when they are modified

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

class SubPointer(ComparativePointer):
    """Returns the subtraction of the values of the two given pointers"""
    def calculateValue(self):
        return self.pointer1.getValue()-self.pointer2.getValue()

class DivPointer(ComparativePointer):
    """Returns the division of the values of the two given pointers; Pointer1/Pointer2"""
    def calculateValue(self):
        return self.pointer1.getValue()/self.pointer2.getValue()

#Confrontative pointers
class MaxPointer(ComparativePointer):
    """Returns the pointer with the bigger value between the two given"""
    def calculateValue(self):
        if self.pointer1.getValue()>=self.pointer2.getValue():
            return self.pointer1.getValue()
        else:
            return self.pointer2.getValue()