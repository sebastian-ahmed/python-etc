# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import logging

class BMDecorate(object):
    '''
    BMDecorate is a descriptor protocol utility class which provides a general
    and extensible bound method-call decorator service for any class via a
    function decorator pattern. This means for example, that for any given class
    definition, methods which need to be decorated can be defined as follows:

    @my_decorator
    def a_method(self,...):
        ... 

    or with decorator parameters as follows

    @my_decorator(param1=value1, param2=value2 ...)
    def a_method(self,...):
        ... 

    my_decorator is a specialization of BMDecorate

    In order to add wrapping functionality for any registered method, BMDecorate should be
    derived allowing the exec_wrap() method to be overridden. The base implementation simply
    calls the wrapped method. Note that the called method object reference is supplied as
    "instance", so any calling object can be operated upon in the exec_wrap() method
 
    If a decorator with parameters/arguments is required this base __init__() method must
    also be overridden to capture the parameters during the decoration phase

    There is a 1:1 mapping of decorated methods and a corresponding BMDecorate object,
    i.e. there is a unique BMDecorate object per client method definition.
    
    '''
    
    # Implementation details:
    # ########################
    # BMDecorate decorators which are of the "simple" form (e.g. @my_decorator), utilize the
    # Python descriptor protocol:
    #     When a bound-method call is actually made for an object of a client-class, its unique
    #     BMDecorate descriptor object captures the calling instance reference and stores it in 
    #     the _instance attribute (during the __get__ phase of the call). This is immediately followed
    #     by the interpreter calling the __call__ method of the unique BMDecorate object which now
    #     not only has the previously registered un-bound function object reference (stored in attribute _func),
    #     but also has the bound method call client object reference allowing it to perform
    #     the bound-method call. Subsequent bound method-calls update the object reference and so
    #     the _instance attribute is very dynamic
    #
    # DMDecorate decorators which are of the parameterized form, do not use the descriptor protocol
    # because their declarations result in a call of the decorator object during the decorating 
    # phase which allows __call__() in these cases to return the callable at that time which ensures
    # that future calls of the callable reference are always bound to the caller's object reference 

    def __init__(self,*args,**kwargs):
        '''
        This base initializer method can be overridden if a decorator requires arguments.
        The general template for such an override of this method is as follows:

        def __init__(self,*args,param1=<default1>, param2=<default2>, ... ,**kwargs):
            super().__init__(*args,**kwargs) # Call this base initializer
            self._param1 = param1
            self._param2 = param2
            ...

        '''
        self._func_name = 'None' # holds function which is wrapped (defined in __call__)
        self._func = None
        if len(args)==1: # This represents the condition of a parameter-less call
            self._func = args[0]
            self._func_name = args[0].__name__
            logging.debug(f"Decorating function {self._func_name} as parameter-less decorator")

    @property
    def func_name(self)->str:
        return self._func_name


    def exec_wrap(self,func,instance,*args,**kwargs):
        '''
        Override this method to control how the registered bound-method call is called, e.g.
        by fixing arguments or otherwise. The general template for an override of this method
        is as follows:

        - Perform any prologue code, e.g. modifying/setting arguments passed in
        - Call this base method (possibly capturing the return value)
          ret_val = super().exec_wrap(func,instance,*args,**kwargs)
        - Optionally modify the return value before returning it

        '''
        return func(instance,*args,**kwargs)


    def __get__(self,instance,insttype=None):
        logging.debug(f"\nCalling __get__() on {self} with object instance {instance}")
        self._instance = instance # Used in subsequent __call__ invocation
        return self

    def __call__(self,*args,**kwargs):
        # Two cases must be handled here.
        # 1) In the case where we had no decorator parameters (e.g. @BMDecorate). In this case
        #    the __call__ method is invoked each time the decorated method is called in which case 
        #    this method ends up essentially being a delegated callable and thus must in turn
        #    called the previously decorated method
        # 2) In the case where we had decorator parameters (e.g. @BMDecorate(...)), the __call__ method
        #    is only called once during the decoration process (i.e. when the client class definition
        #    is being interpreted) and thus we must return a callable (function object) so that calls
        #    to the decorated method are effectively calls to this callable
        # Note that in either case, a call to this method is bound to this object, not to the object
        # which is calling this object, but in the second case below this is only called once to 
        # return a function object which ultimately is bound to the object which calls it
        if self._func: # Case #1 (called each time a method call is made)
            # Here we used the saved self._instance captured in __get__()
            logging.debug(f"Calling {self._func.__name__} as bound function on object {self._instance}")
            return self.exec_wrap(self._func,self._instance,*args,**kwargs)
        else: # Case 2 (called only during decoration process)
            func = args[0]
            logging.debug(f"Decorating {func.__name__} and returning callable back to {func.__name__}")
            self._func_name = func.__name__
            def wrapped_call(instance,*args,**kwargs):
                return self.exec_wrap(func,instance,*args,**kwargs)
            return wrapped_call
