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

from dataclasses import dataclass
from dataclasses import field
from dataclasses import InitVar
import pandas as pd
import random 
import math

@dataclass
class DataClass_Modern(object):

    '''
    dataclasses based imlpementation
    (see https://medium.com/swlh/python-dataclasses-with-properties-and-pandas-5c59b05e9131)
    '''
    # Invisible attribute (init-only)
    attr0:InitVar[int] = 81

    # Initialized attribute
    attr1:int   =0
    attr2:float =0.
    attr3:str   ='undefined'
    attr4:list  = field(default_factory=list)

    # Generated attribute
    attr5:float = field(init=False)

    # Generated attribute - read property
    @property
    def attr5(self)->float:
        return math.sqrt(abs(self._attrHidden))

    # Generated attr - set property (required by dataclasses)
    @attr5.setter
    def attr5(self,_):pass # Do nothing, this is a read-only attribute

    def __post_init__(self,attr0):
        # Make a copy of the init-only attribute to a local attribute that
        # is used for the generated attribute (via a property)
        self._attrHidden = attr0 # This attribute should remain hidden from pandas

class DataClass_Classic(object):
    '''
    Classic imlpementation without dataclasses
    '''

    def __init__(
        self,
        attr0:int=81,
        attr1:int=0,
        attr2:float=0.,
        attr3:str='undefined',
        attr4:list=None):

        self._attrHidden = attr0
        self.attr1       = attr1
        self.attr2       = attr2
        self.attr3       = attr3
        if attr4 == None:
            self.attr4 = []
        else:
            self.attr4=attr4
 
    # Generated attribute - read property
    @property
    def attr5(self)->float:
        return math.sqrt(abs(self._attrHidden))

    def __str__(self)->str:
        ostr =  f'attr1={self.attr1},'
        ostr += f'attr2={self.attr2},'
        ostr += f'attr3={self.attr3},'
        ostr += f'attr4={self.attr4},'
        ostr += f'attr5={self.attr5}'
        return ostr


    def asdict(self)->dict:
        '''
        Custom method to return a dict which is selective. This is required to
        filter out attr0, _attrHidden and provide attr5 as an attribute
        '''
        tmpDict = {}
        for k,v in self.__dict__.items():
            if k not in ['attr0','_attrHidden']:
                tmpDict[k] = v
        # Now we need to add attr5 which by default won't be picked up 
        # by the standard __dict__ method because it is a pure property
        tmpDict['attr5']=self.attr5
        return tmpDict

class DataClass_Factory(object):
    '''
    Simple random factory class to generate random initializer calls for
    the Modern and Classic examples
    '''

    def __init__(self,cls):
        self._cls = cls

    def __call__(self):
        '''
        Returns an object of the calling class with randomized initialization attributess
        '''
        return self._cls(
            attr0=random.randint(-1e3,1e3),
            attr1=random.randint(-1e6,1e6),
            attr2=random.random(),
            attr3=random.choice(
                [
                    'Tool',
                    'PinkFloyd',
                    'Soundgarden',
                    'FaithNoMore',
                    'aPerfectCircle',
                    'KingCrimson',
                    'PearlJam',
                    'ChildrenOfBodom']),
            attr4=random.choices(range(100,999),k=3)
            )

def main():
    print("\n=================================================================")
    print("Example1: Using dataclasses")
    print("=================================================================")

    rand_objects = [DataClass_Factory(DataClass_Modern)() for _ in range(100)]
    df = pd.DataFrame(rand_objects)

    print(df)

    print("\n=================================================================")
    print("Example2: Using classic approach with __dict__")
    print("=================================================================")

    objects_old = [DataClass_Factory(DataClass_Classic)().__dict__ for _ in range(100)]
    df = pd.DataFrame.from_dict(objects_old)

    print(df)

    print("\n=================================================================")
    print("Example3: Using classic approach with custom dict method")
    print("=================================================================")

    objects_old_fixed = [DataClass_Factory(DataClass_Classic)().asdict() for _ in range(100)]
    df = pd.DataFrame.from_dict(objects_old_fixed)

    print(df)

if __name__ == '__main__':
    main()