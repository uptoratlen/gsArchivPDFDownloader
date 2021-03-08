# gsArchivPDFDownloader

## Table of contents
- [General info](#General-info) 
  * [Exclusion](#Exclusion)
- [Technologies](#technologies)
- [Setup](#setup)
- [Run](#run)

## General info
As a user of "Gamerstar Plus" I got access to the archive of pdfs.
This is part of the subscription. 
There is the option to download the previous and current editions from 1997 to current day.
But there is one gap, you can't download them in one job. You need to open each edition and then save it.
Even as I got (most) of the editions in paper, I wanted to get them all as pdf.
So this is gsArchivPDFDownloader for. It will connect with your credentials (yes, you still need a subscription, this is automation not theft...)
open all editions from 1998 to 2020 and download them to a selectable folder.

###Exclusion
There are three exclusions:
* No download for 1997 (as there are only 4) - I did it manually
* No download for 2021 (as there are only 4) - I did it manually
* No download for the 2013/13 edition (was a 13th edition in that year to overcome the existing gap that the 12th edition was about to be published in October of each year, because of a slight date change over time) - I did it manually



## Technologies
The gsArchivPDFDownloader obviously was created in Python with Selenium and the geckodriver(firefox).
geckodriver was not particular selected because of a certain feature, but because I use Firefox anyway.

As I expect that the webpage may be altered by some time, I guess later the automation will fail.
```
* The job ran successful with webpages at 6th March 2021.
* Python 3.7.3 (also 3.9.2 also worked)
* Selenium was version 3.141.0
* geckodriver 0.29.0 (cf6956a5ec8e 2021-01-14 10:31 +0200)
* hosting OS was Windows 10 (20H2)
```

## Setup
* Install obviously python (assuming default settings)
* install with pip selenium
```
pip install selenium
```
* Get gsArchivPDFDownloader.py and gs.json from this repository
```
git clone https://github.com/uptoratlen/gsArchivPDFDownloader
```
* Get geckodriver from 
https://github.com/mozilla/geckodriver/releases
and place it in the same folder as the gsArchivPDFDownloader.py
* Edit gs.json
```
[
    {
        "user": "<edit your username here>",
        "password": "<edit your password here>",
        "downloadtarget": "s:\GS"
    }
]
```

on the downloadtarget please mask all "\\" with a leading "\\", so a path like "c:\\download\\Gamestar-archive" will look like "c:\\\\download\\\\Gamestar-archive".

## Run
To start a download job open a cmd and type
```
python gsArchivPDFDownloader.py
```

Now the job will start, it will check and create the "downloadtarget" folder.
It will open a firefox/geckodriver browser, login and open the URL for the archive.
Than it will save the file. After the download is complete (no *.part is seen anymore), the new file is moved to a sub folder of the year.
In other words the structure of the sample will look like
```

C:
  |
  +--download
            |
            +--Gamestar-archive
                              |
                              +1998  <-- all editions of that year
                              +1999  <-- all editions of that year
                              +2000  <-- all editions of that year
                              +...         
```
