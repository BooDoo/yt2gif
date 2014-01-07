INSTRUCTIONS (Windows)
===============
 - Install [Python 2.7](http://www.python.org/download/releases/2.7.6/)  
 - Install [pip](https://sites.google.com/site/pydatalog/python/pip-for-windows) for Python package management  
 - Run: `pip install youtube-dl pytumblr pyimgur`  
 - Install [ffmpeg](http://ffmpeg.zeranoe.com/builds/)  
 - Install `numpy` 1.8.0 and `opencv` 2.4.7 binaries from [here](http://www.lfd.uci.edu/~gohlke/pythonlibs/)  
 - Install [ImageMagick](http://imagemagick.org/script/binary-releases.php#windows)  
 - **Copy `convert.exe` from your `ImageMagick/bin` install directory to the `yt2gif` directory**  
		There's an MS-native `C:\Windows\System32\convert.exe` which fucks it all up otherwise.  
 - $ `git clone https://github.com/BooDoo/yt2gif`  
 - $ `cd yt2gif; git submodule update --init`  
 - $ `python yt2gif.py --help`  

Hopefully that works without any horrible errors. If so, move on to:  
`python yt2gif.py -d 3 -f 10 --bw [YOUTUBE VIDEO ID]`  

This should download a video at 360p and make a 3 second black & white GIF of the full frame at 10fps.  

If that happens you're probably in the clear for messing around to your heart's content.  

As an example, making [this GIF](http://deadspelunkers.tumblr.com/post/70364761562/ibmv7shvevm) would be:  
`python yt2gif.py --start 522 --duration 4 --fps 10 --delay 8 --fuzz 4% --crop 27.5% 20% --bw IbMv7shVeVM`  
(`--crop` works like CSS args: single value acts as universal, two is treated as top/bottom and left/right, four go clockwise from top)  

KNOWN ISSUES  
-------------  
 - It probably won't clean up after itself (deleting source MP4/temp AVI) in Windows.
 - Tumblr/Imgur integrated upload isn't working yet.  
