import safer_time as time
import safer_gc as gc
import safer_machine as machine
import safer_sys as sys
import ujson

# These are imported for eval usage
# I'm sure someone will find a way to use ure
# to execute an infinite duration regex...but
# we'll solve that if it becomes a problem
# because it's fun for extracting data
import ure
import safer_network as network
import safer_os as os

# add urquests.py and uncomment to allow
# web requests from evaluated messages
# import urequests

# some stuff we don't want eval to call
open = None
exec = None
__import__ = None
memoryview = None
setattr = None
input = None

try:
    del vfs, bdev, uos
except:
    pass

# borrowed method out of urllib.py
# for urldecoding the Slack requests
def unquote_plus(s):
    s = s.replace('+', ' ')
    res = s.split('%')
    for i in range(1, len(res)):
        item = res[i]
        res[i] = chr(int(item[:2], 16)) + item[2:]
    return "".join(res)

def build_hipchat_response(message):
    body = {
        'color': "green",
        'message': message,
        'notify': "false",
        'message_format': "text"
    }
    body = ujson.dumps(body)

    return '''HTTP/1.0 200 OK\r\nContent-type: application/json\r\nContent-length: %d\r\n\r\n%s''' % (len(body), body)

def build_slack_response(message):
    body = {
        'response_type': 'in_channel',
        'text': message
    }
    body = ujson.dumps(body)

    return '''HTTP/1.0 200 OK\r\nContent-type: application/json\r\nContent-length: %d\r\n\r\n%s''' % (len(body), body)


def script_from_hipchat_request(request):
    request = request.decode("utf-8")

    print("Hipchat Request: " + request)

    body_start = request.find("\r\n\r\n")
    body = request[body_start+4:]
    print("Body: " + body)

    json = ujson.loads(body)
    script = json['item']['message']['message'].replace("/micropython", "", 1).strip()
    print ("Script: " + script)
    return script

def script_from_slack_request(request):
    request = request.decode("utf-8")

    print("Slack Request: " + request)

    # replace special double quote characters slack inserts
    request = request.replace("%E2%80%9C", "\"").replace("%E2%80%9D", "\"")

    script = unquote_plus(ure.search("text=(.*?)&", request).group(1))
    print ("Script: " + script)

    return script

def start():
    # import socket here to avoid it being available for eval
    import socket

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)

    print('listening on', addr)

    try:
        while True:
            gc.collect()
            print("Waiting for next client")
            cl, addr = s.accept()
            reset = False
            response = "No Response"
    
            try:
                print('client connected from', addr)
                gc.collect()
    
                cl.settimeout(1.0)
                request = cl.recv(1024)
    
                try:
                    cl.settimeout(.1)
                    for i in range(10):
                        request += cl.recv(1024)
                except:
                    pass

                url = ure.search("(?:GET|POST) (.*?) HTTP", request).group(1)
                print("URL is {}".format(url))
                hipchat = "hipchat" in url

                if hipchat:
                    script = script_from_hipchat_request(request)
                else:
                    script = script_from_slack_request(request)

                request = None
                gc.collect()
    
                try:
                    response = str(eval(script))
                except (IndentationError, ZeroDivisionError, NameError, SyntaxError, AttributeError, TypeError) as e1:
                    response = str(e1)
                except Exception as e1:
                    reset = True
                    response = str(e1) + " (there may be a small delay before requests are processed again)"
                print("MicroPython response: " + response)
    
                script = None
                gc.collect()

                if hipchat:
                    response = build_hipchat_response(response)
                else:
                    response = build_slack_response(response)
    
                cl.settimeout(5)
                while len(response) > 0:
                    print("Response Length: %s" % len(response))
                    sent = cl.send(response)
                    response = response[sent:]
                    print("Sent %s bytes" % sent)
    
            except Exception as e:
                print("Failed to handle request")
                sys.print_exception(e)
    
            cl.close()
            if(reset):
                time.sleep(.25)
                machine.reset()
    finally:
        s.close()

start()