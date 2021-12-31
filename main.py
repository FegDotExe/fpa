from posixpath import dirname
import pygame
from os import path,listdir

#TODO: add intermediate blitting
#https://stackoverflow.com/questions/46965968/is-there-a-faster-way-to-blit-many-images-on-pygame

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
    def __init__(self,screen:pygame.display,dirpath,resize_function) -> None:
        self.assets={} #A dictionary which holds all the assets
        assetPath=dirpath+"assets/textures"
        self.loadAssets(assetPath)

        self.screen=screen #The screen which is used to draw the objects
        GraphicalBase.decorations=Decorations() #A class which contains decoration functions
        self.object_dict={} #A dictionary which holds all the objects
        GraphicalBase.container=self #The container which is used throughout the program. MUST be initialized before any other object
        self.updatedList=[] #The objects updated in an update cycle; is needed in order to not update the same object twice
        self.windowPointedBy=[] #List of objects which point the window and will be updated on resize
        self.layers={} #Dict of all layers by which objects are drawn; references are to the objects' names, so that if they are replaced there should be no trouble; every layer is a list with an int by index
        self.resize_function=resize_function

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
        self.resize_function()
    def draw(self) -> None:
        """Draws all the objects stored in the object_dict"""
        """for keyname in self.object_dict:
            self.object_dict[keyname].draw()"""
        #FIXME: should reorder the keys in the dict and then use those, in order to save time
        for i in sorted(self.layers.keys()):
            for element in self.layers[i]:
                self.object_dict[element].draw()
        """i=0
        j=0
        while i<len(self.layers):
            if j in self.layers:
                for keyname in self.layers[j]:
                    self.object_dict[keyname].draw()
                i+=1
            j+=1"""

class Decorations():
    """A class which enables the use of custom properties, used to update graphical objects only when needed"""
    class DimensionalProperty():
        def __init__(self,fget,fset=None) -> None:
            self.fget=fget
            self.fset=fset
            self.functions={}
            self.previous=None
        def __get__(self,obj,objtype=None):
            return self.fget(obj)
        def __set__(self,obj,value):
            if self.previous!=value:
                self.previous=value
                self.fset(obj,value)
                for function in self.functions:
                    function(*self.functions[function])

        def setter(self,fset):
            return type(self)(self.fget,fset)

    def get_property_class(self,name):
        """Returns a property class"""
        if name not in type(self).__dict__:
            raise AttributeError("The property \"{}\" is not defined".format(name))
        return type(self).__dict__[name]

    def add_function(self,property_name,function,args=()):
        """Add a function which will be executed when the property is set"""
        property=self.get_property_class(property_name)
        property.functions[function]=args

    def add_property(self,name,fget=None,fset=None):
        """Add a property to the class. This function also creates a variable for the property, named '<name>_var', <name> being the name argument"""
        setattr(self,name+"_var",0)
        def internal_fget(self):
            return getattr(self,name+"_var")
        def internal_fset(self,value):
            setattr(self,name+"_var",value)
        
        out_fget=internal_fget if fget is None else fget
        out_fset=internal_fset if fset is None else fset
        
        setattr(type(self),name,Decorations.DimensionalProperty(out_fget,out_fset))

    def remove_function(self,property_name,function):
        """Remove a function from a property"""
        property=self.get_property_class(property_name)
        if function in property.functions:
            del property.functions[function]

    def remove_property(self,name):
        """Remove a property from the class"""
        delattr(self,name+"_var")
        delattr(type(self),name)

#Graphical classes
class GraphicalBase():
    """The base which holds static variables for graphical objects"""
    nameId=0
    container=Container
    decorations=Decorations
    def __init__(self) -> None:
        self.container=None

class GraphicalObject():
    """Base of all graphical objects; holds its static variables in GraphicalBase"""
    def __init__(self,pos_functions,size_functions,name:str="",layer=0,size_properties=[],clickable=False) -> None:
        """
        This function provides to correctly intialize a GraphicalObject so that it can later be easily used

        Variables:
        - name: the name given to the object, used to identify it from other functions. It currently must be specified.
        """
        if name=="":
            name=str(GraphicalBase.nameId)
            GraphicalBase.nameId+=1
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

        for element in size_properties:
            GraphicalBase.decorations.add_function(element,self.update_size)

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
    
    def update(self):
        """The function used to update the object from a graphical standpoint; updates both position and size; needs to be overwritten"""
        pass
    def update_size(self):
        pass

    def __str__(self):
        #FIXME: still uses old variables
        return "<'name':'"+self._name+"', 'pos':("+str(self.x)+","+str(self.y)+"), 'size':("+str(self.xSize)+","+str(self.ySize)+"), 'pos_functions':({posf1},{posf2}), 'size_functions':({sizef1},{sizef2})>".format(posf1=self.x_funct.__name__,posf2=self.y_funct.__name__,sizef1=self.xSize_funct.__name__,sizef2=self.ySize_funct.__name__)

    def __repr__(self) -> str:
        return self.__str__()

    #TODO: add framed movement

class GraphicalRectangle(GraphicalObject):
    #TODO: change implementation to use decorators
    def __init__(self, name: str="", rect=pygame.Rect((0,0),(100,100)),layer=0,color=(0,0,0),pos_functions=(None,None),size_functions=(None,None)) -> None:
        super().__init__(pos_functions,size_functions,layer=layer,name=name)
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
    def __init__(self, pos_functions=(None,None), size_functions=(None,None),size_properties=[], text_properties=[], font_properties=[], color_properties=[], alpha_properties=[], name: str="", text_function=lambda:"", font_path="", alpha_function=lambda:255, font_size_function=lambda:32, layer=0,color_function=lambda:(0,0,0), clickable=False) -> None:
        #Should look into this: https://stackoverflow.com/questions/50280553/adding-text-to-a-rectangle-that-can-be-resized-and-moved-on-pygame-without-addo
        super().__init__(pos_functions, size_functions, name=name, layer=layer, clickable=clickable,size_properties=size_properties)
        self.text_function=text_function
        self.font_function=font_size_function
        self._font_name=font_path
        self.font=None #A pygame font object. Is created and updated in update_font
        self.font_height=None #The height of the font; used to calculate the size of the text box

        self.changed_surface=False

        self.alpha_function=alpha_function
        self.color_function=color_function

        self.base_surfaces=[] #List of surfaces which are used to change the graphical properties
        self.surfaces=[] #List of the surfaces which are actually displayed

        for element in font_properties:
            GraphicalBase.decorations.add_function(element,self.update_font)
        for element in text_properties:
            GraphicalBase.decorations.add_function(element,self.update_text)
        for element in color_properties:
            GraphicalBase.decorations.add_function(element,self.update_color)
        for element in alpha_properties:
            GraphicalBase.decorations.add_function(element,self.update_alpha)

        self.update_font()
        #TODO: should probably add a first create surface as init

    @property
    def text(self):
        return self.text_function()
    @property
    def color(self):
        return self.color_function()
    @property
    def alpha(self):
        return self.alpha_function()

    def createSurface(self):
        """Creates the correct text surface for the given text"""
        self.base_surfaces=[]
        line_width=0
        line=[]
        space_width=self.font.size(" ")[0]

        for word in self.text.split():
            line_width+=self.font.size(word)[0]+space_width
            if line_width>self.xSize:
                self.base_surfaces.append(self.font.render(" ".join(line),True,self.color).convert_alpha())
                line=[]
                line_width=self.font.size(word)[0]+space_width
            line.append(word)
        self.base_surfaces.append(self.font.render(" ".join(line),True,self.color).convert_alpha())
        self.surfaces=self.base_surfaces.copy()
        self.update_alpha()

    def update_font(self):
        """Updates the font"""
        self.font=pygame.font.Font(self._font_name,self.font_function())
        self.font_height=self.font.get_linesize()
        self.changed_surface=True
    def update_text(self):
        """Updates the text contained in the object"""
        self.changed_surface=True
    def update_color(self):
        """Updates the color of the text"""
        self.changed_surface=True
    def update_size(self):
        """Updates the size of the text"""
        self.changed_surface=True
    def update_alpha(self):
        """Updates the alpha of the text"""
        for i in range (len(self.base_surfaces)):
            surface=self.base_surfaces[i].copy()
            surface.fill(self.color+(self.alpha,),None,pygame.BLEND_RGBA_MULT)
            self.surfaces[i]=surface

    def draw(self):
        if self.changed_surface:
            self.createSurface()
            self.changed_surface=False
        for y, surf in enumerate(self.surfaces):
            if y*self.font_height+self.font_height>self.ySize:
                break
            GraphicalBase.container.screen.blit(surf,(self.x,self.y+y*self.font_height))

class GraphicalSprite(GraphicalObject):
    def __init__(self, name="", image=[],size_properties=[],layer=0,alpha_function=lambda:255,pos_functions=(None,None),size_functions=(None,None)) -> None:
        super().__init__(pos_functions,size_functions,layer=layer,name=name,size_properties=size_properties)
        if len(image)>0:
            try:
                self._base_image=GraphicalBase.container.getAsset(image)#Stores the base image; is used in order to prevent messiness when rescaling
            except Exception as e:
                image=[]
        if len(image)==0:#Not an else so that it can be entered if load fails
            self._base_image=GraphicalBase.container.getAsset(["nullimage"])
        self._image=self._base_image

        self.alpha_function=alpha_function

        self.dimension_cache={}

        self.size=(self.xSize,self.ySize)

        self.update_size()

    def transform_image(self,xSize,ySize,alpha):
        self._image=pygame.transform.scale(self._base_image,(xSize,ySize))
        self._image.fill((255,255,255,alpha),None,pygame.BLEND_RGBA_MULT)

    #Properties
    @property
    def alpha(self):
        return self.alpha_function()

    def update_size(self):
        self.update()
    def update(self):
        self.transform_image(self.xSize,self.ySize,self.alpha)

    def draw(self):
        #TODO: add a size setter
        GraphicalBase.container.screen.blit(self._image,(self.x,self.y))

#Functions
def reference(objectName:str) -> GraphicalObject:
    """Returns the object with the name corresponding to objectName"""
    return GraphicalBase.container.object_dict[objectName]