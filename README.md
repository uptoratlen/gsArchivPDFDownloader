# gsArchivPDFDownloader

## Table of contents
- [Overview](#overview)
  * [Demo Video](#demo-video)
  * [Exclusion](#exclusion)
- [Technologies](#technologies)
- [Setup](#setup)
- [Edit gs_credential.json](#edit-gs_credentialjson)
- [Edit gs.json](#edit-gsjson)
  * [Filenamepattern in gs.json](#filenamepattern-in-gsjson)
  * [editions in gs.json](#editions-in-gsjson)
- [Run](#run)
  * [based on gs.json](#based-on-gsjson)
  * [commandline argument](#commandline-argument)
    + [--year](#--year)
    + [--latest](#--latest)
- [Remarks](#remarks)
- [FAQ](#faq)

## Overview
As a user of "Gamerstar Plus" I got access to the archive of pdfs.
This is part of the subscription. 
There is the option to download the previous and current editions from 1997 to current day.
But there is one gap, you can't download them in one job. You need to open each edition and then save it.
Even as I got (most) of the editions in paper, I wanted to get them all as pdf.
That is where **gsArchivPDFDownloader** comes in. It will connect with your credentials (yes, you still need a subscription, this is automation not "(G)amestar (t)heft (a)utomation ...)
open all editions from 1997/9 to 2021/3 and download them to a selectable folder.
```
Info: Important change - since 0.5.6 a new gs_credential.json was created
```

### Demo Video
Check this small demo Video: 
Video shows Version 0.1 - current solution works similar, with a bit different logging  
[Demo Video](http://www.kastaban.de/demo_mp4/gsArchivePDFDownloader.mp4 "Demo Video")  
The video displays what the start of the program would look like, than the start of the download. In this sample there are already some previous downloaded file. It will skip 1998/1 to 1998/6, than it will download 1998/7. Skip 8/1998 as also previously downloaded. Download 9/1998 and skip again 10/1998. The job was stopped for demo after 1/1999 and finally a tree is displayed. This is what the years should look like in the very end.

### Exclusion
* Since v0.2 and v0.3 there is none of the exception existing anymore. The user is now in full control of what requested download are part of the job.
* The edition 2017/10 is still a exception: Caused by a error in "Blättercatalog"  
(thx to thomas-k for motivation): A waring will be displayed in case you try to download this edition  
  (09 March 2021) - I contacted GS on that.   
  (12 March 2021) - the edition is downloadable as a ZIP,but not from blätterkatalog which uses the program  
  (28 April 2021) - Even worse the Blätterkatalog does not even display the edition anymore.....
  
## Technologies
The gsArchivPDFDownloader obviously was created in Python with Selenium and the geckodriver(firefox).
geckodriver was not particular selected because of a certain feature needed, but because I use Firefox anyway.

For users with less experience, basically what it does:
Python opens a Firefox browser with a new profile (so your real one does not get altered) by the webdriver geckodriver (GeckoDriver is the link between Selenium and the Firefox browser), and than it simulates browser actions like a user does. Selenium is mostly used to automate tests of web applications.

As I expect that the webpage may be altered by some time, I guess later the automation will fail. The program is to some extent configurable for this case. 
First use (env)
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

## Edit gs_credential.json
This is a not working sample ! - Get the real one from code or release page.

```
[
  {
        "user":"<edit_your_username_here>",
        "password":"<edit_your_password_here>"
  }
]
```
| Name          | value allowed        | Remark|introduced/removed
|:---|:---:|:---|:---:|
| user      | string | your gs user name | v0.1|
| password      | string   | your gs user password | v0.1|


## Edit gs.json
This is a not working sample ! - Get the real one from code or release page.

```
[
    {
        "log_level": "INFO",
        "downloadtarget": "c:\\download\\Gamestar-archive",
        "edition2d": "No",
        "downloadtimeout": 240,
        "abortlimit": 2,        
        "filenamepattern_intarget": "GameStar Nr. <ausgabe>_<jahr>.pdf",
        "filenamepattern_fromserver": "GameStar Nr. <ausgabe>_<jahr>.pdf"
        "latestdownload": [
            {
                "year": 2021,
                "edition": "3"
            }
        ],
        "browser_display_on_latest": "no",        
        "editions":[
         {
            "1997":"9,10,11,12"
         },
         {
            "1998":"1,2,3,4,5,6,7,8,9,10,11,12"
         },
         .......
         {
            "2013":"1,2,3,4,5,6,7,8,9,10,11,12,13"
         },
         .......
         {
            "2017":"1,2,3,4,5,6,7,8,9,11,12,13"
         },
         .......         
         {
            "2020":"1,2,3,4,5,6,7,8,9,10,11,12"
         },
         {
            "2021":"1,2,3,4"
         }
      ]        
    }
]
```
| Name          | value allowed        | Remark|introduced/removed
|:---|:---:|:---|:---:|
| ~~user~~      | string | moved to extra file since v0.5.6; ~~your gs user name~~ | ~~v0.1~~/v0.5.6|
| ~~password~~      | string   | moved to extra file since v0.5.6; ~~your gs user password~~ | ~~v0.1~~/v0.5.6|
| log_level      | [debug/info/warning/error/critical]   | The loglevel just in case needed - info is default, debug is fallback | v0.5|
| downloadtarget | string   | please mask all "\\" with a additional leading "\\", so a path like "c:\\download\\Gamestar-archive" will look like "c:\\\\download\\\\Gamestar-archive". | v0.1|
| edition2d | [Yes/No] | "No" will use the edition from the server like 1,2,3,4,5; "Yes" will create edition names like "01,02,03,04,05..." | v0.2|
| ~~skip20yearedition~~ | deprecated  | not used anymore since V0.3; see ["editions"](#editions-in-gsjson) for more info | ~~v0.2~~/v0.3|
| downloadtimeout | int | Time in seconds the download wait for a download before trying to download the next edition. This is a max timer, in case the edition is completed before that time it will not wait until the max time. Currently only successful downloads will be moved to target | v0.1|
| abortlimit | int | default 2; In case a "-year" run is selected and 'abortlimit' edition in sequence are not found the run will be aborted. A new success after a failed download will reset the counter.   | v0.5.6|
| browser_display_on_latest | [Yes/No]  | In case the commandline option --latest or -l thi soption allow a hidden browser on value "no", "yes" will display the browser also on this commandline option  | v0.5|
| latestdownload | list] | in case the commandline option --latest/-l is used this will be updated with the latest downloaded edition, so the next run (month) will start from that edition the copy; see ["latest"](#--latest)  | v0.5|



### Filenamepattern in gs.json
| Name          | value allowed        | Remark|
|:---|:---:|:---|
| filenamepattern_intarget      | string | The downloaded file will be moved with that name to the downloadtarget folder |
| filenamepattern_fromserver      | string   | That is the file we get after we click on the "alle" button in "blätterkatalog" |  

Basic idea: The filename pattern is read from file and than the strings "\<ausgabe\>" and "\<jahr\>" are replaced by the current proceeded values.

So you do not like the naming of the files? You want to honor GS? You need a file name like: "Tolle GameStar Nr. aus dem Jahr 1997 mit Ausgabe 9.pdf"
than alter the "filenamepattern_intarget" to ```"filenamepattern_intarget": "Tolle GameStar Nr. aus dem Jahr <jahr> mit Ausgabe <ausgabe>.pdf"```
or simpler you want a filename like "GameStar 1997-9.pdf" than use "filenamepattern_intarget" to ```"filenamepattern_intarget": "GameStar <jahr>-<ausgabe>.pdf"```

I found out during the creation of v0.2 that the server changed the naming. They moved from "GameStar_Nr._9_1997.pdf"  to  "GameStar Nr. 9_1997". Mind the small change in use of the "\_"
To overcome this small but maybe annoying thing (maybe "they" did not like my downloader, or it was Shodan, GLaDOS...), I added also here a way to get the right URL.
As mentioned in the start and end, if "they" change fundamental things, upsi....it will not work anymore.
With that we could try a small fix.

### editions in gs.json
| Name          | value allowed        | Remark|
|:---|:---:|:---|
| editions      | string   | a list of each year request to download with a comma separated value; no spaces,no leading 0|

Example a list like (for documentation I removed the rest of the json)
```
[
    {
    "editions":[
         {
            "1997":"9,10"
         },
         {
            "2006":"4,6,7,10"
         },
         {
            "2013":"13"
         },
         {
            "2021":"1,2,3,4"
         }
      ]        
    }
]
```
This list would download 1997 editions 9 and 10; from 206 the editions 4,6,7,10; from 2013 only 13 and from 2021 the editons 1 to 4.

Attention:  
_If you create a list like ```"2035":"4,5,6"``` you will need a time-machine, as the year **2035** is not yet reached and the editions **4,5,6** do really not exist by now....  
In other words, **the script does not check of any misconfiguration or meaningless values**._

## Run 
### based on gs.json
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
                              +1997  <-- all editions of that year (4)
                              +1998  <-- all editions of that year (12)
                              +1999  <-- all editions of that year (12)
                              +2000  <-- all editions of that year (12)
                              +...         
```
The requested editions are stored in the gs.json ``` "editions" ```

### commandline argument
```
usage: gsArchivPDFDownloader.py [-h] [-y YEAR]

Download a certain year with all editions

optional arguments:
  -h, --help            show this help message and exit
  -l, --latest          try to download always the newest (starting from
                        2021-03)
  -y YEAR, --year YEAR  a single year in range [1997-2035]
  -V, --version         show program's version number and exit
```
#### --year
eg. a commandline  ``` python gsArchivPDFDownloader.py -y 2020 ``` will download all editions from 2020.
In case the commandline is used due to 2017 each year will try to get a 13 editions. Yes I know that does not make much sense, but let me fix that in a future edition in a better way.
This run type uses the "abortlimit" of the gs.json file to trigger an abort if the number is reached.  
in case the number is 2 and the flow is like this: success - fail - fail > Abort 
in case the number is 2 and the flow is like this: success - fail - success > the run will continue


#### --latest
In case you want to repeat the download on a monthly base after you downloaded all (with the initial function), this is the option for you.
```
python gsArchivPDFDownloader.py --latest
```
This run will read 'latestdownload' from the json file and tries now to download the next edition, eg. the last download was 2021/03 and we are currently at the 28th of April,  
this will first try to download the edition of 04/2021, than it will also check as it is past the 15th of the current month also to download the edition 05/2021.
I guess that maybe around the third week of a month there is a potential release of the next edition.
The "latest" commandline also takes in credit of a year jump (\*crossing fingers\*) around December.
Of course it makes maybe somehow sense to combine this with the json option "browser_display_on_latest" = "no".
In this run type, the max edition number of a year is 12. So if ever a 13th edition will come up, I need a fix.
```
Hint: If you create the task, create it as:  
Windows 10 , hidden, run without user logged in , do not store password  
add the absolute path to the python.exe in program field, add the "--latest" as argument and  
set the "start in folder" to the folder the gsArchivPDFDownloader.py is in.
```


## Remarks
Since v0.1 some parts are changed. Mostly to new error or requested enhancements.
Not sure how many this script used, but as long as I will use it I will update the program with error fixes and enhancements.

## FAQ
* Will it always work?  
  No, it depends on the webpage. In case the fields are renamed it will not work anymore. Taking in account that the basic function will stay the same, editing the names should not be a big issue.
* It not even download a single bit.  
  Did you edit the gs.json? Or It is broken already, sorry....drop me a note and I will a) fix or b)remove this :-)
  Send me the logfile via github (of course the credentials are blurred in the file)
* It will only download a fraction of the edition like a sample.  
  You may not enter in gs.json the right credentials
* Hell, why you use simple sleeps?  
  ...one time effort...lazy?...eh...I guess you are right, but it worked for me.....sorry. And I tried some limited conditional waits...

* After some successful downloads the job stopped, what is this?  
  I assume this is caused by a timeout, which is not caught. Just restart the job, it will start from the beginning, but skips all already downloaded pdf.

* You mixed German and English in the logging?  
  Yes, as I said it was more a one timer. In case I got some time I may convert all to one language.
* One timer? In version 0.x ? You cheating liar....  
  I need to confess, I added some nice features after my initial use...for others...so it's ok?

  
