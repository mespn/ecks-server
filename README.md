# ecks-server

## Parts of the program

This program is made of 4 parts, 3 of which are in their own directory.

The parent directory is the web server. It contains the directories with

- the frontend files (ecks)
- the database files (database)
- 2 load tests (load_tests)

## To run

To run this program, it is necessary to run 3 different scripts. The commands below
are meant to be ran from the parent directory

- Web server `python ./web_server.py [database_host]`
- Database coordinator `python ./database/coordinator.py [worker_host:port]`
- Database workers `python ./database/coordinator.py [port]`

### Notes

The Web Server's port is 8990.

The database_host argument in the web_server is there for convenience. It is set to localhost as default and it
references the location of the coordinator. Its port is set by default, and there is no reason to edit it.

The coordinator can call as many workers as needed.

## Database Protocol

To get the database: `{"type": "GET"}`

To edit an item: `{"type": "GET", "id":tweet_id, "obj":tweet}`.

    Note that {"type": "GET", "id":"", "obj":tweet} creates a new item in the database.

### Testing the 2PC separately

The message `{"type":"LOCK", "id":tweet_id}` locks the tweet with id `tweet_id`.
