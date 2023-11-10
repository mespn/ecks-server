#!/bin/bash

# Change this!
HOST="cormorant.cs.umanitoba.ca"
PORT=8991

for item in `seq 1 40`
do
    (echo '{"type":"SET", "id":"key", "obj":"value '$item'"}' | nc -w4 $HOST $PORT) &
done
wait
echo "Done setting. Most of these should fail."

# get them all (any order)

echo '{"type":"GET"}' | nc -w1 $HOST $PORT

wait
echo "Done"