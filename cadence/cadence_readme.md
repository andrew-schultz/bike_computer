### App & Local Server
* Install Python 3 if you don't already have it
* Create a python3 virtual environment
    * Run `pyenv virtualenv myenv`
    * Activate the environment: `pyenv activate myenv`
    * you may need to install usbutils: `brew install usbutil`
    * In your new venv, run `pip3 install --upgrade pip && pip3 install -r requirements.txt`
    * To run program: `python cadence.py`


The above script generally does the following:

- `setup()` preps the ANT stick for the appropriate idVendor and idProduct, and finds a free channel to work on;
    - Currently, we set up a channel only for our speed/cadence sensors;
    - You can find your device type (if you're a linux user) via lsusb.

- `start_listen()` starts the device listening for broadcast events from any sensors matching our specified type;

- `stop_listen()` stops the device and closes the channel and antnode -- freeing the USB device to use again;
    - For whatever reason, I end up having to unplug / re-plug the device to get it connected again.. whatever...
    
- Listens for broadcast events on the channel


----
Some notes on how this stuff works:

Interpreting / handling the data was a massive pain in the ass... for whatever reason, the data is sent out in byte-arrays and required a fair deal of converting back and forth between binary and integer formatting...

Had to learn a bit about MSB and LSB bit numbering... That was fun;

If your wheels are a different size, you'll probably want to update the wheel_diameter value -- mine is 673mm;

Script spits out your instantaneous cadence in RPM's, and your instantaneous speed in km/hr -- if you want your shit Americanized, you can 'GIT OUT:


----
So assuming that you've punched in the appropriate antProduct listed in your lsusb, and updated for any difference in wheel size -- you SHOULD be up and rolling:

Open up your terminal:
```
source env/bin/activate
python
import cadence
listener = cadence.ANTListener()
listener.setup()
listener.start_listen()
```

you SHOULD start seeing outputs like the following:

Cadence Timestamps:  6.95703125 || Cadence Revolutions:  285
Cadence Rev Delta:  4  Cadence Time Delta 2742  cadence:  89.62800875273523  RPM
Speed Timestamps:  7.2412109375 || Speed Revolutions:  1581
Speed Rev Delta:  8  Speed Time Delta 3033  Speed:  20.55819452018244  km/hr
=============
Cadence Timestamps:  9.6435546875 || Cadence Revolutions:  289
Cadence Rev Delta:  4  Cadence Time Delta 2460  cadence:  99.90243902439025  RPM
Speed Timestamps:  10.1884765625 || Speed Revolutions:  1589
Speed Rev Delta:  8  Speed Time Delta 3018  Speed:  20.66037242535233  km/hr
=============
Cadence Timestamps:  13.0166015625 || Cadence Revolutions:  294
Cadence Rev Delta:  5  Cadence Time Delta 2896  cadence:  106.07734806629834  RPM
Speed Timestamps:  13.140625 || Speed Revolutions:  1597
Speed Rev Delta:  8  Speed Time Delta 3023  Speed:  20.62620045640534  km/hr
=============
Cadence Timestamps:  15.744140625 || Cadence Revolutions:  298
Cadence Rev Delta:  4  Cadence Time Delta 2666  cadence:  92.18304576144037  RPM
Speed Timestamps:  16.130859375 || Speed Revolutions:  1605
Speed Rev Delta:  8  Speed Time Delta 3062  Speed:  20.363489216104945  km/hr
=============
Cadence Timestamps:  18.486328125 || Cadence Revolutions:  302
Cadence Rev Delta:  4  Cadence Time Delta 2412  cadence:  101.8905472636816  RPM
Speed Timestamps:  18.7626953125 || Speed Revolutions:  1612
Speed Rev Delta:  7  Speed Time Delta 2695  Speed:  20.24448181159524  km/hr

----
So that's it that's all! That's how you can whip up a quick and dirty ANT+ speed/cadence reader...

Next steps are up to you -- I've got some cool ideas for what I want to accomplish... Images below paint a bit of a story for what I'm thinking...
