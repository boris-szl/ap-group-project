# ap-group-project
project for advanced programming

# Project description
This script scrapes listing data based on the first page on Chrono24 for an arbitrary reference number.
Subsequently the program statistically describes the data based on the entries, giving infromation about the 
descriptive nature, including location parameters such as min, max, mean; about the distribution such as std and quartiles. 

# Setup project
## Clone the project using git https or ssh
```
$ git clone <url> 
```
## Install virtualenv
Install virtualenv
```
$ pip install virtualenv
```
## Create a virtualenv
Create a virtualenv called `myenv`
```
$ virutalenv myenv
```
## Activate your virtual env
```
$ source myenv/bin/activate
```
## Install the packages 
Install the requirements for the file
```
$ pip install -r requirements.txt
```
# Run project
## Run the script
You must me in the int the `src/` directory to run this command:
```
$ python main.py
```




