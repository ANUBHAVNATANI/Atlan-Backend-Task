# Atlan-Backend-Task

## Introduction

Backend internship task

There are three operations in this application
1. Upload a baseline data for the form
2. Export the uploaded data
3. Create multiple teams

All three operations are long running tasks user should be able to stop them at point to time

I have also implemented functionality to pause and resume the task as well

Technologies/Tools Used:
  - Python
  - Flask
  - SQLite databse

## Run the flask appliction (Use this)
1.  Do a pip install requirements.txt
2.  Run python app.py

## Run using the docker container (Currently in development)
Make sure you have [Docker](https://docs.docker.com/installation/).
  1. Clone the project
  `https://github.com/ANUBHAVNATANI/Atlan-Backend-Task.git`
  2. Move to project folder
  `cd Atlan-Backend-Task`
  3. Run `docker build --tag collect:1.0 .` and wait for Docker to build the image.
  4. Run `docker run --publish 8000:8000 --detach --name bb collect:1.0`
  5. Open `http://localhost:8000/` in your browser to open the app
  
  ## APIs
   1. **API to baseline upload CSV file**
   `http://localhost:8000/baselineUpload` 
 
   Method: POST  
   Server receives file with key as `file`  
   This API uses threading event in python to upload the file. If it is completed successfully the data is stored in the database otherwise you can stop, pause or resume the task.
   >There is a sample csv file in sampleData named MOCK_FORM_DATA csv file should be formatted like this.
   
   2. **API to create teams from CSV file**
   `http://localhost:8000/createTeams`  

   Method: POST  
   Server receives file with key as `file`  
   This API uses threading event in python to upload the file. If it is completed successfully the data is stored in the database otherwise you can stop, pause or resume the task.
   >There is a sample csv file in sampleData named MOCK_TEAM_DATA csv file should be formatted like this.
   
   
  2. **API to Export Data**
   `http://localhost:8000/export`
  
   Method: GET  
   This API starts also uses python threading event and get the data from the database and we can stop, pause and resume the samme task.
   
 
  3. **API to Stop a Task**
   `http://localhost:8000/stop`  
  
    This is will stop the current long running task

  4. **API to pause a Task**
    `http://localhost:8000/pause`

    This is will pause the current long running task

  5. **API to resume a Task**
    `http://localhost:8000/resume` 
   
    This is will resume the current long running task
  
  6. **API to clear data from database**
    `http://localhost:8000/clearDatabase` 

    This is will clear data from both database 

 7. **API to get ths status of a Task**
    `http://localhost:8000/status` 
   
    This is will get the status of current long running task

 8. **API to get all the teams**
    `http://localhost:8000/getTeams` 
   
    This is will get all the teams in the database