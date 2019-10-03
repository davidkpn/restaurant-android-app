# Restaurant Waiters - Bar application

this kivy application can run cross-platform thanks to the kivy python library.

tested well on android, Linux, and Windows 10.

This app is divided into two sub-apps.

App for the bartender, there he sees which orders he has to make.

And an app for a waiter where the waiter sees the tables and clients.

Also, the waiter can manage an order at any time - adding or deleting products.

These sub-apps are connected with TCP socket, and any update from one app is passed to the other on the same session.

![image](https://media.giphy.com/media/U43wxeN9EHvus2jLCZ/giphy.gif)

## Bar sub-app

The bar's app referred to bartender control.



This app contains the database (SQLite).


and initialize the restaurant server.


no need for port forwarding and can run on device hot spot.


(all the devices should be connected to the same net)


any add/remove/update/get requests are passed from the bar app to the waiter app.


## Waiter sub-app

The waiter needs to connect to the bartender's server, by a given IP and username.


waiter's app referred for the walking waiter holding the tablet,


and he can live update all any database data (which he got permission to) on the bartender's app,


with SQL queries, and the TCP socket connection.


This app can work with a few different waiters connecting to the same Bar app server.
