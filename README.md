# gsArchivPDFDownloader


# Table of contents

- [Overview](#overview)
  - [Demo Video](#demo-video)
  - [Exclusion](#exclusion)
- [Technologies](#technologies)
- [Setup](#setup)
- [Edit gs_credential.json](#edit-gs_credentialjson)
- [Edit gs.json](#edit-gsjson)
  - [Filenamepattern in gs.json](#filenamepattern-in-gsjson)
  - [skip_editions in gs.json](#skip_editions-in-gsjson)
- [Run](#run)
  - [commandline argument](#commandline-argument)
    - [--full](#--full)
    - [--cover](#--cover)      
    - [--range](#--range)
    - [--year](#--year)
    - [--latest](#--latest)
    - [--coverlatest](#--coverlatest)
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
Info: Important change - since 0.5.6 a new gs_credential.json is used to seperate credentials from other settings
```
Here is the link to the GS forum: https://www.gamestar.de/xenforo/threads/schon-mal-alle-hefte-aus-dem-plus-archiv-geladen-wenn-nein-dann.470604/

### Demo Video
Check this small demo Video: 
Video shows Version 0.1 - current solution works similar, with a bit different logging  
[Demo Video](http://www.kastaban.de/demo_mp4/gsArchivePDFDownloader.mp4 "Demo Video")  
The video displays what the start of the program would look like, than the start of the download. In this sample there are already some previous downloaded file. It will skip 1998/1 to 1998/6, than it will download 1998/7. Skip 8/1998 as also previously downloaded. Download 9/1998 and skip again 10/1998. The job was stopped for demo after 1/1999 and finally a tree is displayed. This is what the years should look like in the very end.

### Exclusion
* The edition 2017/10 was a exception until May 11th 2021: Caused by an error in "Blättercatalog"  
To prevent a error the edition is listed in [gs.json](#edit-gsjson) in key "skip_editions"  
(thx to thomas-k for motivation): A warning will be displayed in case you try to download this edition  
  (09 March 2021) - I contacted GS on that.   
  (12 March 2021) - the edition is downloadable as a ZIP,but not from blätterkatalog which uses the program  
  (11 May   2021) - hightower5 reported this as working -> see issue#10
  
* The cover of 2021/08 misses some text
This is caused by a faulty pdf, I'm no expert on PDFs, but it looks like a font is missing in the pdf.
  
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
* Win32Printing was version 0.1.3
* Ghostscript (py) was version 0.7
* geckodriver 0.29.0 (cf6956a5ec8e 2021-01-14 10:31 +0200)
* Firefox 86.0(64-bit)
* Ghostscript was version 9.54.0
* hosting OS was Windows 10 (20H2)
```

## Setup
* Install obviously python (assuming default settings)
  
* Install ghostscript (Executable)
```
winget install ghostscript
```
If winget is not already part of your system, check this out (https://docs.microsoft.com/en-us/windows/package-manager/winget/)
WInget is a lookalike apt-get, but of course you could install ghostscript as you like. Portable will only work in 
case python is able to locate the dll in the system. 

* install with pip selenium
```
pip install selenium
```
* install with pip ghostscript & win32printing
```
pip install ghostscript win32printing
```
* Get gsArchivPDFDownloader.py and gs.json from this repository  
Use one of the two options  
  - Go to "releases" and download the last release published as ZIP
  - Download from main   
```
Click on "Code" (green button on top), than select "Download ZIP"
Extract the Content to some writeable folder. Eg. \gsDownloader\gsArchivePDFDownloader 
```
The difference is that main, may contain newer und not so tested code.

* Get geckodriver(.exe) as zip from 
https://github.com/mozilla/geckodriver/releases, extract the geckodriver.exe
and place it in the same folder as the gsArchivPDFDownloader.py
  ```
  Hint: The "pip install geckodriver" will install the driver also, but may not work, as I expect the driver in the 
  same folder as the .py file
  ```

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
| Name          | value allowed        | Remark|introduced|
|:---|:---:|:---|:---:|
| user      | string | your gs user name | v0.5.6|
| password      | string   | your gs user password | v0.5.6|


## Edit gs.json
This is a not working sample ! - Get the real one from code or release page.

```
[
    {
        "log_level": "INFO",
        "downloadtarget": "c:\\download\\Gamestar-archive",
        "downloadtargetcovers": "c:\\download\\Gamestar-archive\\covers",
        "edition2d": "Yes",
        "downloadtimeout": 240,
        "abortlimit": 2,
        "filenamepattern_intarget": "GameStar Nr. <ausgabe>_<jahr>.pdf",
        "filenamepattern_fromserver": "GameStar Nr. <ausgabe>_<jahr>.pdf",
        "filenamepattern_fromserverwhiledl": "GameStar Nr.*<ausgabe>_<jahr>.pdf",        
        "latestdownload": [
            {
                "year": "2021",
                "edition": "8"
            }
        ],
        "latestdownload_cover": [
            {
                "year": "2021",
                "edition": "8"
            }
        ],
        "cover_page_print": "Yes",
        "cover_page_number": 1,
        "browser_display_on_latest": "no",
        "skip_editions": []
    }
]
```
| Name          | value allowed        | Remark|introduced|
|:---|:---:|:---|:---:|
| log_level      | [debug/info/warning/error/critical]   | The log level just in case needed - info is default, debug is fallback | v0.5|
| downloadtarget | string   | please mask all "\\" with a additional leading "\\", so a path like "c:\\download\\Gamestar-archive" will look like "c:\\\\download\\\\Gamestar-archive". | v0.1|
| downloadtargetcovers | string   | please mask all "\\" with a additional leading "\\", so a path like "c:\\download\\Gamestar-archive\\covers" will look like "c:\\\\download\\\\Gamestar-archive\\\\covers". | v0.7|
| edition2d | [Yes/No] | "No" will use the edition from the server like 1,2,3,4,5; "Yes" will create edition names like "01,02,03,04,05..." | v0.2|
| downloadtimeout | int | Time in seconds the download wait for a download before trying to download the next edition. This is a max timer, in case the edition is completed before that time it will not wait until the max time. Currently only successful downloads will be moved to target | v0.1|
| abortlimit | int | default 2; In case a "-year" run is selected and 'abortlimit' edition in sequence are not found the run will be aborted. A new success after a failed download will reset the counter.   | v0.5.6|
| browser_display_on_latest | [Yes/No]  | In case the commandline option --latest or -l thi soption allow a hidden browser on value "no", "yes" will display the browser also on this commandline option  | v0.5|
| latestdownload | list] | in case the commandline option --latest/-l is used this will be updated with the latest downloaded edition, so the next run (month) will start from that edition the copy; see ["--latest"](#--latest)  | v0.5|
| latestdownload_cover | list] | in case the commandline option --coverlatest/-cl is used this will be updated with the latest downloaded cover, so the next run (month) will start from that edition the copy; see ["--coverlatest"](#--coverlatest)  | v0.7|
| cover_page_print | [Yes/No]   | "Yes" will print the cover directly in case --coverlatest/-cl is used to default printer - with current default settings| v0.7|
| cover_page_number | int   | The pdf contains multiple formats, 1 might by the DVD box layout, --coverlatest/-cl will print this page   | v0.7|


### Filenamepattern in gs.json
| Name          | value allowed        | Remark                                                                                                       | Introduced |
|:---|:---:|:-------------------------------------------------------------------------------------------------------------|:----------:|
| filenamepattern_intarget      | string | The downloaded file will be moved with that name to the downloadtarget folder                                |    v0.1    |
| filenamepattern_fromserver      | string   | That is the file we get after we click on the "alle" button in "blätterkatalog"                              |    v0.1    |  
| filenamepattern_fromserverwhiledl      | string   | That is the file we get while thwe file is downloaded |   v0.8   |  

Basic idea: The filename pattern is read from file and than the strings "\<ausgabe\>" and "\<jahr\>" are replaced by the current proceeded values.

So you do not like the naming of the files? You want to honor GS? You need a file name like: "Tolle GameStar Nr. aus dem Jahr 1997 mit Ausgabe 9.pdf"
than alter the "filenamepattern_intarget" to ```"filenamepattern_intarget": "Tolle GameStar Nr. aus dem Jahr <jahr> mit Ausgabe <ausgabe>.pdf"```
or simpler you want a filename like "GameStar 1997-9.pdf" than use "filenamepattern_intarget" to ```"filenamepattern_intarget": "GameStar <jahr>-<ausgabe>.pdf"```

I found out during the creation of v0.2 that the server changed the naming. They moved from "GameStar_Nr._9_1997.pdf"  to  "GameStar Nr. 9_1997". Mind the small change in use of the "\_"
To overcome this small but maybe annoying thing (maybe "they" did not like my downloader, or it was Shodan, GLaDOS...), I added also here a way to get the right URL.
As mentioned in the start and end, if "they" change fundamental things, upsi....it will not work anymore.
With that we could try a small fix.

In April 2022 a new file download name is introduced (or seen). While downloading a differnet name is seen. Not sure 
why or what caused this, but at least the  <filenamepattern_fromserverwhiledl> is a option to get arround this.

### skip_editions in gs.json
| Name          | value allowed        | Remark|
|:---|:---:|:---|
| skip_editions      | string   | a list of each year with editions that cause error while downloading (server issue), request to download with a comma separated value; no spaces,no leading 0|

Currently, (May 2021) there should be only one edition (2017/10)

## Run 
### commandline argument
```
usage: gsArchivPDFDownloader.py [-h] [-l] [-f] [-y YEAR] [-r RANGE] [-v]

Download GameStar PDFs from webpage

optional arguments:
  -h, --help            show this help message and exit
  -l, --latest          try to download always the newest (starting from
                        xxxx-x)
  -cl, --coverlatest    try to download always the newest cover (starting from
                        xxxx-x)
  -f, --full            a full download of all editions from 1997/09 to x/xxxx
  -c, --cover           a full download of all covers from from 2000/01 to
                        x/xxxx
  -y YEAR, --year YEAR  a single year in range [1997-2035]
  -r RANGE, --range RANGE
                        a range in fomrat yyyy:mm-yyyy:mm; example -r
                        2019:09-2020:11
  -v, --version         show program's version number and exit

```

#### --full
To start a download job open a cmd and type
```
python gsArchivPDFDownloader.py -f 
```
```
python gsArchivPDFDownloader.py --full 
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

#### --cover
To start a download job open a cmd and type
```
python gsArchivPDFDownloader.py -c 
```
```
python gsArchivPDFDownloader.py --cover 
```

Now the job will start, it will check and create the "downloadtarget" folder.
It will open a firefox/geckodriver browser and than tries in a loop to download all covers starting from 2000/01 to 
the current year. Than it will save the file. After the download is complete (no *.part is seen anymore), the new file is moved to a sub folder of the year.
In other words the structure of the sample will look like
```

C:
  |
  +--download
            |
            +--Gamestar-archive
                              |
                              +--covers
                                      |
                                      +2000  <-- all covers of that year
                                      +2001  <-- all covers of that year 
                                      +2002  <-- all covers of that year 
                                      +2000  <-- all covers of that year 
                                      +...         
```
It will not check for errors. In case a cover  is missing, it simply tries the next. Practically the first cover 
found is 2015/12. Maybe the older covers are not there or in a different format. I kept the start year 2000 just for 
no good reason.

#### --range
```
python gsArchivPDFDownloader.py --range YYYY:mm-YYYY:mm

Example: python gsArchivPDFDownloader.py --range 2012:02-2013:10
```
the argument ```YYYY:mm-YYYY:mm``` is in format   
```4 digits start year>:<2 digits start month>-<4 digits end year>:<2 digits end month>```

The start year/month needs to be older than the end year/month.   
Script will check for correct format and valid range.
Anything from 1997/08 to 2039/12 will be accepted as valid.

#### --year
eg. a commandline  ``` python gsArchivPDFDownloader.py -y 2020 ``` or  ``` python gsArchivPDFDownloader.py --year 2020``` 
will download all editions from 2020.
In case the commandline is used, each year will try to get a 13 editions. Which currently does only exists in 2017.  
Yes I know that does not make much sense, and this issue will be adressed in a next version.  

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

#### --coverlatest
In case you want to repeat the download of a cover on a monthly base after you downloaded all (with the initial 
function --cover), this is the option for you.
```
python gsArchivPDFDownloader.py --coverlatest
```
This run will read 'latestdownload_cover' from the json file and tries now to download the next cover, eg. the last 
download was 2021/03 and we are currently at the 28th of April,  
this will first try to download the cover of 04/2021, than it will also check as it is past the 15th of the 
current month also to download the cover 05/2021.
I guess that maybe around the third week of a month there is a potential release of the next edition.
The "coverlatest" commandline also takes in credit of a year jump (\*crossing fingers\*) around December.
Of course it makes maybe somehow sense to combine this with the json option "browser_display_on_latest" = "no".
In this run type, the max cover number of a year is 12. So if ever a 13th cover will come up, I need a fix.
```
Hint: If you create the task, create it as:  
Windows 10 , hidden, run without user logged in , do not store password  
add the absolute path to the python.exe in program field, add the "--coverlatest" as argument and  
set the "start in folder" to the folder the gsArchivPDFDownloader.py is in.
```

## Remarks
Since v0.1 some parts are changed. Mostly to new error or requested enhancements.
Not sure how many this script used, but as long as I will use it I will update the program with error fixes and enhancements.

## FAQ
* Will it always work?  
  No, it depends on the webpage. In case the fields are renamed it will not work anymore. Taking in account that the basic function will stay the same, editing the names should not be a big issue.
  See change caused  by April 2022.

* It not even download a single bit.  
  Did you edit the gs.json? Or It is broken already, sorry....drop me a note and I will a) fix or b)remove this :-)
  Send me the logfile via github (of course the credentials are blurred in the file)

* It will only download a fraction of the edition like a sample.  
  You may not enter in gs.json the right credentials

* After a Job, somtimes file remain in the top download folder?
  This should not happen. Will be adressed in of of the next versions

* Hell, why you use simple sleeps?  
  ...one time effort...lazy?...eh...I guess you are right, but it worked for me.....sorry. And I tried some limited conditional waits...

* After some successful downloads the job stopped, what is this?  
  I assume this is caused by a timeout, which is not caught. Just restart the job, it will start from the beginning, 
  but skips all already downloaded pdf.  thelog may report these editions and you should try a rerun withthte same 
  command. This may overcome the issue by it self.

* You mixed German and English in the logging?  
  Yes, as I said it was more a one timer. In case I got some time I may convert all to one language.

* One timer? In version 0.x ? You cheating liar....  
  I need to confess, I added some nice features after my initial use...for others...so it's ok?
  
* Printing does not work for me.
  Well as the printing uses some transformations and additional packages, it may not work. Even I tested it on three 
  system with different printers. There is a high chance that it may not work for you. But maybe we could sort it 
  out by some logging and debugging.

  
