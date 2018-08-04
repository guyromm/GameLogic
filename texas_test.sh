#!/bin/bash
echo '*** deal and make sure are equal'
./texas.py new deal save | jq . > /tmp/1 &&
    ./texas.py load save < /tmp/1 | jq . > /tmp/2 &&
    (diff -Nuar /tmp/1 /tmp/2 | wc -l)
echo '*** create and then deal, make sure are different.'
./texas.py new save | jq . > /tmp/1 &&
    ./texas.py load deal save < /tmp/1 | jq . > /tmp/2 &&
    (diff -Nuar /tmp/1 /tmp/2 | wc -l)
