# ESP8266 MicroPython Slack/HipChat Integration

A simpler webhook handler written in MicroPython for the ESP8266 that evaluates the message as MicroPython and returns the result as the response to the webhook.  This allows for interactions like

    /micropython 1+1
    2
    
    /micropython “Memory Free: {} / {} bytes”.format(gc.mem_free(), gc.mem_free() + gc.mem_alloc())
    Memory Free: 16432 / 28160 bytes
    
    /micropython network.WLAN(network.STA_IF).ifconfig()
    ('192.168.2.119', '255.255.255.0', '192.168.2.1', '192.168.2.1')
    
    /micropython “I found a {}”.format(ure.search(“(cat|dog)”, "The animal is a dog.”).group(1))
    I found a dog

By default the [urequests module](https://github.com/micropython/micropython-lib/blob/master/urequests/urequests.py) is not imported to avoid someone being able to make web requests from your device, but if you include urequests.py and uncomment out the import a number of interesting /micropython requests coming urequests and ure become possible.
    
## Setup
1. Ensure your ESP8266 is running the [latest MicroPython firmware load](https://micropython.org/download/#esp8266).  Turn off access point mode and connect it to a wireless network in station mode.
2. Place main.py, safer_gc.py, safer_machine.py, safer_network.py, safer_os.py, safer_sys.py, and safer_time.py on the device (I use the [WebREPL](https://docs.micropython.org/en/latest/esp8266/esp8266/quickref.html#webrepl-web-browser-interactive-prompt) to do this).
3. Reboot the device...it should now be running the script
4. Configure a slash command of /micropython in either Slack or HipChat (or both).  For HipChat the destination URL will be the IP of the device (or your router if you setup port forwarding) and /hipchat.  For Slack it will be the IP of the device and /slack.  The URL allows the device to determine which format the request and response will be in.
5. Done!  Try a /micropython command and see the responses.  The scripts print out a lot of debug so you should be able to have a lot of debug information to determine where it might fail.

## Functionality
The modules gc, machine, network, os, sys, and time are both available with some of their functionality removed to avoid someone inadvertently bringing the device offline by changing network settings or deleting files from flash.

The ure module is available in full to demonstrate interesting parsing capabilities from MicroPython.

## Resiliency
Try except handling is in place to try and keep the webhook handler alive despite various exceptions that might be encountered while evaluating the supplied scripting.

In order to try and maintaint he most stable experience the device will proactively reboot when it hits exceptions like memory allocation failures.  For other exceptions that are benign (syntax errors) it will just return the error to the caller without rebooting.  Since the main.py script should start when the device boots it should only result in minimal unavailability.

## Protection
Instead of providing modules like os and sys directly, slightly sanitized versions are imported (safer_sys as sys) in order to protect the webhook handling.  Without this requests to something like sys.exit() could terminate the script and prevent it from handling subsequent webhooks.

Additionally various built-ins like open(), \__import__, memoryview, and others are cleared so they're not available to the evaluated script.

If you find anything that can allow an evaluated script to affect the handling of subsequent webhooks or elevate its access to things like the filesystem or network feel free to open up an issue.

As it stands, the most likely place I can think of is the possibility of a carefully selected RegEx executed with the ure module that might cause the script to block for a long time (but I haven't tried that yet).