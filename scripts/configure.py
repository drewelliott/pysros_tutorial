#!/usr/bin/env python3
 
from helpers import get_connection
from pysros.wrappers import *

ROUTER = '10.5.5.5'
USER = 'admin'
PASS = 'admin'
PORT = 830
    
def main():
    c = get_connection(ROUTER, USER, PASS, PORT)

    path = '/nokia-conf:configure/port'
    data = {
    '1/1/c1': Container(
        {'port-id': Leaf('1/1/c1'), 
        'admin-state': Leaf('enable'), 
        'connector': Container({'breakout': Leaf('c1-100g')})}), 
    '1/1/c1/1': Container(
        {'port-id': Leaf('1/1/c1/1'), 
        'admin-state': Leaf('enable')}), 
    '1/1/c2': Container({
        'port-id': Leaf('1/1/c2'), 
        'admin-state': Leaf('enable'), 
        'connector': Container({'breakout': Leaf('c1-100g')})}), 
    '1/1/c2/1': Container({
        'port-id': Leaf('1/1/c2/1'), 
        'admin-state': Leaf('enable')})}

    c.candidate.set(path, data)

if __name__ == "__main__":
    main()