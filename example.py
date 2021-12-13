from functools import cache
class ExampleObject():
    def __init__(self,pos_funct:tuple) -> None:
        self.x_funct=pos_funct[0]
        self.y_funct=pos_funct[1]
    
    @property
    @cache#See if the cache is clearable
    def x(self) -> int:
        return self.x_funct()
    @property
    @cache
    def y(self) -> int:
        return self.y_funct()

window=10

updatable_cache={}

#A precious example of a cached function. Will add a way to add it to a cached list so that the cache can then be emptied.
def updatable(func,*args,**kwargs):
    """A decorator which adds cache capabilities to a function."""
    def wrapper(*args,**kwargs):
        key=func.__name__+str(args)+str(kwargs)
        if key not in updatable_cache:
            value=func(*args,**kwargs)
            updatable_cache[key]=value
        else:
            value=updatable_cache[key]
        return value
    return wrapper

@updatable
def exampleProportion():
    return window/2

#Updatable gives: 12586269025
#Cache gives: 12586269025

@updatable
def recursive_fibonacci(n):
    if n<=2:
        return 1
    return recursive_fibonacci(n-1)+recursive_fibonacci(n-2)

example=ExampleObject(pos_funct=(exampleProportion,lambda:20))

print(example.x)
print(example.y)

print(recursive_fibonacci(50))