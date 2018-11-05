# Ported for python 3
For python 2 [USE THIS ONE](https://github.com/mohsinister/movie-meta-fetch/tree/Mohsin)

# Movie Metadata fetch
Fetch metadata of your movies easily with this script and save them in a html file to view/search for movies according to genre, actors, imdb rating. 


### How to use?
* Sign Up on omdabpi.com and get apikey.
* Replace XXXX with the api key in line 6 in main.py where omdbapiKey = 'XXXX'
* Sign up on themoviedb.org and get apikey.
* Replace XXXXXXXX woth the api key in line 7 in main.py where tmdbKey = 'XXXXXXXXXXX'
* Run the python file, feed in the directory where all your movies are listed and kaboom! You will get a txt file with json data of all details related to the movie. Upload the *content.txt* and *index.html* in the same folder to view your movie metadata online. For the movie folders/files it coulnd't process it will add the details to the ERRORLOG file.

### How does it work?
This script will work for almost everyone, I made it for my personal use and I have a habit of keeping my folders tidy. Generally all the movie files/folder are saved in this format *MOVIE NAME [YEAR] (1080p) (YTS.AM)*, or *MOVIE.NAME.Year.1080p.YTS.AM.mp4/mkv*, or *Movie.Name* would do.
Eg. of dummy folder
[Screenshot of Dummy Movie Folder](http://i.imgur.com/6NcRoiQ.png)

### What details will it fetch?
*   Name
*   Year
*   Time (mins)
*   Rating
*   Metascore
*   Plot
*   Genre
*   Actors

### Technical Details
Gets all the meta data from [OMDB API](http://www.omdbapi.com/)
