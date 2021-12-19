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
    - layers: a dict which contains the name references of the objects, layer by layer; the layers with lower values are the ones which get drawn first, in other words, the layers with higher values are more likely to be visible"""
    def __init__(self,screen:pygame.display,dirpath) -> None:
        self.assets={} #A dictionary which holds all the assets
        assetPath=dirpath+"assets/textures"
        self.loadAssets(assetPath)

        self.screen=screen #The screen which is used to draw the objects
        self.object_dict={} #A dictionary which holds all the objects
        GraphicalBase.container=self #The container which is used throughout the program. MUST be initialized before any other object
        self.updatedList=[] #The objects updated in an update cycle; is needed in order to not update the same object twice
        self.windowPointedBy=[] #List of objects which point the window and will be updated on resize
        self.layers={} #Dict of all layers by which objects are drawn; references are to the objects' names, so that if they are replaced there should be no trouble; every layer is a list with an int by index
    
    #Properties
    @property
    def width(self) -> int:
        return self.screen.get_width()
    @property
    def height(self) -> int:
        return self.screen.get_height()

    #Asset loading
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
    def draw(self) -> None:
        """Draws all the objects stored in the object_dict"""
        """for keyname in self.object_dict:
            self.object_dict[keyname].draw()"""
        #FIXME: should reorder the keys in the dict and then use those, in order to save time
        i=0
        j=0
        while i<len(self.layers):
            if j in self.layers:
                for keyname in self.layers[j]:
                    self.object_dict[keyname].draw()
                i+=1
            j+=1


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

        self.x_funct=pos_functions[0] if pos_functions[0]!=None else lambda:self._x
        self.y_funct=pos_functions[1] if pos_functions[1]!=None else lambda:self._y
        self.xSize_funct=size_functions[0] if size_functions[0]!=None else lambda:self._xSize
        self.ySize_funct=size_functions[1] if size_functions[1]!=None else lambda:self._ySize

        self.dimension_cache={}

        #Adds in right layer
        if layer not in GraphicalBase.container.layers:
            GraphicalBase.container.layers[layer]=[]
        if self not in GraphicalBase.container.layers[layer]:
            GraphicalBase.container.layers[layer].append(self._name)

    def dimensionalProperty(self,func,change_func):
        """A decorator for dimensional properties, such as xSize and ySize.
        
        Variables:
        - func: the function that is used to get the value of the property
        - change_func: the function used to change pylib's wrapped object's value. Takes the result of func as an argument"""
        def wrapper(*args,**kwargs):
            changed=False
            value=func(*args,**kwargs)
            if func not in self.dimension_cache:
                self.dimension_cache[func]=value
                changed=True
            else:
                if self.dimension_cache[func]!=value:
                    self.dimension_cache[func]=value
                    changed=True
            if changed:
                change_func(value)
            return self.dimension_cache[func]
        return wrapper

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
        return "<'name':'"+self._name+"', 'pos':("+str(self.x)+","+str(self.y)+"), 'size':("+str(self.xSize)+","+str(self.ySize)+"), 'pos_functions':({posf1},{posf2}), 'size_functions':({sizef1},{sizef2})>".format(posf1=self.x_funct.__name__,posf2=self.y_funct.__name__,sizef1=self.xSize_funct.__name__,sizef2=self.ySize_funct.__name__)

    def __repr__(self) -> str:
        return self.__str__()

    #TODO: add framed movement

class GraphicalRectangle(GraphicalObject):
    def __init__(self, name: str, rect=pygame.Rect((0,0),(100,100)),layer=0,color=(0,0,0),pos_functions=(None,None),size_functions=(None,None)) -> None:
        super().__init__(name,pos_functions,size_functions,layer=layer)
        self._rect=rect
        self._color=color
        self.dimension_cache={}

    @property
    def x(self):
        def change_rect(x):
            self._rect.left=x
        return self.dimensionalProperty(self.x_funct,change_rect)()
    @property
    def y(self):
        def change_rect(y):
            self._rect.top=y
        return self.dimensionalProperty(self.y_funct,change_rect)()
    @property
    def xSize(self):
        def change_rect(xSize):
            self._rect.width=xSize
        return self.dimensionalProperty(self.xSize_funct,change_rect)()
    @property
    def ySize(self):
        def change_rect(ySize):
            self._rect.height=ySize
        return self.dimensionalProperty(self.ySize_funct,change_rect)()
    
    def draw(self):
        variables=(self.x,self.y,self.xSize,self.ySize) #Used to update variables
        pygame.draw.rect(surface=GraphicalBase.container.screen,color=self._color,rect=self._rect)

class GraphicalText(GraphicalObject):
    """A quick and easy way to display text"""
    def __init__(self, name: str, pos_pointers, size_pointers, text="", font="", fontSizeFunct=None, layer=0, clickable=False) -> None:
        #Should look into this: https://stackoverflow.com/questions/50280553/adding-text-to-a-rectangle-that-can-be-resized-and-moved-on-pygame-without-addo
        super().__init__(name, pos_pointers, size_pointers, layer=layer, clickable=clickable)
        self._text=text
        self._font=font
        self.font_function=fontSizeFunct

        self.surfaces=[]
        self.createSurface()

    @property
    def font(self):
        return pygame.font.Font(self._font,self.font_function())#TODO: add cache for this, maybe make a separate function in order to make this better

    def createSurface(self):
        """Creates the correct text surface for the given text"""
        self.surfaces=[]
        line_width=0
        line=[]
        space_width=self.font.size(" ")[0]

        for word in self._text.split(" "):
            line_width+=self.font.size(word)[0]+space_width
            if line_width>self.xSize:
                self.surfaces.append(self.font.render(" ".join(line),True,(0,0,0)))#TODO: add a way to change color
                line=[]
                line_width=self.font.size(word)[0]+space_width
            line.append(word)
        self.surfaces.append(self.font.render(" ".join(line),True,(0,0,0)))#TODO: add a way to change color

    def draw(self):
        for y, surf in enumerate(self.surfaces):
            if y*self.font.get_linesize()+self.font.get_linesize()>self.ySize:
                break
            GraphicalBase.container.screen.blit(surf,(self.x,self.y+y*self.font.get_linesize()))


class GraphicalSprite(GraphicalObject):
    def __init__(self, name: str, image=[],layer=0,pos_functions=(None,None),size_functions=(None,None)) -> None:
        super().__init__(name,pos_functions,size_functions,layer=layer)
        if len(image)>0:
            try:
                self._base_image=GraphicalBase.container.getAsset(image)#Stores the base image; is used in order to prevent messiness when rescaling
            except Exception as e:
                image=[]
        if len(image)==0:#Not an else so that it can be entered if load fails
            self._base_image=GraphicalBase.container.getAsset(["nullimage"])
        self._image=self._base_image

        self.dimension_cache={}

        self.size=(self.xSize,self.ySize)

    #Properties
    @property
    def xSize(self):
        def change_image(xSize):
            self._image=pygame.transform.scale(self._base_image,(xSize,self.ySize))
        value=self.dimensionalProperty(self.xSize_funct,change_image)()
        return value
    @property
    def ySize(self):
        def change_image(ySize):
            self._image=pygame.transform.scale(self._base_image,(self.xSize,ySize))
        value=self.dimensionalProperty(self.ySize_funct,change_image)()
        return value

    def draw(self):
        #TODO: add a size setter
        self.size=(self.xSize,self.ySize)
        GraphicalBase.container.screen.blit(self._image,(self.x,self.y))

#Functions
def reference(objectName:str) -> GraphicalObject:
    """Returns the object with the name corresponding to objectName"""
    return GraphicalBase.container.object_dict[objectName]