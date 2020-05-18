# EdTechHub Searchable Publications Database (SPuD)

The EdTech Hub is a hub for and of research excellence. Any credible, high quality research endeavour needs to build on the prior literature. The EdTech Hub, with its unique vantage point across the sector, needs to be deeply familiar with that prior literature — not only to synthesise learning, but also to understand research priorities and skills within the educational technology sector.

This has led to the need to develop a Searchable Publications Database (SPuD) that utilises technology in research to enable unprecedented depth and turn-around time in literature review and analysis. The purpose to create a comprehensive database for researcher to search for relevant literature on technology use in education in low- and middle-income countries faces. SPuD allows for cross-database searching given that no database contains all the relevant publications. It also offers optimised searches where broad or generic terms like ‘sub-Saharan Africa’ or ‘laptop’ do not return the most relevant results.

The first version of the database was completed in January 2020 and the project is currently in it’s second phase. This second phase seeks to improve the reliability and usability of the database through the web interface.


### Environment Details
- Ubuntu 18.04
- Django 3.0.2
- PostgresSQL 11.5 (Google Cloud)
- Python 3.6


## Deployment

- to install dependencies please run
```html
pip install -r requirements.txt
```


### Google Cloud PostgresSQL Instance Settings

- Choose SQL instance from [SQL instances list](https://console.cloud.google.com/sql/instances/)

- Click `Connections` on left panel and whitelist your machine's IP

- To get any machine's IP - hit (CURL) [A Simple Public IP Address API](https://api.ipify.org/?format=json)

- Click `Databases` and create new one if it hasn't been created before


### Virtual Environment

- install virtual environment by using command
```html
sudo apt install python3-venv
```

- create and run virtual enviroment
```html
python3.6 -m venv venv
source venv/bin/activate
```


### Starting Web Application

- go into `spud` folder inside root direcotry and run following command
```html
/usr/bin/python3.6 manage.py runserver
```

- Access your application on your [localhost](http://127.0.0.1:8000/)


### Settings and Authentication

- Please rename `.env.example` to `.env` and fill out configuration variables 

- Auth token is rquired to access application which you can get from admin. If not used you will get `401 Unauthorized` error


### Highlighting feature

To add new keywords in old categories, expand the Python lists in the settings.py file with new additional keywords.

To add new keyword categories:
- Add desired keywords as a Python dictionary in the settings.py file
- Add new CSS highlighting in publications.css in the format .highlighted(your_keyword)

## MIT License


Copyright (c) 2020 The EdTech Hub

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
