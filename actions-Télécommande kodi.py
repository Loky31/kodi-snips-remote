#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import configparser
import io
import requests
import kodi
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology.injection import InjectionRequestMessage, AddInjectionRequest, AddFromVanillaInjectionRequest

playing_state_old = 0
is_in_session=0
is_injecting=0

#snips username with ':' or '__' at the end
snipsuser = "Loky31:"

#kodi  login data
kodi_ip = '192.168.1.3'
kodi_user = ''
kodi_pw = ''
kodi_port = '80'


debuglevel = 2 # 0= snips subscriptions; 1= function call; 2= debugs; 3=higher debug

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {
            section: {
                option_name: option
                for option_name, option in self.items(section)
            }
            for section in self.sections()
        }

def ausgabe(text,mode=3):
    # 0= snips subscriptions; 1= function call; 2= debugs; 3=higher debug
    '''
    function name -mode= 1
    debugs -mode= >=2
     - kodi function -mode= 1
       -- snips subscription -mode= 0
    '''
    ausgabe=""
    if mode < 1:
        ausgabe = "   -- "
    if mode >= debuglevel:
        print(ausgabe + str(text))
    return
        
        
def build_tupel(json, filtervalue):
    #Build tupels and lists of json
    #ausgabe('build_tupel',1)
    json_data = json
    tupel = []
    for item in json_data:
        if item[filtervalue] != '' and item[filtervalue] != ' ':
            tupel = tupel + [item[filtervalue]]
    return tupel

def inject():
    #makes an injection for snips from the kodi library. Entities Injection must be installed
    #replaces all special chars with ' ' before inject.
    global is_injecting
    is_injecting = 1
    #ausgabe('inject',1)
    send={"operations": [["addFromVanilla",{"shows":[],"movies":[]}]]} #"shows":[],"movies":[],... are entitie names from snips
    tupel = build_tupel(kodi.get_movies(),'title')
    send['operations'][0][1]['movies'] = send['operations'][0][1]['movies']+tupel
    tupel = build_tupel(kodi.get_shows(),'title')
    send['operations'][0][1]['shows'] = send['operations'][0][1]['shows']+tupel
    tupel = build_tupel(kodi.get_genre(),'title')
    request= [
        AddFromVanillaInjectionRequest(send)
    ]
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.request_injection(request)
    #Hermes.publish("hermes/injection/perform",json.dumps(send))
    return

def search(slotvalue,slotname,json_d):
    #check if word is in titles of the kodi library. e.g. marvel will be in more than 1 title. if found it will display it in kodi
    #ausgabe("search",1)
    titles = kodi.find_title(slotvalue,json_d)
    if len(titles) ==0:
        start_session(session_type="notification", text="aucun média trouvé")
    elif len(titles) >=1:
        #ausgabe('slotname: '+slotname,2)
        if slotname == 'shows':
            mediatype = 'tvshows'
        elif slotname =='movies':
            mediatype = 'movies'
        kodi.open_gui("", mediatype, slotvalue,isfilter=1)
    return(titles)

def main_controller(slotvalue,slotname,id_slot_name,json_d,session_id,intent_filter,playlistid):
    
    '''
    serch id of title in json from kodi library. if id is found get episodes/songs ids, stop kodi, insert playlist, (shuffle playlist), play.
    if id not found: search(). if search finds only one(search "big bang" find "the big bang theroy"): main_controller with slotvalue=search() return.
    if found multiple (search "iron" find "iron man 1, iron man 2..." keep session alive and add media_selected to custom_data. 
    playlist size is limited to 20 items cause kodi keeps crashing while adding to much items
    
    slotvalue: the media title from snips e.g. Iron Man
    slotname: the name of the slot of the snips intent e.g. movies
    id_slot_name: the key value name of the media id from the kodi library json
    session_id: the snips session id
    intent_filter: the intents for new or keep alive snips sessions
    israndom: from snips if the media should played in random order e.g. hey snips play seinfeld in random order
    playlistid: the playlist id for kodi. 0=Music; 1=Movies; 2=Pictures
    '''
    global playing_state_old
    #ausgabe('main_controller',1)
    media_id_of_title_found = kodi.find_title_id(slotvalue,'label',id_slot_name,json_d)
    if media_id_of_title_found != 0:
        intent_filter=""
        if slotname =='shows':
            id_slot_name='episodeid'
            json_episodes = kodi.get_episodes_unseen(media_id_of_title_found)
            if json_episodes['limits']['total'] != 0:
                id_tupel = build_tupel(json_episodes['episodes'], id_slot_name)
            else:
                return "aucun épisode trouvé"
        elif slotname=='movies':
            id_tupel = [media_id_of_title_found]
        playing_state_old = 0
        #end_session(session_id, text="")
        kodi.stop()
        if playlistid == 1:
            kodi_navigation_gui("videoplaylist")
        elif playlistid == 0:
            kodi_navigation_gui("musicplaylist")
        kodi.insert_playlist(id_tupel,id_slot_name, playlistid)
        kodi.start_play(playlistid)
    else:
        titles = search(slotvalue,slotname,json_d)
        #ausgabe(titles)
        if len(titles) == 1:
            end_session(session_id, text="")
            main_controller(titles[0],slotname,id_slot_name,json_d,session_id,intent_filter,playlistid)
            return
        elif len(titles) > 1:
            keep_session_alive(session_id,text="okay. was?",intent_filter=intent_filter,customData="media_selected")            
    return
    
 
def intent_callback(hermes, intent_message):
    intent_name = intent_message.intent.intent_name.replace("Loky31:", "")
    result = None
    if intent_name == "play_show":
        main_controller(intent_message.slots.shows.first().value,shows,'tvshowid',kodi.get_shows(),session_id,intent_filter,playlistid)
        result = "Je lance {} sur Kodi".format(intent_message.slots.shows.first().value) 
    elif intent_name == "search_show":
        search(intent_message.slots.shows.first().value,shows,kodi.get_shows())
        result = "Je cherche {} sur Kodi".format(intent_message.slots.shows.first().value)
    elif intent_name == "search_movie":
        search(intent_message.slots.movies.first().value,movies,kodi.get_movies())
        result = "Je cherche {} sur Kodi".format(intent_message.slots.movies.first().value)
    elif intent_name == "play_movie":
        main_controller(intent_message.slots.movies.first().value,movies,'movieid',kodi.get_movies(),session_id,intent_filter,playlistid)
        result = "Je lance {} sur Kodi".format(intent_message.slots.movies.first().value)
    elif intent_name == "synchronisation":
        inject()
        result = "Je me synchronise avec Kodi" 
    if result is not None:
        hermes.publish_end_session(intent_message.session_id, result)


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intents(intent_callback).start()
       