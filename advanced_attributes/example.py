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

class Base(object):

    def __init__(self):
        self._ro = {}
        self._prot = {}

    def __getattr__(self,name):
        if name in self._ro.keys():
            return self._ro[name]
        else:
            raise AttributeError

    def __setattr__(self,name,val):
        if name in ['_ro', '_prot']:
            super(Base,self).__setattr__(name,val)
            return
        if name.replace('_PRAGMA_RO_','') in self._ro.keys():
            raise AttributeError(f"Attempted to write to read-only field {name.replace('_PRAGMA_RO_','')}")
        if name.replace('_PRAGMA_PROT_','') in self._prot.keys():
            pass            
        if name.startswith('_PRAGMA_RO_'):
            self._ro[name.replace('_PRAGMA_RO_','')] = val
            return
        else:
            super(Base,self).__setattr__(name,val)

class Derived(Base):
    def __init__(self,*args,**kwargs):
        super(Derived,self).__init__(*args,**kwargs)
        self._PRAGMA_RO_ro_field1 = 27
        self._PRAGMA_RO_ro_field2 = 28
        self.field3 = 42
        self.field3 = 43

def main():
    d = Derived()
    d._var1 = 5
    print(d.__dict__)

    print(f'd.ro_field1={d.ro_field1}')
    print(f'd.ro_field2={d.ro_field2}')
    print(f'd.field3   ={d.field3}')
if __name__ == '__main__':
    main()