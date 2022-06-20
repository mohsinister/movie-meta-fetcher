#!/usr/bin/env python3
import os
import requests
import json
import re
from youtube_search import YoutubeSearch
from pathlib import Path

omdbapiKey = 'XXXX'
tmdbKey = 'XXXX'
trakTvKey = 'YYYY'
trakTvUser = 'ZZZZ'
finaljson = ''
def dataSetter(json1):
    headers = {'trakt-api-version': '2','trakt-api-key': trakTvKey}
    movieTitle = "<a href='"+trailer+"' target='_blank'>"+moviename+"</a>"
    movieYear = ''
    movieRuntime = ''
    movieGenre = ''
    moviePlot = ''
    movieMeta = ''
    movieImdb = ''
    movieActors = ''
    movieWatched = ''
    if json1['Runtime'] == "N/A":
        movieRuntime = "0"
    if json1['Year']:
        movieYear = json1['Year']
        movieYear= str(movieYear).replace('"','\\"')
    if (json1['Runtime']):
        movieRuntime = json1['Runtime']
        movieRuntime= str(movieRuntime).replace('"','\\"')
    if json1['Genre']:
        movieGenre = json1['Genre']
        movieGenre= str(movieGenre).replace('"','\\"')
    if json1['Plot']:
        moviePlot = json1['Plot']
        moviePlot= str(moviePlot).replace('"','\\"')
    if json1['Metascore'] == "N/A":
        movieMeta = 0
    elif json1['Metascore']:
        movieMeta = json1['Metascore']
        movieMeta= str(movieMeta).replace('"','\\"')
    if json1['imdbRating'] == "N/A":
        movieImdb = 0
    elif json1['imdbRating']:
        movieImdb = json1['imdbRating']
        imdbID = json1['imdbID'].replace('"','\\"')
        url = 'https://api.trakt.tv/users/{0}/history/movies/{1}'.format(trakTvUser,imdbID)
        fetchedDetails = requests.get(url,headers=headers)
        details = fetchedDetails.content
        jsonTrakTv = json.loads(details)
        if len(jsonTrakTv)>0:
            movieWatched = 'Yes'
        else:
            movieWatched = 'No'
        imdbID = "https://www.imdb.com/title/"+imdbID
        movieImdb = str(movieImdb).replace('"','\\"')
        movieImdb = "<a href='"+imdbID+"' target='_blank'>"+movieImdb+"</a>"
    if json1['Actors']:
        movieActors = json1['Actors']
        movieActors = str(movieActors).replace('"','\\"')
    print (originalfile + " was successful")
    jsonpart = '\t\t\t["{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"]'.format(counter,movieTitle, movieYear, movieRuntime, movieImdb, movieMeta, moviePlot, movieGenre, movieActors, movieWatched)
    if counter != totalmovies:
        global finaljson
        finaljson = ''.join([finaljson, jsonpart, " , \n"])
    else:
        finaljson = ''.join([finaljson, jsonpart])
    return finaljson
currentDir = os.getcwd()
my_file = Path(currentDir + "/content.json")
oldjson = ""
if my_file.is_file():
    fr = open("content.json", "r")
    oldjson = fr.read()
    fr.close()
print ("Your current directory is : ")
print (currentDir)

#flag = input("Is this where your movies are? (y/n): ")

#if(flag=="n"):
#    currentDir = input("Please input the full address to your directory where movies are.\nDir:\t")

dirs = sorted(os.listdir(currentDir))
print (dirs)
totalmovies = len(dirs)
if "main.py" in dirs:
	totalmovies = totalmovies-1
if "index.html" in dirs:
	totalmovies = totalmovies-1
if "ERRORLOG" in dirs:
	totalmovies = totalmovies-1
if "content.json" in dirs:
	totalmovies = totalmovies-1
print ("Total: {}".format(totalmovies))
counter = 0
errorflag = 0
finaljson = "{\n\t\"data\": \n\t\t[\n"
errorfile = open("ERRORLOG", "w")
for filename in dirs:
    if filename != 'main.py' and filename!='content.json' and filename!='index.html' and filename!='ERRORLOG':
        originalfile = filename
        filename = filename.replace("(", "")
        filename = filename.replace(")", "")
        filename = filename.replace("[", "")
        filename = filename.replace("]", "")
        filename = filename.replace("+", "")
        filename = filename.replace("1080p", "")
        filename = filename.replace("BluRay","")
        filename = filename.replace("720p", "")
        filename = filename.replace("HDRiP", "")
        filename = filename.replace("WEBRip", "")
        filename = filename.replace("BRRip", "")
        filename = filename.replace(".mp4", "")
        filename = filename.replace(".flv", "")
        filename = filename.replace(".avi", "")
        filename = filename.replace(".mkv", "")
        filename = filename.replace(".txt", "")
        filename = filename.replace("YTS.AG", "")
        filename = filename.replace("YTS.AM", "")
        filename = filename.replace("YTS-AG", "")
        filename = filename.replace("YTS-AM", "")
        filename = filename.replace("."," ")
        years= re.findall('(\d{4})', filename)
        if len(years) > 0:
            moviename = filename[0:filename.find(years[0])]
            moviename = moviename.replace("."," ")
            moviename = moviename.rstrip()
            results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
            test = json.loads(results)
            try:
                trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
            except IndexError:
                trailer = "null"
            url = 'http://www.omdbapi.com/?apikey={0}&t={1}&y={2}'.format(omdbapiKey,moviename, years[0])
        else:
            moviename = filename.replace("."," ")
            moviename = moviename.rstrip()
            results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
            test = json.loads(results)
            try:
                trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
            except IndexError:
                trailer = "null"
            url = 'http://www.omdbapi.com/?apikey={0}&t={1}'.format(omdbapiKey,moviename)
        counter = counter + 1
        if oldjson.find('>'+moviename)>0:
            strTest = oldjson.split('>'+moviename,1)
            strO = strTest[0].rfind("<a")
            strP = strTest[1].split(']',1)
            strQ = strTest[0][strO:]+'>'+moviename+strP[0][0:]
            print (moviename+ ' was found in local file.')
            #print(strQ)
            #strName = '\t\t\t["{0}","{1}]'.format(counter,strO:oldjson.find("]",oldjson.find(moviename))])
            jsonpart = '\t\t\t["{0}","{1}]'.format(counter,strQ)
            finaljson = ''.join([finaljson, jsonpart, " , \n"])

        else:
            fetchedDetails = requests.get(url)
            details = fetchedDetails.content
            if trailer == "null":
               results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
               test = json.loads(results)
               try:
                   trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
               except IndexError:
                   trailer = "null"
            json1 = json.loads(details)
            if json1['Response'] == "False":
                if trailer == "null":
                   results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
                   test = json.loads(results)
                   try:
                        trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
                   except IndexError:
                        trailer = "null"
                url = 'https://api.themoviedb.org/3/search/movie?query={0}&api_key={1}'.format(moviename,tmdbKey )
                fetchedDetails = requests.get(url)
                details = fetchedDetails.content
                json2 = json.loads(details)
                if json2['total_results'] > 0:
                    if trailer== "null":
                       results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
                       test = json.loads(results)
                       try:
                            trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
                       except IndexError:
                            trailer = "null"
                    tmdbID = json2['results'][0]['id']
                    url = 'https://api.themoviedb.org/3/movie/{0}?&api_key={1}'.format(tmdbID,tmdbKey )
                    fetchedDetails = requests.get(url)
                    details = fetchedDetails.content
                    json2 = json.loads(details)
                    imdbID = json2['imdb_id']
                    if imdbID != "":
                        if trailer == "null":
                           results = YoutubeSearch(moviename +'Trailer', max_results=1).to_json()
                           test = json.loads(results)
                           try:
                               trailer = "https://www.youtube.com/watch?v=" + test['videos'][0]['id']
                           except IndexError:
                               trailer = "null"
                        url = 'http://www.omdbapi.com/?apikey={0}&i={1}'.format(omdbapiKey,imdbID)
                        fetchedDetails = requests.get(url)
                        details = fetchedDetails.content
                        json2 = json.loads(details)
                        finaljson = dataSetter(json2)
                    else:
                        errorflag = 1
                        errorfile.write(originalfile + " -- API Error : " + json1['Error'] + " URL : " + url + "\n")
                else: 
                    errorflag = 1
                    errorfile.write(originalfile + " -- API Error : " + json1['Error'] + " URL : " + url + "\n")
            else:
                finaljson = dataSetter(json1)
finaljson = finaljson.rstrip(", \n")
finaljson = ''.join([finaljson, "\n\t\t]\n}"])
fh = open("content.json", "w", encoding='utf-8')
fh.write(finaljson)
fh.close()
errorfile.close()
print("****************")
closer = input("Done, press Enter")
