### Timehut Scrapy version 1.0
##### Purpose
Using Selenium to automatically scrap the data from the website.

##### Prerequisite
- Selenium
- RabbitMQ

##### Status
There's something wrong with the website that prevent selenium to load all the collection. Right now is somewhat falling in the middle of the scrapying progress

--- 
### Timehut Scrapy version 2.0
##### Purpose
As right now scrapying from the website doesn't really work smoothly, trying another way to fetch the data via the timehut mobile app

##### Prerequisite
- mitmproxy
- RabbitMQ

##### Description
- Use mitmproxy to collect the collection id/information from the request
- Fire one moment request to fetch the header used in the moment request
- Apply those collection_id and the header captured to fire all the request to fetch the moment information

##### Execution
1. sudo rabbitmq-server
2. Run timehutQueueConsumer.py
3. Run mitmproxy -p 8080 -s [script_name]
4. or mitmweb -s [script_name]
5. Need to reinstall the app and relogin
6. Tab one of the moment to fetch all moments