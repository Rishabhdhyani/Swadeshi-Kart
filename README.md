# Swadeshi-Kart
An E-commerce website built using the Django web framework. It provides various functionalities including Review and Rating System. It also comes with very efficient search engine and recommender system which is build using matrix factorization based algorithm(SVD). This website uses Paypal business account for payment gateway integration.

## Stack

* Django(Python REST API)
* Python
* Sqlite3(Development)
* PostgreSQL(Production)
* scipy
* scikit-surprise
* [Heroku](https://swadeshikart.herokuapp.com/)
* Numpy
* Pandas

## Installation Procedure

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can create virtual env as follows:-

* python3 -m venv /path/to/new/virtual/environment/kart

To activate the virtual env, execute the following command:-

* source kart/bin/activate

Then install the project dependencies with

* pip install -r requirements.txt

Execute following command for database execution:-

* python manage.py makemigartions
* python maange.py migrate
* python manage.py collectstatic

Now you can run the project with this command

* python manage.py runserver

**Note** Don't forget to put environment varibles in the .bash_profile file.




