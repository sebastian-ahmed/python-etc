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

if __name__=='__main__':
    main()