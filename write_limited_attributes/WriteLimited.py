# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

class WriteLimitError(Exception):
    '''
    Specialized exception to support WriteLimited class. When an object of this class
    is thrown the following attributes can be inspected:
    name      : name of write limited attribute whose write limit was exceeded
    count     : max write-count of write limited attribute whose write limit was exceeded
    '''
    def __init__(self,msg,name='',count=0):
        self.attribute_name = name
        self.max_wcount     = count
        super().__init__(msg)

    def __str__(self):
        ostr = ''
        for k,v in self.__dict__.items():
            ostr += f'{k}:{v}, '
        return ostr[:-2]

class WriteLimited(object):
    '''
    General purpose write-count limiting descriptor class to enable class attributes
    which require limiting the number of writes of a given attribute. The wcount_max
    initializing argument sets the maximum number of writes allowed to an attribute

    Configuration:
    --------------
    - When wcount_max=0 there are no write allowed, and this attribute behaves as
      a class-level constant (of the client class), such that all objects of the client
      class return const_val
    - Value of wcount_max >=1 behave as expected, where total writes (including those
      by the client-object __init__ method, are limited to wcount_max)
    - Creating a client-object-specific read-only attribute which can be initialized
      can be achieved by setting wcount_max to 1 and initializing the attribute in the 
      client-class __init__ method. After the __init__ method is executed, no other
      writes will be permitted

    Exceptions (behavior when exceeding the write-limit is attempted):
    ------------------------------------------------------------------
    When a wcount_max has been reached for a given attribute, any subsequent write
    will resulting in the WriteLimitError exception being thrown. The exception
    can be disable on a per-descriptor basis by initializing with dis_except=True

    '''

    def __init__(self,wcount_max=1,const_val=None,dis_except=False):
        self._wcount_max     = max(0,wcount_max)
        self._wcount         = 0
        self._const_val      = const_val
        self._dis_except     = dis_except

    def __set_name__(self,owner,name):
        self._name_public  = name
        self._name_private = '_WMAX_' + name

    def __get__(self,instance,inst_type=None):
        if self._wcount_max == 0: # zero-write (constant) case
            return self._const_val
        else:
            return getattr(instance,self._name_private)

    def __set__(self,instance,value):
        if self._wcount < self._wcount_max:
            setattr(instance,self._name_private,value)
            self._wcount += 1
        else:
            if not self._dis_except:
                error_msg = f"Maximum writes exceeded to '{self._name_public}' (max-count={self._wcount_max} reached)"
                raise WriteLimitError(error_msg,self._name_public,self._wcount_max)
