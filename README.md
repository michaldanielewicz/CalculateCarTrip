# Calculate Car Trip

With this app you can easily look up estimated cost of travel by car. 

## Why?
I travel a lot with my friends around my country. I was sick of always checking prices of fuel, distance etc. so I decided to write this app.
I also wanted to create this app to improve my skills in Flask, managing databases, working with HTML and CSS. 

## Technologies
* Python - version 3.9.1
* Flask - version 1.1.2
* Flask-SQLAlchemy - version 2.4.4 

## Database
I searched web for car databases. After some time of reasearch I've found [this](https://www.fueleconomy.gov/feg/ws/). I've downloaded it and make some cleaning. It counted around 45 columns (data about CO2, year and many other things). I erased some corupted data and not important stuff.
After that I've done some testing on local database. After deploying on Heroku I noticed that I have to erase about 75% of data because of 10,000 records
limit on hobby-dev on Heroku. 
It is possible to add new cars, be happy to add some cars of your choice. :)

## Live
You can check the live version [HERE](https://calculatecartrip.herokuapp.com/) (Heroku).

## Features
List of features ready and TODOs for a future development.

### Ready:
* Calculate the cost of trip for desired car.
* Add new car to the database.
* Choose origin and destination place.
* Add passengers.

### To-do list:
* Add cost of highway tickets.
* Add interactive map.
* Change CSS to comprehend different windows size and mobile.

## Status
Project is: _in progress_.

## Contact
Created by [@michaldanielewicz](https://michaldanielewicz.github.io/) - feel free to contact me!
