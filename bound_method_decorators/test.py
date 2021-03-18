#!/usr/bin/env python3

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
logging.basicConfig(level=logging.DEBUG)

from BMDecorate import BMDecorate

class my_decorator(BMDecorate):
    '''
    Example specialization of a BMDecorate bound-method decorator where
    we specialize __init__ and exec_wrap. We modify an incoming argument in 
    cases where it exists (arg1) and we also modify the return value if it
    exists
    '''

    def __init__(self,*args,custom_msg='',**kwargs):
        super().__init__(*args,**kwargs)
        logging.debug(f"Custom decorator argument custom_msg={custom_msg} for wrapped function")
        self.custom_msg = custom_msg

    def exec_wrap(self,func,instance,*args,**kwargs):
        logging.debug(f"Custom invocation of the wrapped function, message={self.custom_msg}")
        if 'arg1' in kwargs: # Only do this for methods which have 'arg1'
            kwargs['arg1']="OVERRIDDEN" # Override 'arg1' argument      
        logging.debug(f"This method is being called for {func} with instance={instance}")
        # Modify the return value if one exists
        ret_val = super().exec_wrap(func,instance,*args,**kwargs)
        if ret_val:
            return ret_val * 2
    
class A(object):
    '''Example base class with a couple of registered methods'''
    def __init__(self,bound_val):
        self._bv = bound_val

    @my_decorator
    def method1(self):
        logging.debug(f"method1 got called on {self} with bound value {self._bv}")

    @my_decorator
    def method2(self):
        logging.debug(f"method2 got called on {self} with bound value {self._bv}")

class B(A):
    '''Example derived class with a couple of additional registered methods'''

    @my_decorator
    def method3(self):
        logging.debug(f"method3 got called on {self} with bound value {self._bv}")

    @my_decorator(custom_msg="THIS IS A CUSTOM MESSAGE")
    def method4(self,arg1,arg2):
        logging.debug(f"method4 got called with arg1={arg1}, arg2={arg2} on {self} with bound value {self._bv}")
        return 42.0

def main():
    a  = A(bound_val=1234)
    b0 = B(bound_val=5678)

    a.method1()
    a.method2()

    b0.method1()
    b0.method2()
    b0.method3()
 
    # Method4 returns a value, so print it
    logging.debug(b0.method4(arg1="ABC",arg2="RST"))

if __name__ == '__main__':
    main()
