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
    limit     : write-count-limit of attribute whose write limit was exceeded
    '''
    def __init__(self,msg,name='',limit=0):
        self.attribute_name        = name
        self.attribute_write_limit = limit
        super().__init__(msg)

    def __str__(self):
        ostr = ''
        for k,v in self.__dict__.items():
            ostr += f'{k}:{v}, '
        return ostr[:-2]

class WriteLimited(object):
    '''
    General purpose write-count limiting descriptor class to enable class attributes
    which require limiting the number of writes of a given attribute. The wcount_limit
    initializing argument sets the maximum number of writes allowed to an attribute

    Configuration:
    --------------
    - When wcount_limit=0 there are no writes allowed (including initialization), and
      this attribute behaves as a class-level constant (of the client class), such
      that all objects of the client class return const_val
    - For wcount_limit >=1 behaves as expected, where total writes (including those
      by the client-object __init__ method, are limited to wcount_limit)
    - Creating a client-object-specific read-only attribute which can be initialized
      can be achieved by setting wcount_limit to 1 and initializing the attribute in the 
      client-class __init__ method. After the __init__ method is executed, no other
      writes will be permitted

    Exceptions (behavior when exceeding the write-limit is attempted):
    ------------------------------------------------------------------
    When a wcount_limit has been reached for a given attribute, any subsequent write
    will resulting in the WriteLimitError exception being thrown. The exception
    can be disable on a per-descriptor basis by initializing with dis_except=True

    Attribute state checking utility methods:
    -----------------------------------------
    There are three static utility methods which can be used to get relevant state on any
    client instance's attributes based on WriteLimited descriptors:
    - WriteLimited.getattr_ro(instance,name:str)->bool : Returns if attribute is in read-only state
    - WriteLimited.getattr_wcount(instance,name:str)->int : Returns attribute write-count
    - WriteLimited.getattr_wcount_limit(instance,name:str)->int : Returns attribute write-count-limit

    Note that these methods are static and must be called with the descriptor class name.
    Also note that the interface follows the Python data-model getattr() method

    Example Usage:
    --------------

    class Example(object):
        attribute_1 = WriteLimited(0,3.142) # Class-level constant with value 3.142
        attribute_2 = WriteLimited(0,2.718,dis_except=True) # Class-level constant, no exceptions
        attribute_3 = WriteLimited(1) # Initialize-once, read-only after
        attribute_4 = WriteLimited(2) # Initialize-once, write-once, then read-only
        attribute_5 = WriteLimited(11) # Initialize, then write 10 more times, then read-only

        def __init__(self):
            self.attribute_3 = 3 # initialize the read-only (by user) attribute
            self.attribute_4 = 4 # initialize the write-once (by user) attribute
            self.attribute_5 = 5 # initialize allowing user to write 10 more times

    Checking whether attribute_2 for example is read-only on an Example class object 
    can be done as follows:

    example = Example()

    if getattr_ro(example,'attribute_2'):
        ... do something

    '''

    # Important implementation details:
    # For each instance of a client class we create "shadow" attributes which hold the following values:
    # - A "private" attribute to hold the actual value of the instance-bound attribute
    # - An attribute to hold the instance-bound write-count associated with the attribute
    #   - This attribute is created the first time we set an attribute on an instance
    #   - This attribute is updated each time we either get or set the attribute. By updating this
    #     during a get, it allows a utility method to get the write-count/read-only state of an
    #     instance-bound attribute

    shadow_prefixes = {
        'private' : '_WL_SHADOW_PRIVATE_',
        'count'   : '_WL_SHADOW_COUNT_',
        'ro'      : '_WL_SHADOW_RO_',
        'limit'   : '_WL_SHADOW_LIMIT_'
    }

    # Utility functions to determine the write-count or read-only state
    # of a given object instance
    @staticmethod
    def getattr_ro(instance,name:str)->bool:
        '''
        Returns a boolean reflecting whether the attribute 'name' for the object 'instance'
        is currently read-only
        '''
        return instance.__dict__[WriteLimited.shadow_prefixes['ro']+name]

    @staticmethod
    def getattr_wcount(instance,name:str)->int:
        '''
        Returns an int reflecting the current write-count of attribute 'name' for the object 'instance'
        '''
        return instance.__dict__[WriteLimited.shadow_prefixes['count']+name]

    @staticmethod
    def getattr_wcount_limit(instance,name:str)->int:
        '''
        Returns an int reflecting the write-count-limit of the attribute 'name' for the object 'instance'
        '''
        return instance.__dict__[WriteLimited.shadow_prefixes['limit']+name]

    def __set_proxies(self,instance,count:int):
        setattr(instance,self._name_count,count)
        setattr(instance,self._name_ro,count == self._wcount_limit)
        setattr(instance,self._name_limit,self._wcount_limit)

    def __get_count(self,instance)->int:
        try:
            return getattr(instance,self._name_count)
        except AttributeError: # initialize for first set
            return 0

    def __init__(self,wcount_limit=1,const_val=None,dis_except=False):
        self._wcount_limit   = max(0,wcount_limit)
        self._const_val      = const_val
        self._dis_except     = dis_except

    def __set_name__(self,owner,name):
        self._name_public  = name # "Public" attribute name (refers to this descriptor object)
        self._name_private = WriteLimited.shadow_prefixes['private'] + name # shadow attribute per client instance which holds the actual value
        self._name_count   = WriteLimited.shadow_prefixes['count']   + name # shadow attribute per client instance which holds the write-count
        self._name_ro      = WriteLimited.shadow_prefixes['ro']      + name # shadow attribute per client instance which holds the read-only state
        self._name_limit   = WriteLimited.shadow_prefixes['limit']   + name # shadow attribute per client instance which holds a copy of the limit

    def __get__(self,instance,inst_type=None):
        # We re-fresh/set shadow values when we read attributes so that the
        # utility functions can do a priming read before returning shadow values
        if self._wcount_limit == 0: # zero-write (constant) case
            self.__set_proxies(instance,0)
            return self._const_val
        else:
            return getattr(instance,self._name_private)

    def __set__(self,instance,value): 
        # Get the latest count for this instance
        instance_wcount = self.__get_count(instance)             
        if self._wcount_limit > 0 and instance_wcount < self._wcount_limit:
            setattr(instance,self._name_private,value)
            instance_wcount += 1
            self.__set_proxies(instance,instance_wcount)
        else:
            if not self._dis_except:
                error_msg = f"Maximum writes exceeded to '{self._name_public}' (max-count={self._wcount_limit} reached)"
                raise WriteLimitError(error_msg,self._name_public,self._wcount_limit)

