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

import random
from WriteLimited import WriteLimited, WriteLimitError

class A(object):
    '''
    Test class which uses a write-limit of 0 (i.e. a constant value) which is
    applied to all objects of this class
    '''

    # Set a class-level constant attribute with value 42
    attr_const = WriteLimited(0,42)
    attr_const_no_except = WriteLimited(0,42,dis_except=True) # No exceptions

class B(object):
    '''
    Test class which creates a per-object attribute that is initialized and then
    becomes read-only. This is essentially a "write-once" case
    '''

    # Create a read-only (initialized once) attribute
    attr_ro = WriteLimited(1)

    def __init__(self):
        # Initialize to a pre-determined integer. Write-once, then read-only
        self.attr_ro = 1234

class C(object):
    '''
    Test class which creates a per-object attribute that can only be written 
    10 times (including the initialization)
    '''

    # Create a 10-write limited attribute
    attr_w10 = WriteLimited(10)

    def __init__(self):
        self.attr_w10 = random.randint(0,99)

class ExampleUse(object):
    '''
    Example of a class which uses all the features of WriteLimited attributes
    '''

    # We assign each attribute with an appropriate class-level descriptor
    attribute_1 = WriteLimited(0,3.142) # Class-level constant with value 3.142
    attribute_2 = WriteLimited(0,2.718,dis_except=True) # Class-level constant, no exceptions
    attribute_3 = WriteLimited(1) # Initialize-once, read-only after
    attribute_4 = WriteLimited(2) # Initialize-once, write-once, then read-only
    attribute_5 = WriteLimited(11) # Initialize, then write 10 more times, then read-only

    def __init__(self):
        self.attribute_3 = 3 # initialize the read-only (by user) attribute
        self.attribute_4 = 4 # initialize the write-once (by user) attribute
        self.attribute_5 = 5 # initialize allowing user to write 10 more times

    def __str__(self):
        ostr = '\nExampleUse object:\n'
        ostr += f'attribute_1 = {self.attribute_1}\n' 
        ostr += f'attribute_2 = {self.attribute_2}\n'
        ostr += f'attribute_3 = {self.attribute_3}\n'
        ostr += f'attribute_4 = {self.attribute_4}\n'
        ostr += f'attribute_5 = {self.attribute_5}\n'
        return ostr

def main():
    a0=A()
    a1=A()
    assert a0.attr_const == a1.attr_const, "Class A attr_const should be constant across all objects"
    b=B()
    c=C()
    print(f"a0.attr_const = {a0.attr_const}")
    print(f"a1.attr_const = {a1.attr_const}")
    print(f"b.attr_ro     = {b.attr_ro}")
    print(f"c.attr_w10    = {c.attr_w10}")

    print("\nAttempt to modify a0.attr_const")
    try:
        a0.attr_const += 1
    except WriteLimitError as e:
        print(f"Got WriteLimitError exception, error details: {e}")

    print("\nAttempt to modify a0.attr_const_no_except (no exception expected)")
    try:
        a0.attr_const_no_except += 1
        assert a0.attr_const_no_except == 42, "constant value was modified"
    except WriteLimitError as e:
        raise RuntimeError("Got an unexpected WriteLimitError exception")

    print("\nAttempt to modify b.attr_ro (post initialization)")
    try:
        b.attr_ro += 1
    except WriteLimitError as e:
        print(f"Got WriteLimitError exception, error details: {e}")

    print("\nAttempt to write c.attr_w10 indefinitely")
    wcount = 1 # First count is the class initializer
    try:
        while True:
            wcount +=1
            c.attr_w10 = wcount
            print(f"Wrote random value {c.attr_w10} to c.attr_w10")
    except WriteLimitError as e:
        print(f"Got WriteLimitError exception, error details: {e}")

    # Instantiate the ExampleUse class
    example = ExampleUse()
    example.attribute_2 = 100.0 # Should not modify, and not raise exception
    print(example)

    # Use the utility methods on attribute_2
    print(f"\nattribute_2 write-count={WriteLimited.getattr_wcount(example,'attribute_2')}, is_read-only = {WriteLimited.getattr_ro(example,'attribute_2')}")

    print("\nNow write to example.attribute_5 11 times, which should result in an un-handled exception")
    # Note: we also use the static utility methods to get the write-count and read-only state for the attribute
    for k in range(11):
        example.attribute_5 = k
        print(f"Wrote {k} to attribute_5",end='')
        print(f", write-count = {WriteLimited.getattr_wcount(example,'attribute_5')}, is_read-only = {WriteLimited.getattr_ro(example,'attribute_5')}")

if __name__=='__main__':
    main()