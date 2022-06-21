# Ported for python 3
For python 2 [USE THIS ONE](https://github.com/mohsinister/movie-meta-fetch/tree/Mohsin)

# Movie Metadata fetch
Fetch metadata of your movies easily with this script and save them in a html file to view/search for movies according to genre, actors, imdb rating. 


### How to use?
* Sign Up on omdabpi.com and get apikey.
* Replace XXXX with the api key in main.py where omdbapiKey = 'XXXX'
* Sign up on themoviedb.org and get apikey.
* Replace XXXX with the api key in main.py where tmdbKey = 'XXXX'
* Replace XXXX with your trak.tv username where trakTvUser = 'XXXX'
* For traktv api key go to [APP](https://trakt.tv/oauth/applications) and create an application. It is not rocket science.
* Replace XXXX where trakTvKey = 'XXXX'
* Next go to [Trakt API](https://trakt.docs.apiary.io) read the documentation on how to use the api. In this version, I am only using GET requests so authorization is not necessary.
* Run the python file, feed in the directory where all your movies are listed and kaboom! You will get a txt file with json data of all details related to the movie. Upload the *content.txt* and *index.html* in the same folder to view your movie metadata online. For the movie folders/files it coulnd't process it will add the details to the ERRORLOG file.
* Run localhost server through python/tomcat/xampp etc to open the html, don't open directly as browsers don't allow this anymore.

### How does it work?
This script will work for almost everyone, I made it for my personal use and I have a habit of keeping my folders tidy. Generally all the movie files/folder are saved in this format *MOVIE NAME [YEAR] (1080p) (YTS.AM)*, or *MOVIE.NAME.Year.1080p.YTS.AM.mp4/mkv*, or *Movie.Name* would do.
Eg. of dummy folder
[Screenshot of Dummy Movie Folder](http://i.imgur.com/6NcRoiQ.png)

To keep track of the movies you have watched, you can either manually mark them on Trakt or use this [3rd Party Service](https://www.thenerdystudent.com/2020/05/vlc-trakt-scrobble/) to automatically mark it as watched on Trakt.

### What details will it fetch?
*   Name (with trailer from youtube)
*   Year
*   Time (mins)
*   IMDB Rating
*   Metascore
*   Plot
*   Genre
*   Actors
*   Watched Status (from Trakt)

### Technical Details
Gets all the meta data from [OMDB API](http://www.omdbapi.com/)

### ToDo
*   Someone make the Html pretty.
