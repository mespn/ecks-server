# Protocol

## WEB SERVER -> DB SERVER

### Ask for Database

``` json
{type: "GET"}
```

### Create a new tweet

``` json
{
  type: "SET", 
  author: author,
  content: tweet
  }
```

### Update a tweet

``` json
{
  type: "UPDATE", 
  id: tweet-id
  author: author,
  content: tweet
}
```

---

## COORDINATOR -> WEB SERVER

### Response to GET request

```json
{
  type: "GET-RESPONSE",
  payload_type: "DB",
  db: tweet_database
}
```

### Response to SET request

```json
{
  type: "SET-RESPONSE",
  success: true/false
}
```

### Response to UPDATE request

```json
{
  type: "UPDATE-RESPONSE",
  success: true/false
}
```

### Errors

```json
{
  type: "ERROR",
  scope: "REQUEST"/"SERVER"
  details: other_info
}
```

---

## COORDINATOR -> WORKER

### Ask for the Database

``` json
{ type: "GET"}
```

### Change database

``` json
{ 
  type: "SET",
  id: tweet_id,
  content: tweet
}
```

### Start Two-Phase-Commit

``` json
{type: "LOCK"}
```

---

## WORKER -> COORDINATOR

### Response to GET

``` json
{ 
  type: "GET-RESPONSE",
  payload-type: DB,
  db: tweet_database
}
```

### Response to LOCK

``` json
{ 
  type: "LOCK-RESPONSE",
  success: true/false
}
```

### Response to SET

``` json
{ 
  type: "SET-RESPONSE",
  success: true/false
}
```
