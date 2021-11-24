An extension to Pygame I made to have full control of the code, and to converge all the frustration only to myself
# Container
A general container, which should be the first thing to be initialized. It controls all the actions regarding all graphical objects, including variable sorting and drawing.

It takes a `pygame.display` object as a variable in order to be initialized; this display will be the one on which everything will be displayed.

One of the first things in your code, after the import actions, should be
```python
import fpa.main as fpa

container = fpa.Container(pygame.display.set_mode((800,600),pygame.RESIZABLE))
```
In this way, every `GraphicalObject` created will be added to `container.object_dict`, with a tag of the GraphicalObject's name pointing at the object itself.

It can be later refered to using `GraphicalBase.container.object_dict` 

# Pointers
Pointers are REALLY important in order to use dyanmic variables. Here's how they work

- First of all, they are linked to an `Updatable` object through `updatable.upInit()`, which takes as argument a dictionary of variable-pointers, like this: `{"x":IntPointer(5),"y":IntPointer(6)}`; `upInit()` correctly indexes the variables, moving them to `updatable.pointedVarDict`; this is needed in order to remove the `None` pointers in order to save on performance.
- Then, when `updatable.initPointers()` is run (which should be just after `upInit()`), every Pointer runs its `pointer.initialize(Updatable)` method, with the `updatable` instance as argument
- When an `updatable` instance calls its `beginUpdate()` function, every pointer for that instance runs its `getValue()` function in order to correctly set its value for the corresponding variable (all correspondances are determined by the `updatable.pointedVarDict`)