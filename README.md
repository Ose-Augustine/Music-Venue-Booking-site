# fyurr-webapp
### Introduction

This is a web application where artists and different venues can make a listing, post shows and interact with the different pages. This is my first project on full stack web development in the udacity full stack course. Every needed change and modification in to the starter_code is in the commits .

#### Features 
* The app allows artists and venues to register live data into a database. The example in the code is a local postgresql database.
* Recently listed artists and shows are displayed on the homepage.
* Every artist has the ability to register the times they will be available for booking. So a venue cannot book a show outside of the artists available time.
* Partial string search as well as searching by city and state pairs has been enabled to make it easier to navigate throuhg the site.
* Venues can be deleted if no longer available.

#### Notes 

 On this project , I used the following concepts to bring the website to completion:
 * Flask 
 * Flask-WTF forms 
 * Posgresql
 * SQLAlchemy ORM
 * The datetime module in python 
 
 The above are the summary of what i used to :
 * Create a db model to influence and design my database shcema
 * Maintaing referencial integrity between the tables having one to many and many to many relationships.
 * Provide datetime comparisons and default setttings. This is used in the creation time columns of my Artist and Venue models where instead of (db.Column(db.DateTime(timezone=True, default = datetime.now()))) I used server_default = datetime.now(). The former depended on the network latency of the user while the latter is set solely by the database server so no discripancies would arise.
 * Create a formfield that sends the data of the artists available time as one of the same field rather than creating extra forms for it . 
 *There are many more of these features i learned working on the project but these are but to mention a few.

 