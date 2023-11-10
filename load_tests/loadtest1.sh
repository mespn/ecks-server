#!/bin/bash

# Change this!
HOST="cormorant.cs.umanitoba.ca"
PORT=8991

for item in `seq 1 30`
do
    (echo '{"type":"SET", "id":"key '${item}'", "obj":"value '$item'"}' | nc -w4 $HOST $PORT) &
done
wait
echo "Done setting. Should have taken less than four seconds"

# do an update

for item in `seq 1 30`
do
    (echo '{"type":"SET", "id":"key '${item}'", "obj":"updated value '$item'"}' | nc -w4 $HOST $PORT) &
done
wait
echo "Done updating. Should have taken less than four seconds"

# get them all (any order)

echo '{"type":"GET"}' | nc -w1 localhost $PORT

wait
echo "Done"