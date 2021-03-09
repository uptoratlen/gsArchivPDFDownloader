# gsArchivPDFDownloader

## Table of contents
- [Overview](#Overview) 
  * [Exclusion](#Exclusion)
- [Technologies](#technologies)
- [Setup](#setup)
- [Run](#run)
- [Remarks](#remarks)
- [FAQ](#faq)

## Overview
As a user of "Gamerstar Plus" I got access to the archive of pdfs.
This is part of the subscription. 
There is the option to download the previous and current editions from 1997 to current day.
But there is one gap, you can't download them in one job. You need to open each edition and then save it.
Even as I got (most) of the editions in paper, I wanted to get them all as pdf.
That is where **gsArchivPDFDownloader** comes in. It will connect with your credentials (yes, you still need a subscription, this is automation not "(G)amestar (t)heft (a)utomation ...)
open all editions from 1998 to 2020 and download them to a selectable folder.

### Demo Video
Check this small demo Video: 
[Demo Video](http://www.kastaban.de/demo_mp4/gsArchivePDFDownloader.mp4 "Demo Video")
The video shows what the start should look like, than the start of the task. In this sample there are already some previous downloaded file. It will skip 1998/1 to 1998/6, than it will download 1998/7. Skip 8/1998 as also previously downloaded. Download 9/1998 and skip again 10/1998. The job was stopped for demo after 1/1999 and finally a tree is displayed. This is what the years should look like in the very end.

### Exclusion
There are three exclusions:
* No download for 1997 (as there are only 4) - I did it manually, aka too lazy to add code for this
* No download for 2021 (as there are only 4) - I did it manually, aka too lazy to add code for this
* No download for the 2013/13 edition (was a 13th edition in that year to overcome the existing gap that the 12th edition was about to be published in October of each year, because of a slight date change over time) - I did it manually,aka too lazy to add code for this
* The edition of 2017/10 is not downloading - eh don't blame me, even manualy the option is not set for download all (date 09 March 2021) - I think I contacted GS on that.


## Technologies
The gsArchivPDFDownloader obviously was created in Python with Selenium and the geckodriver(firefox).
geckodriver was not particular selected because of a certain feature, but because I use Firefox anyway.

For users with less experience, basically what it does:
Python opens a Firefox browser with a new profile (so you real one does not get altered) by the webdriver geckodriver (GeckoDriver is the link between Selenium and the Firefox browser), and than it simulates browser actions like a user does. Selenium is mostly used to automate tests of web applications.

As I expect that the webpage may be altered by some time, I guess later the automation will fail.
```
* The job ran successful with webpages at 6th March 2021.
* Python 3.7.3 (also 3.9.2 also worked)
* Selenium was version 3.141.0
* geckodriver 0.29.0 (cf6956a5ec8e 2021-01-14 10:31 +0200)
* Firefox 86.0(64-bit)
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
Click on "Code" (green button on top), than select "Download ZIP"
Extract the Content to some writeable folder. Eg. \gsDownloader\gsArchivePDFDownloader 
```
* Get geckodriver(.exe) as zip from 
https://github.com/mozilla/geckodriver/releases, extract the geckodriver.exe
and place it in the same folder as the gsArchivPDFDownloader.py
* Edit gs.json
```
[
    {
        "user": "<edit your username here>",
        "password": "<edit your password here>",
        "downloadtarget": "c:\\download\\Gamestar-archive"
    }
]
```
in user add the GameStar useraccount, in password your password. Simply the same info as you type in on the GameStar Page to login to your account.
on the downloadtarget please mask all "\\" with a additional leading "\\", so a path like "c:\\download\\Gamestar-archive" will look like "c:\\\\download\\\\Gamestar-archive".

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

## Remarks
As I used it one time, there is of course plenty of room for improvements.
It did the job once, and it saved me some time (compared to manual download).But it's far from being perfect or errorfree. On the other hand maybe someone finds this also useful and before it is forgotten on my disk I created this repo.


## FAQ
* Will it always work?  
  Well no, it depends on the webpage. In case the fields are renamed it will not work anymore. Taking in account that the basic function will stay the same, editing the names should not be a big issue.
  
* It not even download a single bit.  Did you edit the gs.json? Or It is broken already, sorry....drop me anote and I will a) fix or b)remove this :-)
* It will only download a fraction of the edition like a sample.  Well you may not enetered in gs.json the right credentials
* Hell, why you use simple sleeps?  Well...one time effort...lazy?...eh...I guess you are right, but it worked for me.....sorry.

* After some successful downloads the job stopped, what is this?  
  I assume this is caused by a timeout, which is not catched. Just restart the job, it will start from the beginning, but skips all already downloaded pdf.

* You mixed German and English in the logging?  
  Yes, as I said it was more a one timer. In case I got some time I may convert all to one language.
