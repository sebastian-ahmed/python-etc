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

    In order to add wrapping funtionality for any registered method, BMDecorate should be
    derived allowing the prologue(), execute() and epilogue() methods to be overriden.
    Default versions of these methods perform no action other than to call the decorated method
    on the calling object's instance. The structure of any BMDecorate based decorator has the
    following 3 call phases

    1) prologue is executed (with a bound object reference)
    2) The wrapped bound-method is executed
    3) epilogue is executed (with a bound object reference)

    Since prologue and epilogue each get the bound method call instance reference, the bound
    object may be operated upon in the wrapper functions. The middle execution phase may
    be overriden to control the wrapped function call in any way including altering the
    calling arguments.

 
    There is a 1:1 mapping of decorated methods and a corresponding BMDecorate object,
    i.e. there is a unique BMDecorate object per client method definition.
    
    '''
    
    # Implementation details:
    # ########################
    # BMDecorate decorators which are of the "simple" form (e.g. @my_decorator), utilize the
    # Python descriptor protocol:
    #     When a bound-method call is actually made for an object of a client-class, its unique
    #     BMDecorate descriptor object captures the calling instance reference and stores it in 
    #     the obj attribute (during the __get__ phase of the call). This is immediately followed
    #     by calling the __call__ method of the unique BMDecorate object which now not only has
    #     the previously registered un-bound function object reference (stored in attribute func),
    #     but also has the bound method call client object reference allowing it to perform
    #     the bound-method call. Subsequent bound method-calls update the object reference and so
    #     the obj attribute is very dynamic
    #
    # DMDecorate decorators which are of the parameterized form, do not use the descriptor protocol
    # because their declarations result in a call of the decorator object during the decorating 
    # phase which allows __call__() in these cases to return the callable at that time which ensures
    # that future calls of the callable reference are always bound to the caller's object reference 

    def __init__(self,*args):
        self._func_name = 'None' # holds function which is wrapped (defined in __call__)
        self._func = None
        if len(args)==1: # This represents the condition of a parameter-less call
            self._func = args[0]
            self._func_name = args[0].__name__
            logging.info(f"Decorating function {self._func_name} as parameter-less decorator")

    @property
    def func_name(self)->str:
        return self._func_name

    def prologue(self,instance):
        '''
        Override this method to perform instance-level decorator operations before the wrapped
        bound method call is made
        '''
        pass

    def execute(self,func,instance,*args,**kwargs):
        '''
        Override this method to control how the registered bound-method call is called, e.g.
        by fixing arguments or otherwise
        '''
        return func(instance,*args,**kwargs)

    def epilogue(self,instance,*args,**kwargs):
        '''
        Override this method to perform instance-level decorator operations after the wrapped
        bound method call is made
        '''
        pass

    def __get__(self,instance,insttype=None):
        logging.info(f"\nCalling __get__() on {self} with object instance {instance}")
        self._instance = instance # Used in subsequent __call__ invocation
        return self

    def __call__(self,*args,**kwargs):
        # Two cases must be handled here.
        # 1) In the case where we had decorator parameters (e.g. @BMDecorate(...)), the __call__ method
        #    is only called once during the decoration process and thus we must return a callable
        #    so that calls can be made to the callable
        # 2) In the case where we had no decorator parameters (e.g. @BMDecorate), the __call__ method is
        #    invoked each time the wrapped function is called in which case this method ends up 
        #    being a delegate caller (i.e. only returns the return value of the underlying wrapped
        #    function call).
        # Note that in either case, a call to this method is bound to this object, not to the object
        # which is calling this object, but in the first case below this is only called once to 
        # return a function object which ultimately is bound to the object which calls it
        if self._func is None: # Case #1 (called only during decoration process)
            func = args[0]
            logging.info(f"Decorating {func.__name__} and returning callable back to {func.__name__}")
            self._func_name = func.__name__
            def wrapped_call(instance,*args,**kwargs):
                self.prologue(instance)
                ret_val = self.execute(func,instance,*args,**kwargs)
                self.epilogue(instance)
                return ret_val
            return wrapped_call
        else: # Case 2 (called each time a method call is made)
            # Here we used the saved self._instance intercepted in __get__()
            logging.info(f"Calling {self._func.__name__} as bound function on object {self._instance}")
            self.prologue(self._instance)
            ret_val = self.execute(self._func,self._instance,*args,**kwargs)
            self.epilogue(self._instance)
            return ret_val
