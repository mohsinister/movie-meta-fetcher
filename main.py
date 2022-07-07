#!/usr/bin/env python3
import os
import requests
import PTN
import threading
import json
import re
from youtube_search import YoutubeSearch
from pathlib import Path
import unicodedata
import argparse
from dataclasses import dataclass
import queue
from typing import Dict, List

omdbapiKey = 'XXXX'
errorfile = open("ERRORLOG.txt", "w")
tmdbKey = 'XXXX'
trakTvKey = 'XXXX'
trakTvUser = 'XXXX'
headers = {'trakt-api-version': '2','trakt-api-key': trakTvKey}
parser = argparse.ArgumentParser(description='Commands to help with the script.')
group = parser.add_mutually_exclusive_group()
group.add_argument('-p','--purge',action='store_true',help='purge the content of json file.')
group.add_argument('-w','--watch',action='store_true',help='update watch status for movies from trakt.')
args = parser.parse_args()
oldjson=''
watchStatusList =[]
@dataclass
class ThreadRequests(object):
    urls: queue.Queue = queue.Queue()
    infos: queue.Queue = queue.Queue()

    def __init__(
        self,
        urls: List[str],
        http_method: str,
        nb_threads: int,
    ) -> None:
        """Put all urls to the queue url """
        self.nb_threads = nb_threads
        self.http_method = http_method
        self.workers = {"GET": self.worker_get, "Trakt": self.worker_trakt, "Watch": self.worker_watch}
        for url in urls:
            self.urls.put(url)
    @property
    def responses(self) -> List[Dict]:
        return list(self.infos.queue)

    def run(self) -> None:
        """ Run all workers"""
        for i in range(0, self.nb_threads):
            threading.Thread(target=self.workers[self.http_method], daemon=True).start()
        self.urls.join()

    def worker_get(self) -> None:
        global tmdbKey
        global omdbapiKey
        global headers
        global oldjson
        global errorfile
        movieName =''
        year = ''
        """Pull a url from the queue and make a get request to Ombd"""
        while not self.urls.empty():
            movie = self.urls.get()
            if '+' in movie:
                movie = movie.split('+',1)
                movieName = movie[0]
                year = movie[1]
                url = f"http://www.omdbapi.com/?apikey={omdbapiKey}&t={movieName}&y={year}"
            else:
                movieName = movie
                url = f"http://www.omdbapi.com/?apikey={omdbapiKey}&t={movieName}"
            if oldjson.find('>'+movieName)>0:                
                strTest = oldjson.split('>'+movieName,1)
                strO = strTest[0].rfind("<a")
                strP = strTest[1].split(']',1)
                strQ = strTest[0][strO:]+'>'+movieName+strP[0][0:]
                strImbdID = strQ.split("/title/",1)
                strImbdID = (strImbdID[1].split("'",1)[0])
                strQ = strQ.split('","')
                strQ[0] = strQ[0].split("watch?v=")[1].split("' target=")[0]
                strQ[3] = strQ[3].split('>',1)[1].split('<')[0]
                TraktID = strQ[8].split("/movies/",1)[1].split("' target=")[0]
                strQ[8] = strQ[8].split('>',1)[1].split('<')[0]
                jsont = f"""{{
                         "Title" : "{movieName}",
                         "YouTube" : "{strQ[0]}",
                         "Year" : "{strQ[1]}",
                         "Runtime" : "{strQ[2]}",
                         "imdbRating" : "{strQ[3]}",
                         "imdbID" : "{strImbdID}",
                         "Metascore" : "{strQ[4]}",
                         "Plot" : "{strQ[5]}",
                         "Genre" : "{strQ[6]}",
                         "Actors" : "{strQ[7]}",
                         "Trakt" : "{strQ[8]}",
                         "TraktID": "{TraktID}"}}"""
                
                makeJson = json.loads(jsont)
                self.infos.put(makeJson)
                self.urls.task_done()
            else:
                resp = requests.get(url)
                if resp.json()['Response'] != "False":
                    x=resp.json()
                    x["Title"] = movieName
                    results = YoutubeSearch(movieName +'Trailer' +x["Year"], max_results=1).to_json()
                    youtubeData = json.loads(results)
                    try:
                        x["YouTube"] = youtubeData['videos'][0]['id']
                    except IndexError:
                        trailer = "null"
                    
                    self.infos.put(x)
                    self.urls.task_done()
                else:
                    url = f"https://api.trakt.tv/search/movie?query={movieName}"
                    resp = requests.get(url, headers= headers)
                    if len(resp.json())>0:
                        imdbID = resp.json()[0]['movie']['ids']['imdb']
                    #print (imdbID)
                    #url = f"https://api.themoviedb.org/3/movie/{tmdbID}?&api_key={tmdbKey}"#format(tmdbID,tmdbKey )
                    #resp = requests.get(url)
                    #imdbID = resp.json()['imdb_id']
                        if imdbID != "":
                            url = f"http://www.omdbapi.com/?apikey={omdbapiKey}&i={imdbID}"#.format(omdbapiKey,imdbID)
                            resp = requests.get(url)
                            x=resp.json()
                            x["Title"] = movieName
                            results = YoutubeSearch(movieName +'Trailer' +x["Year"], max_results=1).to_json()
                            youtubeData = json.loads(results)
                            try:
                                x["YouTube"] = youtubeData['videos'][0]['id']
                            except IndexError:
                                trailer = "null"
                            self.infos.put(x)
                        else:
                            errorflag = 1
                            errorfile.write(movieName + " -- API Error : URL : " + url + "\n")
                    else:
                        errorflag = 1
                        errorfile.write(movieName + " -- API Error : URL : " + url + "\n")
                    self.urls.task_done()
    def worker_watch(self)-> None:
        global headers
        global oldjson
        global errorfile
        movieName =''
        year = ''
        while not self.urls.empty():
            movie = self.urls.get()
            if '+' in movie:
                movie = movie.split('+',1)
                movieName = movie[0]
                year = movie[1]
            else: movieName = movie
            if oldjson.find('>'+movieName)>0:                
                strTest = oldjson.split('>'+movieName,1)
                strO = strTest[0].rfind("<a")
                strP = strTest[1].split(']',1)
                strQ = strTest[0][strO:]+'>'+movieName+strP[0][0:]
                strImbdID = strQ.split("/title/",1)
                strImbdID = (strImbdID[1].split("'",1)[0])
                strQ = strQ.split('","')
                strQ[0] = strQ[0].split("watch?v=")[1].split("' target=")[0]
                strQ[3] = strQ[3].split('>',1)[1].split('<')[0]
                TraktID = strQ[8].split("/movies/",1)[1].split("' target=")[0]
                strQ[8] = strQ[8].split('>',1)[1].split('<')[0]
                if strQ[8] == 'No':
                    jsont = f"""{{
                            "Title" : "{movieName}",
                            "YouTube" : "{strQ[0]}",
                            "Year" : "{strQ[1]}",
                            "Runtime" : "{strQ[2]}",
                            "imdbRating" : "{strQ[3]}",
                            "imdbID" : "{strImbdID}",
                            "Metascore" : "{strQ[4]}",
                            "Plot" : "{strQ[5]}",
                            "Genre" : "{strQ[6]}",
                            "Actors" : "{strQ[7]}"}}"""
                else:
                    jsont = f"""{{
                         "Title" : "{movieName}",
                         "YouTube" : "{strQ[0]}",
                         "Year" : "{strQ[1]}",
                         "Runtime" : "{strQ[2]}",
                         "imdbRating" : "{strQ[3]}",
                         "imdbID" : "{strImbdID}",
                         "Metascore" : "{strQ[4]}",
                         "Plot" : "{strQ[5]}",
                         "Genre" : "{strQ[6]}",
                         "Actors" : "{strQ[7]}",
                         "Trakt" : "{strQ[8]}",
                         "TraktID": "{TraktID}"}}"""
                makeJson = json.loads(jsont)
                self.infos.put(makeJson)
            self.urls.task_done()
                
    def worker_trakt(self) -> None:
        global headers
        global trakTvUser
        """Pull a url from the queue and make a get request to Trakt"""
        while not self.urls.empty():
            imdbID = self.urls.get()
            url = f"https://api.trakt.tv/users/{trakTvUser}/history/movies/{imdbID}"
            resp = requests.get(url,headers=headers)
            if len(resp.json())>0:
                self.infos.put(resp.json())
                self.urls.task_done()
            else:
                url = 'https://api.trakt.tv/search/imdb/{0}'.format(imdbID)
                resp = requests.get(url,headers=headers)
                self.infos.put(resp.json())
                self.urls.task_done()


def getDirecotry():
    currentDir = os.getcwd()
    global oldjson
    my_file = Path(currentDir + "/content.json")
    if my_file.is_file():
        fr = open("content.json", "r")
        oldjson = fr.read()
        fr.close()
        print ("Your current directory is : ")
        print (currentDir)
        flag = input("Is this where your movies are? (y/n): ")
        if(flag=="n"):
            currentDir = input("Please input the full address to your directory where movies are.\nDir:\t")
        dirs = sorted(os.listdir(currentDir))
        return dirs

def totalMovies():
    totalmovies = len(dirs)
    if "main.py" in dirs:
        totalmovies = totalmovies-1
    if "index.html" in dirs:
        totalmovies = totalmovies-1
    if "ERRORLOG.txt" in dirs:
        totalmovies = totalmovies-1
    if "content.json" in dirs:
        totalmovies = totalmovies-1
    print ("Total: {}".format(totalmovies))
    return totalmovies

def sortDirectory(dirs):
    for filename in dirs:
        if filename != 'main.py' and filename!='content.json' and filename!='movies.ico' and filename!='.vs' and filename!='index.html' and filename!='ERRORLOG.txt':
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
            filename = filename.replace("YTS.MX", "")
            filename = filename.replace("YTS-AG", "")
            filename = filename.replace("YTS-AM", "")
            filename = filename.replace("x264", "")
            filename = filename.replace("x265", "")
            filename = filename.replace("."," ")
    return dirs



def simplify(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if unicodedata.category(c) != 'Mn')

def dataSetter(ombdData,watchStatusList):
    counter = 0
    finaljson = "{\n\t\"data\": \n\t\t[\n"
    movieYear = ''
    movieRuntime = ''
    movieGenre = ''
    moviePlot = ''
    movieMeta = ''
    movieImdb = ''
    movieActors = ''
    movieWatched = ''
    trailer = ''
    while not ombdData.empty():
        counter = counter +1
        json1 = ombdData.get()
        if json1.get('Title'):
            movieTitle = json1.get('Title')
            youtubeData = json1.get('YouTube')
            trailer = f"https://www.youtube.com/watch?v={youtubeData}"
            movieTitle = "<a href='"+trailer+"' target='_blank'>"+movieTitle+"</a>"
        if json1.get('Runtime') == "N/A":
            movieRuntime = "0"
        elif json1.get('Runtime'):
            movieRuntime = json1.get('Runtime')
            movieRuntime= str(movieRuntime).replace('"','\\"')
        if json1.get('Year'):
            movieYear = json1.get('Year')
            movieYear= str(movieYear).replace('"','\\"')
        if json1.get('Genre'):
            movieGenre = json1.get('Genre')
            movieGenre= str(movieGenre).replace('"','\\"')
        if json1.get('Plot'):
            moviePlot = json1.get('Plot')
            moviePlot = str(moviePlot).replace('"','\\"')
        if json1.get('Metascore') == "N/A":
            movieMeta = 0
        elif json1.get('Metascore'):
            movieMeta = json1.get('Metascore')
            movieMeta= str(movieMeta).replace('"','\\"')
        if json1.get('imdbRating') == "N/A":
            movieImdb = 0
        elif json1.get('imdbRating'):
            movieImdb = json1.get('imdbRating')
            imdbID = json1.get('imdbID').replace('"','\\"')
            try:
                if json1.get('Trakt') and json1.get('TraktID'):
                    traktStatus = json1.get('Trakt')
                    traktID = json1.get('TraktID')
                    movieWatched =f"<a href='https://trakt.tv/movies/{traktID}' target='_blank'>{traktStatus}</a>"
                else:
                    movieWatched = watchStatus(imdbID,watchStatusList)
                           
            except:
                print ('qqq')           
            imdbID = "https://www.imdb.com/title/"+imdbID
            movieImdb = str(movieImdb).replace('"','\\"')
            movieImdb = "<a href='"+imdbID+"' target='_blank'>"+movieImdb+"</a>"
        if json1.get('Actors'):
            movieActors = json1.get('Actors')
            movieActors = str(movieActors).replace('"','\\"')
        jsonpart = '\t["{}","{}","{}","{}","{}","{}","{}","{}","{}","{}"]'.format(counter,movieTitle, movieYear, movieRuntime, movieImdb, movieMeta, moviePlot, movieGenre, movieActors, movieWatched)
        finaljson = ''.join([finaljson, jsonpart, " , \n"])

    finaljson = finaljson.rstrip(", \n")
    finaljson = ''.join([finaljson, "\n\t\t]\n}"])
    finaljson = simplify(finaljson)
    fh = open("content.json", "w", encoding='utf-8')
    fh.write(finaljson)
    fh.close()
    errorfile.close()

def watchStatus(imdbID,traktData):
    traktDataStr = str(traktData)
    indexImbd = traktDataStr.find(imdbID)
    indexMovie = traktDataStr.count('[',0,indexImbd)
    if str(traktData[indexMovie-2][0]).find("movie")>0:
        if str(traktData[indexMovie-2][0]).find("watched_at")>0:
            movieWatched = traktData[indexMovie-2][0]["movie"]['ids']['slug']
            movieWatched = "<a href='https://trakt.tv/movies/"+movieWatched+"' target='_blank'>Yes</a>"
            return movieWatched
        else:
            movieWatched = traktData[indexMovie-2][0]["movie"]['ids']['slug']
            movieWatched = "<a href='https://trakt.tv/movies/"+movieWatched+"' target='_blank'>No</a>"
            return movieWatched
    else:
        movieWatched = 'No'
        return movieWatched
def sorter():
    urls = []
    filenames = []
    for i in range(len(dirs)):
        if (dirs[i] != 'main.py' and dirs[i]!='content.json' and dirs[i]!='movies.ico' and dirs[i]!='.vs' and
            dirs[i]!='nold.py' and dirs[i]!='index.html' and dirs[i]!='ERRORLOG.txt'):
            filenames.append(dirs[i])
    for filename in filenames:
        moviename = filename
        years= re.findall('(\d{4})', filename)
        if len(years) > 0:
            moviename = filename[0:filename.find(years[0])]
            moviename = PTN.parse(moviename)
            moviename = moviename['title']
            moviename = moviename.rstrip()
            year = years[0]
            urls.append (f"{moviename}+{year}")
        else:
            moviename = PTN.parse(moviename)
            moviename = moviename['title']
            moviename = moviename.rstrip()
            urls.append(moviename)
    return urls
if args.purge:
    fh = open("content.json", "w", encoding='utf-8')
    fh.write("{\n\t\"data\": \n\t\t[\n\t\t]\n}")
    fh.close()
    print("**FILE PURGED!**")
elif args.watch:
    dirs = getDirecotry()
    totalmovies = totalMovies()
    dirs = sortDirectory(dirs)
    filenames = []
    urls= sorter()
    client = ThreadRequests(urls, "Watch", nb_threads=50)
    client.run()
    jsonData = client.infos
    ombdData = queue.Queue()
    urlsTrakt= []
    finaljson =''
    sortedMovieDataList= (list(client.infos.queue))
    sortedMovieDataList.sort(key=lambda x: x['Title'], reverse=True)
    while not jsonData.empty():
        json1 = jsonData.get()
        sortedJSON = sortedMovieDataList.pop()
        ombdData.put(sortedJSON)
    unwatchedMovies = oldjson.split('\n')
    for i in range(len(unwatchedMovies)):
        if unwatchedMovies[i].find('>No</a>') > 0:
            strImbdID = unwatchedMovies[i].split("/title/",1)
            strImbdID = (strImbdID[1].split("'",1)[0])
            urlsTrakt.append(strImbdID)
    clientTrakt = ThreadRequests(urlsTrakt, "Trakt", nb_threads=50)
    clientTrakt.run()
    print ("Movies Watch Status Fetched")
    watchStatusList= (list(clientTrakt.infos.queue))
    dataSetter(ombdData,watchStatusList)
elif __name__ == "__main__":
    dirs = getDirecotry()
    totalmovies = totalMovies()
    dirs = sortDirectory(dirs)
    filenames = []
    urls= sorter()
       
    comments = [        f"https://jsonplaceholder.typicode.com/comments/{id_}" for id_ in range(1, 50)        ]
    client = ThreadRequests(urls, "GET", nb_threads=50)
    client.run()
    jsonData = client.infos
    ombdData = queue.Queue()
    urlsTrakt= []
    finaljson =''
    sortedMovieDataList= (list(client.infos.queue))
    sortedMovieDataList.sort(key=lambda x: x['Title'], reverse=True)
    print ("Movies Meta Fetched")
    while not jsonData.empty():
        json1 = jsonData.get()
        sortedJSON = sortedMovieDataList.pop()
        ombdData.put(sortedJSON)
        try:
            if not json1.get('Trakt'):
                movieImdb = json1.get('imdbRating')
                imdbID = json1.get('imdbID').replace('"','\\"')
                urlsTrakt.append(imdbID)
        except:
            print ('zzzz')

    clientTrakt = ThreadRequests(urlsTrakt, "Trakt", nb_threads=50)
    clientTrakt.run()
    print ("Movies Watch Status Fetched")
    watchStatusList= (list(clientTrakt.infos.queue))
    dataSetter(ombdData,watchStatusList)
    
    
    


