import pygame

class Container():
    """A general container which holds all the general update/draw/layer variables and methods.
    
    It contains all of the GraphicalObject objects in its object_dict; if two GraphicalObjects end up having the same name, the first one will be overwritten"""
    def __init__(self,screen:pygame.display) -> None:
        self.screen=screen
        self.object_dict={}
        GraphicalBase.container=self
        GraphicalBase.first=None
        self.updatedList=[]#The objects updated in an update cycle; is needed in order to not update the same object twice
    def resize(self,width:int,height:int) -> None:
        """A function which should be run when the video window is resized"""
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        #TODO: do all the other stuff which needs to be done on resize
    def draw(self) -> None:
        """Draws all the objects stored in the object_dict"""
        for keyname in self.object_dict:
            self.object_dict[keyname].draw()

#Graphical classes
class GraphicalBase():
    """The base which holds static variables for graphical objects"""
    def __init__(self) -> None:
        self.container=None
        self.first=None

class GraphicalObject():
    """Base of all graphical objects; holds its static variables in GraphicalBase"""
    def __init__(self,name:str,pos_pointers,size_pointers) -> None:
        GraphicalBase.container.object_dict[name]=self
        #TODO: should add a random name specifier; should prob use a static variable
        self._x=None
        self._y=None
        self._xSize=None
        self._ySize=None
        self.pointedBy=[]
        self.sizePointers=size_pointers
        self.posPointers=pos_pointers

        if self.posPointers[0]!=None:
            self.posPointers[0].initialize(self)
        if self.posPointers[1]!=None:
            self.posPointers[1].initialize(self)

        if self.sizePointers[0]!=None:#Initialization in order to fill the pointedBy list
            self.sizePointers[0].initialize(self)
        if self.sizePointers[1]!=None:
            self.sizePointers[1].initialize(self)

    def draw(self):
        """This is where the drawing action should be"""
        pass

    def beginUpdate(self):
        print(GraphicalBase.first)
        if GraphicalBase.first==None:
            GraphicalBase.first=self
            GraphicalBase.container.updatedList=[]
            self.update()
            GraphicalBase.first=None

    def update(self):
        """This function is called when a graphical parameter which can have influence on other objects is called"""
        if self not in GraphicalBase.container.updatedList:
            GraphicalBase.container.updatedList.append(self)#It's important to have this at the beginning so that the class is not updated after this
            if self.posPointers[0]!=None:#x pos
                self.x=self.posPointers[0].getValue()
            if self.posPointers[1]!=None:#y pos
                self.y=self.posPointers[1].getValue()
            if self.sizePointers[0]!=None:#x size
                self.ySize=self.sizePointers[0].getValue()
            if self.sizePointers[1]!=None:#y size
                self.ySize=self.sizePointers[1].getValue()
            for elements in self.pointedBy:
                elements.update()

class GraphicalRectangle(GraphicalObject):
    def __init__(self, name: str, rect:pygame.Rect,color=(0,0,0),pos_pointers=(None,None),size_pointers=(None,None),init_update=True) -> None:
        super().__init__(name,pos_pointers,size_pointers)
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
    def x(self,value):
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
    def __init__(self, name: str, image:pygame.Surface,coords=(0,0),pos_pointers=(None,None),size_pointers=(None,None),init_update=True) -> None:#TODO: add a way to handle size
        super().__init__(name,pos_pointers,size_pointers)
        self._image=image
        self._coords=coords#TODO: add a way to handle coords

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
        print("sas")
        self._coords=(self._coords[0],value)
        self.beginUpdate()
    @property
    def xSize(self):
        return self._image.get_width
    @xSize.setter
    def xSize(self,value):
        self._xSize=value
        #TODO: for object is self.sizePointed: object.update()
    @property
    def ySize(self):
        return self._image.get_height

    def draw(self):
        GraphicalBase.container.screen.blit(self._image,self._coords)


#Pointers
class Pointer():
    """The base object for pointers"""
    def __init__(self,pointer) -> None:
        self.pointer=pointer
    def getValue(self):
        return self.pointer.getValue()
    def initialize(self,outer_object):
        pass

class IntPointer(Pointer):
    def __init__(self, value:int) -> None:
        self.value=value
    def getValue(self):
        return self.value

class VariablePointer(Pointer):
    """Returns the value of a variable in a given object; before the value is returned, the object is updated"""
    def __init__(self, object:GraphicalObject, variable:str) -> None:
        self.object=object
        self.variable=variable
    def getValue(self):
        self.object.update()#Updates the object in ordere to have correct values
        return getattr(self.object,self.variable)
    def initialize(self,outer_object):
        self.object.pointedBy.append(outer_object)