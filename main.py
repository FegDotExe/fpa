from posixpath import dirname
from numpy import double
import pygame
from os import path,listdir
from bisect import insort
from time import time_ns

#https://stackoverflow.com/questions/46965968/is-there-a-faster-way-to-blit-many-images-on-pygame

class vars:
    debug=False
    debug_tools=False
    debug_stats=True

#TODO: add a way to get absolute (non-surfaced) coordinates of an object
#TODO: reorder the click dictionary
#TODO: add binary search to make things significantly faster
#TODO: add collision methods
#TODO: add pixel-perfect collision
#TODO: totally remove layer when no objects are in it
#TODO: make frame events depend on seconds instead of frames
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
    - layers: a dict which contains the name references of the objects, layer by layer; the layers with lower values are the ones which get drawn first, in other words, the layers with higher values are more likely to be visible
    - fps: the frames per second of the game
    - ups: the updates per second of the game"""
    def __init__(self,screen:pygame.display,dirpath,resize_function,fps=60,ups=30,update_function=lambda: 1, frame_function=None) -> None:
        self.FPS=fps
        self.UPS=ups
        self.update_frame=0 #Which frame is currently being run in order to update
        #self.max_update_frame=self.FPS/self.UPS #The maximum amount of frames that can be run before an update is called

        self.update_function=update_function #A function which should be called every UPS amount of times per second
        self.frame_function=frame_function #A function which should be called every frame

        self.frame_event_dict={"normal":[]} #A list which holds all the events which should be run every frame

        self.assets={} #A dictionary which holds all the assets
        self.dirpath=dirpath

        self.click_layers={"main":{}} #A dictionary which holds all the objects which can be clicked on, and which layer they are in

        self.frame_cache_dict={} #A dictionary which holds values of all functions which are run in a frame; is emptied every frame and is used to improve performance

        self.screen=screen #The screen which is used to draw the objects
        GraphicalBase.decorations=Decorations() #A class which contains decoration functions
        self.object_dict={} #A dictionary which holds all the objects
        GraphicalBase.container=self #The container which is used throughout the program. MUST be initialized before any other object
        self.updatedList=[] #The objects updated in an update cycle; is needed in order to not update the same object twice
        self.windowPointedBy=[] #List of objects which point the window and will be updated on resize
        self.layers={"main":{}} #Dict of all layers by which objects are drawn; references are to the objects' names, so that if they are replaced there should be no trouble; every layer is a list with an int by index

        self.resize_function=resize_function

        self.frame_draws=0

        #These variables down here are used to improve frame drawing intervals
        self.last_second=time_ns() #The time at which the last second started
        self.passed_frames=0 #How many frames have passed in the last second
        self.last_passed_frames=0 #How many frames have passed in the last second
        self.updates_in_second=0 #How many updates have been run in the last second
        self.time_event_dict={} #A dictionary which holds all the time events

        self.average_frame_list=[] #A list which holds the last 5 seconds' fps, in order to calculate the average
        self.AVERAGE_AMOUNT=100 #The seconds to consider while averaging
    
        self.last_frame=time_ns() #The time at which the last frame started
    #Properties
    @property
    def width(self) -> int:
        return self.screen.get_width()
    @property
    def height(self) -> int:
        return self.screen.get_height()

    #Asset loading
    def getImageAsset(self,assetDir:str) -> pygame.Surface:
        if assetDir not in self.assets:
            if path.isfile(self.dirpath+"/assets/textures/"+assetDir):
                value=pygame.image.load(self.dirpath+"/assets/textures/"+assetDir).convert_alpha()
                self.assets[assetDir]=value
                return value
            else:
                raise Exception("The image asset "+assetDir+" does not exist")
        else:
            return self.assets[assetDir]

    def update(self) -> None:
        """A function called every frame, which will be run UPS amount of times each second, if called every frame"""
        this_time=time_ns()-self.last_second
        while this_time-((1000000000/self.UPS)*self.updates_in_second)>=0:
            self.updates_in_second+=1
            self.update_function()
    def frame(self) -> None:
        """A function which should be called every frame"""
        #Temporary code to implment delta time
        new_time=time_ns()
        delta_time=new_time-self.last_frame
        self.last_frame=new_time
        print(delta_time)

        if self.frame_function!=None:
            self.frame_function()
        for frame_event in self.frame_event_dict["normal"]:
            frame_event.frame()
        for element in list(self.time_event_dict):
            self.time_event_dict[element].frame()
        for frame_event in list(self.frame_event_dict):
            if frame_event!="normal":
                self.frame_event_dict[frame_event].frame()

    def add_to_average(self,amount:int):
        """Add a value used to calculate fps average"""
        if amount==0:
            return
        if len(self.average_frame_list)>0:
            average=self.average_fps()
            if average>amount and average-10<amount:
                return
            elif average<amount and average+10>amount:
                return
        if len(self.average_frame_list)<self.AVERAGE_AMOUNT:
            self.average_frame_list.append(amount)
        else:
            self.average_frame_list=self.average_frame_list[1:]
            self.average_frame_list.append(amount)
    def average_fps(self) -> float:
        """Returns the average FPS of the last second"""
        if len(self.average_frame_list)==0:
            return 0
        return sum(self.average_frame_list)/len(self.average_frame_list)
    class frame_event():
        """A way to trigger an event which should be repeated a certain amount of times. It will not be overwritten by other events with the same name, if the name is specified"""
        def __init__(self,normal_function,final_function,dict_name="normal",frame_amount=None) -> None:
            self.frame_amount=frame_amount
            self.frame_id=0
            self.normal_function=normal_function
            self.final_function=final_function
            self.dict_name=dict_name
            if dict_name=="normal":
                GraphicalBase.container.frame_event_dict[dict_name].append(self) #Append this event to the list of events which should be run every frame
            else:
                if dict_name not in GraphicalBase.container.frame_event_dict:
                    GraphicalBase.container.frame_event_dict[dict_name]=self #Append this event to the list of events which should be run every frame
        def frame(self):
            """Make a frame pass for this frame event"""
            self.frame_id+=1
            if (self.frame_amount!=None and (self.frame_id>=self.frame_amount)) or (self.frame_amount==None and self.frame_id>=GraphicalBase.container.max_update_frame):
                self.final_function()
                if self.dict_name=="normal":
                    GraphicalBase.container.frame_event_dict[self.dict_name].remove(self)
                else:
                    GraphicalBase.container.frame_event_dict.pop(self.dict_name) #Remove this event from the list of events which should be run every frame
            else:
                self.normal_function()
    
    def click(self,x,y):
        """Used to verify a click event: returns all the objects which have been clicked on"""
        output=[]
        self.detect_clicked("main",output,x,y)
        return output
    def detect_clicked(self,key,output,x,y):
        """Returns the clicked object at given coordinates; also supports surface layering"""
        for layer in sorted(self.click_layers[key].keys(),reverse=True):
            for element in self.click_layers[key][layer]:
                element=reference(element)
                if x>=element.x and y>=element.y and x<=element.x+element.xSize and y<element.y+element.ySize: #Aka element has been clicked
                    if element._name in self.click_layers:
                        self.detect_clicked(element._name,output,x-element.x,y-element.y)
                    else:
                        output.append(element)
                    if element.stop_click:
                        return output

    def resize(self,width:int,height:int) -> None:
        """A function which should be run when the video window is resized"""
        self.screen=pygame.display.set_mode((width,height),pygame.RESIZABLE)
        self.resize_function()
    def draw(self) -> None:
        """A function which should be run every frame, which will draw all the objects"""
        self.sub_draw(self.layers["main"])
        self.frame_cache_dict={}
        if vars.debug:
            print(f"Drew {self.frame_draws} objects")
            input("Waiting.")
        self.frame_draws=0
    def sub_draw(self,layer_dict) -> None:
        """Used to correctly draw surfaces and subsurfaces so that every object appears correctly"""
        if vars.debug:
            print(f"Begin drawing layer: {layer_dict}")
        for layer in list(layer_dict.keys()): #There is no need to sort, as the dictionary is already sorted
            layer_list=layer_dict[layer].copy()
            for element in layer_list:
                if element in self.layers:
                    #if binary_search_bool(list(self.layers.keys()),element): #If the element is a surface
                    #print(reference(element).updated_values)
                    self.sub_draw(reference(element).updated_values)
                    self.object_dict[element].draw()
                    self.frame_draws+=1
                else:
                    if vars.debug:
                        print(f"Drawing element: {element}",end="; ")
                    self.object_dict[element].draw()
                    self.frame_draws+=1

    def step(self):
        """Performs all the action which are supposed to be performed every game cycle"""
        """if time_ns()-1000000000>=self.last_second:
            #print(f"A second has passed with {self.passed_frames} frames")
            self.last_second=time_ns()
            if len(self.average_frame_list)<self.AVERAGE_AMOUNT:
                self.average_frame_list.append(self.passed_frames)
            else:
                self.average_frame_list=self.average_frame_list[1:]
                self.average_frame_list.append(self.passed_frames)
            self.passed_frames=0"""
        if time_ns()-1000000000>=self.last_second: #This means that a second has passed
            self.last_second=time_ns()
            self.updates_in_second=0
        self.update()
        self.frame()
        self.draw()
        #self.passed_frames+=1

    #Decorators
    def frame_cache(self,funct):
        """A decorator which caches the return value of a function, so that it is only run once per frame"""
        def internal(*args,**kwargs):
            if funct.__name__ not in self.frame_cache_dict:
                self.frame_cache_dict[funct.__name__]=funct(*args,**kwargs)
            return self.frame_cache_dict[funct.__name__]
        return internal

    #Classes
    #http://www.pygame.org/wiki/ConstantGameSpeed?parent=CookBook
    class time_event():
        """An event which has a certain duration expressed in time"""
        def __init__(self,seconds:float, name:str, normal_function:callable=lambda x:0, final_function:callable=lambda x:0) -> None:
            if name in GraphicalBase.container.time_event_dict:
                return
            self.seconds=seconds
            self.nanoseconds=seconds*1000000000
            self.start=time_ns()
            self.name=name
            self.normal_function=normal_function
            self.final_function=final_function
            self.expected_last_step=1-(1/(GraphicalBase.container.FPS/GraphicalBase.container.UPS)) #This number is the step which is supposed to be the last one. It is used to make even really low fps, like 30 fps, relatively smooth
            GraphicalBase.container.time_event_dict[name]=self
        def frame(self) -> None:
            #step=((time_ns()-self.start)/self.nanoseconds)/self.seconds
            if self.nanoseconds==0:
                step=1
            else:
                step=((time_ns()-self.start))/self.nanoseconds
            #print(f"Time event {self.name} is at {step}")
            #if step<self.expected_last_step:
            if step<1:
                self.normal_function(step)
            else:
                #print("End")
                self.final_function(step)
                GraphicalBase.container.time_event_dict.pop(self.name)

    #Properties
    @property
    def max_update_frame(self) -> int:
        """Returns the maximum amount of frames which should be updated per second"""
        if self.average_fps()==0:
            return self.FPS/self.UPS
        return int(self.average_fps()/self.UPS)

class Decorations():
    """A class which enables the use of custom properties, used to update graphical objects only when needed"""
    class DimensionalProperty():
        def __init__(self,fget,fset=None,cache=True) -> None:
            self.fget=fget
            self.fset=fset
            self.functions={}
            self.previous=None
            self.cache=cache
        def __get__(self,obj,objtype=None):
            return self.fget(obj)
        def __set__(self,obj,value):
            if (self.cache and self.previous!=value) or not self.cache:
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

    def add_property(self,name,fget=None,fset=None,cache=True):
        """Add a property to the class. This function also creates a variable for the property, named '<name>_var', <name> being the name argument"""
        setattr(self,name+"_var",0)
        def internal_fget(self):
            return getattr(self,name+"_var")
        def internal_fset(self,value):
            setattr(self,name+"_var",value)
        
        out_fget=internal_fget if fget is None else fget
        out_fset=internal_fset if fset is None else fset
        
        setattr(type(self),name,Decorations.DimensionalProperty(out_fget,out_fset,cache=cache))

    def remove_function(self,property_name,function):
        """Remove a function from a property"""
        property=self.get_property_class(property_name)
        if function in property.functions:
            del property.functions[function]

    def remove_property(self,name):
        """Remove a property from the class"""
        delattr(self,name+"_var")
        delattr(type(self),name)

#Key handling
class KeyHandler():
    """
    Description
    -
    A class which handles key presses

    Write methods
    -
    - down(key) is used to signal that a key is down
    - up(key) is used to signal that a key is up
    - held(key) is used to signal that a key is held
    - remove(key) is used to remove a key from the list of keys: down, up, held

    Read methods
    -
    - is_down(key) is used to check if a key is down
    - is_up(key) is used to check if a key is up
    - is_held(key) is used to check if a key is held
    """
    keys={"down":set(),"up":set(),"held":set()}
    def down(key):
        """Tells the keyhandler that a key is down"""
        KeyHandler.keys["down"].add(key)
    def up(key):
        """Tells the keyhandler that a key is up"""
        KeyHandler.keys["up"].add(key)
    def held(key):
        """Tells the keyhandler that a key is held"""
        KeyHandler.keys["held"].add(key)
    def remove(key):
        """Removes a key from every set"""
        KeyHandler.keys["down"].discard(key)
        KeyHandler.keys["up"].discard(key)
        KeyHandler.keys["held"].discard(key)

    def is_down(key):
        """Returns true if the key is down"""
        return key in KeyHandler.keys["down"]
    def is_up(key):
        """Returns true if the key is up"""
        return key in KeyHandler.keys["up"]
    def is_held(key):
        """Returns true if the key is held"""
        return key in KeyHandler.keys["held"]
    D=100
    S=115
    A=97
    W=119
    Z=122

class MouseHandler():
    buttons={"down":{},"up":{},"held":{}}
    def down(button,x,y):
        MouseHandler.buttons["down"][button]=[x,y]
    def up(button):
        MouseHandler.buttons["down"].pop(button,None)
        MouseHandler.buttons["up"].pop(button,None)
    def hold(button):
        """Tells that the click should be considered held"""
        MouseHandler.buttons["held"][button]=MouseHandler.buttons["new"][button]
        MouseHandler.buttons["down"].pop(button,None)
    def remove(button):
        """Removes the click"""
        MouseHandler.buttons["down"].pop(button,None)
        MouseHandler.buttons["up"].pop(button,None)
        MouseHandler.buttons["held"].pop(button,None)

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
    def __init__(self,pos_functions,size_functions,name:str="",layer=0,pos_properties=[],size_properties=[],clickable=False,stop_click=False,click_layer=None,blit_surface=None) -> None:
        """
        This function provides to correctly intialize a GraphicalObject so that it can later be easily used

        Variables:
        - name: the name given to the object, used to identify it from other functions. It currently must be specified.
        """
        if name=="":
            name=str(GraphicalBase.nameId)
            GraphicalBase.nameId+=1
        GraphicalBase.container.object_dict[name]=self #Adds the object to the container's object_dict
        self._name=name

        if type(blit_surface)==str:
            self.blit_surface=reference(blit_surface)
        else:
            self.blit_surface=blit_surface

        self.layer=layer

        self._x=0
        self._y=0
        self._xSize=0
        self._ySize=0

        self.base_x=0
        self.base_y=0
        self.base_xSize=0
        self.base_ySize=0

        if pos_functions[0] is not None and not callable(pos_functions[0]):
            pos_functions=(lambda value=pos_functions[0]:value, pos_functions[1])
        if pos_functions[1] is not None and not callable(pos_functions[1]):
            pos_functions=(pos_functions[0],lambda value=pos_functions[1]:value)

        #TODO: something like this with size functions

        self.x_funct=pos_functions[0] if pos_functions[0]!=None else lambda:self._x
        self.y_funct=pos_functions[1] if pos_functions[1]!=None else lambda:self._y
        self.xSize_funct=size_functions[0] if size_functions[0]!=None else lambda:self._xSize
        self.ySize_funct=size_functions[1] if size_functions[1]!=None else lambda:self._ySize

        self.updated() #Tells if the object has been updated since the last time it was drawn

        for element in size_properties:
            GraphicalBase.decorations.add_function(element,self.update_size)
        for element in pos_properties:
            GraphicalBase.decorations.add_function(element,self.update_pos)

        self.dimension_cache={}

        #Adds in right layer
        if self.blit_surface is None:
            if layer not in GraphicalBase.container.layers["main"]:
                GraphicalBase.container.layers["main"][layer]=[]
                GraphicalBase.container.layers["main"]=sort_dict(GraphicalBase.container.layers["main"])
            if self not in GraphicalBase.container.layers["main"][layer]:
                GraphicalBase.container.layers["main"][layer].append(self._name)
        else:
            if self.blit_surface._name not in GraphicalBase.container.layers:
                GraphicalBase.container.layers[self.blit_surface._name]={}
                GraphicalBase.container.layers=sort_dict(GraphicalBase.container.layers)
            if layer not in GraphicalBase.container.layers[self.blit_surface._name]:
                GraphicalBase.container.layers[self.blit_surface._name][layer]=[]
            if self not in GraphicalBase.container.layers[self.blit_surface._name][layer]:
                GraphicalBase.container.layers[self.blit_surface._name][layer].append(self._name)

        #Click interaction
        self.clickable=clickable
        self.stop_click=stop_click
        self.click_layer=click_layer
        if self.clickable:
            temp_layer=self.click_layer if self.click_layer!=None else layer

            if self.blit_surface is None:
                if temp_layer not in GraphicalBase.container.click_layers["main"]:
                    GraphicalBase.container.click_layers["main"][temp_layer]=[]
                GraphicalBase.container.click_layers["main"][temp_layer].append(self._name)
            else:
                if self.blit_surface._name not in GraphicalBase.container.click_layers:
                    GraphicalBase.container.click_layers[self.blit_surface._name]={}
                if temp_layer not in GraphicalBase.container.click_layers[self.blit_surface._name]:
                    GraphicalBase.container.click_layers[self.blit_surface._name][temp_layer]=[]
                if self._name not in GraphicalBase.container.click_layers[self.blit_surface._name][temp_layer]:
                    GraphicalBase.container.click_layers[self.blit_surface._name][temp_layer].append(self._name)

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
        """The x position of the object"""
        return self.x_funct()
    @x.setter
    def x(self,value):
        self._x=value
    @property
    def y(self):
        """The y position of the object"""
        return self.y_funct()
    @y.setter
    def y(self,value):
        self._y=value
    @property
    def xSize(self):
        """The x size of the object"""
        return self.xSize_funct()
    @xSize.setter
    def xSize(self,value):
        self._xSize=value
    @property
    def ySize(self):
        """The y size of the object"""
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
    def update_pos(self):
        pass

    def __str__(self):
        return "<'name':'"+self._name+"', 'pos':("+str(self.x)+","+str(self.y)+"), 'size':("+str(self.xSize)+","+str(self.ySize)+"), 'pos_functions':({posf1},{posf2}), 'size_functions':({sizef1},{sizef2})>".format(posf1=self.x_funct.__name__,posf2=self.y_funct.__name__,sizef1=self.xSize_funct.__name__,sizef2=self.ySize_funct.__name__)

    def __repr__(self) -> str:
        return self.__str__()

    def updated(self):
        """Is used to signal that something is changed graphically and that the draw function should be called next frame"""
        if self.blit_surface is not None:
            #print("Updated "+self._name+" on "+self.blit_surface._name)
            if self.layer not in self.blit_surface.updated_values:
                self.blit_surface.updated_values[self.layer]=[]
            if self._name not in self.blit_surface.updated_values[self.layer]:
                self.blit_surface.updated_values[self.layer].append(self._name)


class GraphicalRectangle(GraphicalObject):
    def __init__(self, name: str="", rect=pygame.Rect((0,0),(100,100)),layer=0,color=(0,0,0),pos_functions=(None,None),size_functions=(None,None),size_properties=[],pos_properties=[]) -> None:
        #print(pos_properties)
        super().__init__(pos_functions,size_functions,layer=layer,name=name,size_properties=size_properties,pos_properties=pos_properties)
        self._rect=rect
        self._color=color

        self.update_pos()
        self.update_size()

    def update_pos(self):
        self._rect.left=self.x
        self._rect.top=self.y
    def update_size(self):
        self._rect.width=self.xSize
        self._rect.height=self.ySize
    
    def draw(self):
        pygame.draw.rect(surface=GraphicalBase.container.screen,color=self._color,rect=self._rect)

class GraphicalText(GraphicalObject):
    """A quick and easy way to display text"""
    def __init__(self, pos_functions=(None,None), size_functions=(None,None),size_properties=[], text_properties=[], font_properties=[], color_properties=[], alpha_properties=[], name: str="", text_function=lambda:"", font_path="", alpha_function=lambda:255, font_size_function=lambda:32, layer=0,color_function=lambda:(0,0,0), clickable=False,stop_click=False, click_layer=None ,blit_surface=None) -> None:
        #Should look into this: https://stackoverflow.com/questions/50280553/adding-text-to-a-rectangle-that-can-be-resized-and-moved-on-pygame-without-addo
        super().__init__(pos_functions, size_functions, name=name, layer=layer, clickable=clickable,size_properties=size_properties,blit_surface=blit_surface,stop_click=stop_click,click_layer=click_layer)
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
        self.updated=True

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
            surface.set_alpha(self.alpha)
            self.surfaces[i]=surface
        self.updated=True

    def draw(self):
        if self.changed_surface:
            self.createSurface()
            self.changed_surface=False
        for y, surf in enumerate(self.surfaces):
            if y*self.font_height+self.font_height>self.ySize:
                break
            if self.blit_surface is None:
                GraphicalBase.container.screen.blit(surf,(self.x,self.y+y*self.font_height))
            else:
                if self.updated:
                    self.blit_surface.surface.blit(surf,(self.x,self.y+y*self.font_height))
                    self.updated=False

class GraphicalSprite(GraphicalObject):
    def __init__(self, name="", image="",size_properties=[],layer=0,alpha_function=lambda:255,pos_functions=(None,None),size_functions=(None,None),blit_surface=None,clickable=False,stop_click=False,click_layer=None) -> None:
        super().__init__(pos_functions,size_functions,layer=layer,name=name,size_properties=size_properties,blit_surface=blit_surface,clickable=clickable,stop_click=stop_click,click_layer=click_layer)
        if len(image)>0:
            try:
                self._base_image=GraphicalBase.container.getImageAsset(image)#Stores the base image; is used in order to prevent messiness when rescaling
            except Exception as e:
                image=""
        if len(image)==0:#Not an else so that it can be entered if load fails
            self._base_image=GraphicalBase.container.getImageAsset("nullimage.png")
        self._image=self._base_image

        self.alpha_function=alpha_function

        self.dimension_cache={}

        self.size=(self.xSize,self.ySize)

        self.update_size()

    def transform_image(self,xSize,ySize,alpha):
        self._image=pygame.transform.scale(self._base_image,(xSize,ySize))
        self._image.fill((255,255,255,alpha),None,pygame.BLEND_RGBA_MULT)
        self.updated()

    #Properties
    @property
    def alpha(self):
        return self.alpha_function()

    def update_size(self):
        self.update()
    def update(self):
        self.transform_image(self.xSize,self.ySize,self.alpha)

    def draw(self):
        if self.blit_surface is None:
            GraphicalBase.container.screen.blit(self._image,(self.x,self.y))
        else:
            if vars.debug:
                pass
                #print(f"Drawing {self._name}")
            self.blit_surface.surface.blit(self._image,(self.x,self.y))
            self.blit_surface.updated_values[self.layer].remove(self._name)
            if len(self.blit_surface.updated_values[self.layer])==0:
                self.blit_surface.updated_values.pop(self.layer)
        #GraphicalBase.container.screen.blit(self._image,(self.x,self.y))

class GraphicalSurface(GraphicalObject):
    def __init__(self, pos_functions=(), size_functions=(), name: str = "", layer=0, size_properties=[], alpha_function=lambda:255, alpha_properties=[], clickable=False, stop_click=False, click_layer=None,blit_surface=None) -> None:
        super().__init__(pos_functions, size_functions, name=name, layer=layer, size_properties=size_properties, clickable=clickable, stop_click=stop_click, click_layer=click_layer,blit_surface=blit_surface)
        self.alpha_function=alpha_function
        for element in alpha_properties:
            GraphicalBase.decorations.add_function(element,self.update_alpha)
        self.surface=pygame.Surface((self.xSize,self.ySize),pygame.SRCALPHA,32) #Don't know ab those last two args

        self.updated_values={}

    @property
    def alpha(self):
        return self.alpha_function()

    def update_alpha(self):
        self.surface.set_alpha(self.alpha)
        self.updated=True
    def update_size(self):
        self.surface=pygame.Surface((self.xSize,self.ySize),pygame.SRCALPHA,32)
        self.updated=True
    def draw(self):
        if self.blit_surface is None:
            GraphicalBase.container.screen.blit(self.surface,(self.x,self.y))
        else:
            if self.updated:
                self.blit_surface.surface.blit(self.surface,(self.x,self.y))
                self.updated=False

#Functions
def reference(objectName:str) -> GraphicalObject:
    """Returns the object with the name corresponding to objectName"""
    return GraphicalBase.container.object_dict[objectName]
def sort_dict(dictionary:dict) -> dict:
    """Sorts a dictionary by its keys and returns it as a new dictionary"""
    sorted_keys=sorted(dictionary.keys())
    new_dict={}
    for key in sorted_keys:
        new_dict[key]=dictionary[key]
    return new_dict

def binary_search(list:list,value,low:int=None,high:int=None):
    """Returns the index of the value in the list, or -1 if it is not in the list"""
    if low is None:
        low=0
    if high is None:
        high=len(list)-1

    if low>high:
        return -1
    mid=(low+high)//2
    if list[mid]==value:
        return mid
    elif list[mid]>value:
        return binary_search(list,value,low,mid-1)
    else:
        return binary_search(list,value,mid+1,high)
def binary_search_bool(list:list,value):
    """Returns whether the value is in the list or not"""
    return binary_search(list,value)>-1