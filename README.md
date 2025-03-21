# Python + Jenkins 

## Problem specification

```

1- Code a simple application that exposes the following HTTP based APIs: 

Description: Save/updates a given user name and date of birth in a database. 

Request: PUT /hello/<username> { “dateOfBrith”: “YYYY-MM-DD” } Response: 204 No Content 

Note: 
Username should only be letters. 
YYYY-MM-DD must be a date before today's date. 

Description: Returns a birthday message. 

Request: Get /hello/<username> Response: 200 Ok Response examples: 

A. If username’s birthday is in N days: { “message”: “Hello, <username>! Your birthday is in N day(s)”} 

B. If username’s birthday is today: { “message”: “Hello, <username>! Happy birthday!” } 

Note: Use the storage or DB of your choice. 

2- Code a simple helm chart and deploy this application into a small local kubernetes cluster (like minikube or k3s) 

3- Produce a system diagram of how this solution would be deployed into AWS. You can consider that the application is of high criticality and high usage, so add



```

## Tools, repos and deloyments 



## Project structure 



## How to run and test locally



## How to run and test via docker-compose
```bash
docker-compose up test_server
docker-compose up run_server
```

## Prerequisites
```bash
pip install -r requirements.txt
```

## Setting up

### OSX
```bash
brew update
brew install python
pip install -U pytest
pytest --version
pip install -r requirements.txt
echo 'export PATH=/usr/local/opt/python/libexec/bin:/Users/Ivan/Library/Python/3.7/bin:$PATH' >> ~/.bash_profile
```