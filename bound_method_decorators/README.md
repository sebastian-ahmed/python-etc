# Summary
This sub-project provides a re-usable implementation for a generalized and configurable solution for bound-method decorators by way of an extensible decorator class [`BMDecorate`][1].

The following article discusses this particular sub-project: ["Decorating bound-methods in Python — a general and scalable solution"](https://sebastian-ahmed.medium.com/decorating-bound-methods-in-python-a-general-and-scalable-solution-b16579c3a469)

# Features and Usage
The basic usage is to *extend* [`BMDecorate`][1] to provide the desired decorator functionality and decorate bound methods as needed. The following decoration syntax is supported:

(Assume that `my_decorator` is a specialization of [`BMDecorate`][1])

```python
#... other class code

@my_decorator
def methodA(self,...):
    #...

@my_decorator(param1=...,param2=...)
def methodB(self,...)
    #...
```

## Extending BMDecorate
[`BMDecorate`][1] only requires the `exec_wrap()` method to be overridden (if no decorator parameters are required). This method gets a reference to the bound-method's instance (object) as well as the wrapped method. This allows any prologue or epilogue code to be added around the wrapped method call as well as manipulation of the calling arguments and return value. If decorator parameters are required, the `__init__()` method also needs to be overridden to capture the parameters


A template example of extending the class and overriding both the `exec_wrap()` and `__init__()` methods is as follows:
```python
class my_decorator(BMDecorate):

    def __init__(self,*args,param1=0,**kwargs):
    super().__init__(*args,**kwargs)
    self.param1 = param1

    def exec_wrap(self,func,instance,*args,**kwargs):
    # ... do things before the wrapped method call including operating
    # on the instance reference
    
    # Do the wrapped method call by calling into the base method
    # Note that here we can modify arguments
    ret_val = super().exec_wrap(func,instance,*args,**kwargs)

    # ... optionally modify the return value before returning it
    return ret_val
```

This allows any class to decorate its methods using either `@my_decorator` or `@my_decorator(param1=...)` formats

A full working example can be found in the provided reference [`test.py`][2]

[1]:./BMDecorate.py
[2]:./test.py
