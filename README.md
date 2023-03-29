# Stat_Alert Twitter Bot Project
#### Thomas Cannon

[Stat_Alert Account](https://twitter.com/stat_alert)

### Aim
This repository contains the code used to scrape recent football match data from [Understat.com](https://understat.com/) and analyse the data to create 
visualisations of shots and xG which are then posted to a twitter account known as stat_alert using Python script.
### Requirements
* Python
* Pandas 
* Numpy
* Requests
* Beautifulsoup4
* Matplotlib
* Tweepy

### Usage
Run the hub.py file to scrape the recent match data from FBREF and create visualisations of shots and xG.  
The generated visualisations will be saved in the images folder.  
The images will be posted to the Twitter account.

## Examples taken from Saint-Etienne 0-1 Nantes (December 22 2021)

[Original Tweet](https://twitter.com/stat_alert/status/1639425431379271682)

#### Example Shotmap Output
![Alt text](https://github.com/TCannonx/stat_alert/blob/main/Examples/Saint-Etienne_shotmap.png "Example Shotmap Output")

#### Example Player Stats Output
![Alt text](https://github.com/TCannonx/stat_alert/blob/main/Examples/Saint-Etienne.png "Example Player Stats Output")
