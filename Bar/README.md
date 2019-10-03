# Bar app

runs server and GUI to see incoming orders.

## API

RESTful API to manage database requests.

contains dynamic query functions.

## Server

socket server, listening for connections.

connection sends a request in data form, which contains the function, attributes.

the server handles this function and executes them.

### Message Transfer

Each connection sends bytes message, first is the header.

which contain the length of the message, username and for privacy can provide an encrypted password.

then the server receives the message until the length is equal to the given in the header.

the message stored as Data.

### Data structure

this Data contains a function which is a query, and attributes which are a dictionary of a key, value pairs.

then using the API controller, the server executes those functions.

## DataBase - SQLite3

used this database to easy import and export database file for backup or maintain on PC.(stored on the device)
