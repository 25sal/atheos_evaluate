# pyevaluate

## Installation
## Standalone installation
### Database configuration
Use the database dump  dump/evaluatex.sql to create a mysql database
```bash
mysql -u USER -p evaluatex < dump/evaluatex.sql
```
Update the database connection string in #app/init_db.py# with your credentials
### Data folder configuration
Copy the data folder in your prefered location (here /home/evaluatex), and create the users dir in the same location
```bash
cp -r data /home/evaluatex
mkdir /home/evaluatex/users
```
### Install requiremnts
Move in the software directory and exec
```bash
pip install -r requirements.txt
```
### Start the application 
Start flask. The web page should be available at http://localhost:5000/
```bash
flask run
```
## Docker installation
```bash
docker build . --tag pyevaluate
docker-compose up -d
```

## Configuration
The application is already configured to save database information and users' directories in two different persistent volumes.
The application starts in trial mode, that means registered users can choose programming language and a list of exercises to test


## User Guide

* Open: http://localhost:8001/index.php
* Register an account with username and password.
* Login with credentials
* Choose the programming language
* Select the exercise
* Download the templates
* Upload the solution
* Click test to run tests and to check the correctness of solutions
