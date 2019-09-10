# kodi-snips-remote
# Controll kodi via snips
With this script you can control Kodi via Snips. You can control the player, start or search for movies, shows and music, open different windows of the Kodi gui or use the Kodi navigaton loop. This will start a Snips session automaticaly when the old session ends. The Snips hotword is now not necessary for a faster navigation through the Kodi gui. It is also possible to say only a part of the title and the script will search and display the result in the kodi gui, for all titles in the kodi library that contains the said word. The script checks if Kodi is reachable. When Snips detects the Hotword the Kodi player pauses so that you don't have to scream louder as the  mediasound while talking to Snips. When the Snips session ends the Kodi mediaplayer will return to the previous state unless you told to stop, pause or play something else.

# Functions:
* Entities Injection to get the titles from Kodi media-library in the Snips assistant
* Play show
* Play movie
* Search for shows and display results in gui 
* Search for movies and display results in gui

  
# Snips config
For the script the following Snips-apps with slots are used:
* synchronisation:
  * hey Snips synchronise library
* play_movie:
  * hey Snips start the movie iron man(slot)
  * add the select_movie intent in case multiple titles will be found e.g. iron man 1, iron man 2, iron man 3
  * slotname: movies
  * slotvalue:  -filled from injection
* select_movie:
  * iron man 3(slot)
  * this intent will only work if the session is keept alive with the customData "media_selected" when multiple movie titles are found. so it is possible to only say the movie name without hey Snips hotword.
  * slotname: movies
  * slotvalue:  -filled from injection
* play_show:
  * hey Snips play the show marvels iron fist(slot), hey Snips play a random(slot) episode of futurama(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
  * slotname: random
  * slotvalue: random +synonyms
* select_show:
  * marvels iron fist, marvels luke cake....
  * this intent will only work if the session is keept alive with the customData "media_selected" when multiple shows are found. so it is possible to only say the show name without hey Snips hotword.
  * slotname: shows
  * slotvalue:  -filled from injection
* search_show:
  * hey Snips search show marvel(slot)
  * slotname: shows
  * slotvalue:  -filled from injection
* search_movie:
  * hey Snips search movie spider(slot)
  * slotname: movies
  * slotvalue:  -filled from injection

# install

The Snips entities injection must be installed. https://docs.snips.ai/articles/advanced/dynamic-vocabulary

In kodi you must enable HTTP control: Settings/Services/Control > Allow remote control via HTTP must be enabled. Choose a 
Username, Password and Port

Change following values in the snips_remote.py:
* Kodi Username, Password, IP, Port
* MQTT server IP and Port
* Snips username 

To start the scrip run the snips_remote.py
