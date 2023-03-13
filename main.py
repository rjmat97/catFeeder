btn=Pin(0, Pin.IN, Pin.PULL_UP)
feedob = ''
logfi = '/catfeedLogger.log'
timfi = '/catfeedtime.txt'
intype="""type="number" id=\""""
inputtag1="""<input class="border-2 rounded-lg my-2 p-2" """
h3css='text-3xl font-bold'
print(station.ifconfig())
gsp =1
def timeFormatter(tim=''):
    if len(tim)==0: tim=time.localtime(time.time() + 19800)
    return ''.join(list(map(lambda x: f'0{x}' if x<10 else f'{x}', tim[3:5])))

def parsefeedob(obstr, op="+", sav=False):
    global ti, sp
    print(obstr, '===>')
    ti = obstr.split('_')[0].split(';')
    sp = obstr.split('_')[1].split(';')
    ti = list(map(lambda x: f'{x[:2]}{x[-2:]}', ti))
    if op=="+":
        ti += [timeFormatter()]
        sp += ['2']
    elif op=='-': ti, sp = ti[:-1], sp[:-1]
    
    if sav:
        global timfi
        sav=";".join(ti)+"_"+";".join(sp)
        with open(timfi,'w') as f: f.write(sav)
    
def loadTime(fi):
    global feedob
    with open(fi) as f: feedob=f.readline().split('_')
    return feedob[0].split(';'), feedob[1].split(';')

def dataLogger(fi, val):
    with open(fi, 'a', encoding='utf8') as f:
        f.write(f'{val}\n')
    print('file saved')  

def getRequestVal(req, chstr):
    check = req.find(chstr)
    return req[check:].split(' HTTP/')[0].split('=')[-1]

def web_page():    
    global ti, sp
    timeStamps = ''
    tks, sks = [],[]
    for d,i in enumerate(ti):
#       <script src="https://cdn.tailwindcss.com"></script>
        tks.append(f'"t{d}"')
        sks.append(f'"s{d}"')
        chng="""onchange="changeTime('?/chtime=')" """
        timeStamps += f"""
            {inputtag1}{chng}type="time" id="t{d}" name="appt" value="{i[:2]}:{i[-2:]}">
            {inputtag1}{chng}{intype}s{d}" name="quantity" min="1" value="{sp[d]}"></br>
        """

    negbutton = """<button onclick="changeTime('/?remtime=')" class="bg-emerald-500 rounded-full w-[40px] p-2 text-white font-bold">-</button>"""
    negbutton = negbutton if len(timeStamps)>1 else ''
    html = f"""
        <!DOCTYPE html> <html lang="en"> <head> <title>ESP Web Server</title> <meta name="viewport" content="width=device-width, initial-scale=1"> <script src="https://cdn.tailwindcss.com"></script> </head> <body class="text-center"> <h3 class="text-5xl font-bold mt-6 mb-4">Cat Feeder</h3> <hr class="my-6"/> <p> spoon: {inputtag1}{intype}masterspoon" min="1" value="{gsp}"><br /> open:  {inputtag1}{intype}opn" value="{o}"><br/> close: {inputtag1}{intype}cls" value="{c}"><br/> sleep: {inputtag1}{intype}slp" value="{s}"><br/> <button onclick="pushServe()" class="p-6 m-2 rounded-lg text-base text-white bg-emerald-500">Feed Cat</button><br/> <!-- input class="border-2 rounded-lg my-2 p-2 --> </p> <hr class="my-6"/> <p> <h3 class="text-3xl font-bold">Servo Location Tester</h3> </br> <button onclick="testLoc()" class="p-2 m-2 rounded-lg text-base bg-red-50">setServo</button> {inputtag1}{intype}tst" value="{tst}"> <br /> </p> <hr class="my-6"/> <h3 class="text-3xl font-bold">Auto Feed Times: </h3> """+ timeStamps + """ <button onclick="changeTime('/?addtime=')" class="bg-red-500 rounded-full w-[40px] p-2 text-white font-bold">+</button> """ + negbutton + """ </p> <hr class="my-6"/> </body> <script> times = ["""+ ','.join(tks) +"""]; spons = ["""+ ','.join(sks) +"""]; function sendRequest(req){ let xhr = new XMLHttpRequest(); xhr.open("GET", req); xhr.onload = (e) => { if (xhr.readyState === 4) { if (xhr.status === 200) { window.location.reload(); } else { console.error(xhr.statusText); } } }; xhr.onerror = (e) => { console.error(xhr.statusText); }; xhr.send(); } function changeTime(req) { out1 = times.map((i,d) => document.getElementById(i).value).join(';'); out2 = spons.map((i,d) => document.getElementById(i).value).join(';'); console.log(out1); console.log(out2); reqstr = `${req}${out1}_${out2}`; console.log(reqstr); sendRequest(reqstr); } function pushServe(){ let spoons = document.getElementById('masterspoon').value; let opn = document.getElementById('opn').value; let cls = document.getElementById('cls').value; let sleep = document.getElementById('slp').value; sendRequest(`/?feed=${spoons},${opn},${cls},${sleep}`); } function testLoc(){ let tst = document.getElementById('tst').value; console.log(tst); let rqst = `/?tst=${tst}`; console.log(rqst); sendRequest(rqst); } </script> </html>
    """  
    return html

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.settimeout(10)
serv.bind(('', 80))
serv.listen(5)

ti,sp = loadTime(timfi)
print(sp)
# def sockserver(conob, request):
now=timeFormatter()
# ti = [f'{now[:2]}{int(now[-2:])+0}',
#       f'{now[:2]}{int(now[-2:])+1}',
#       f'{now[:2]}{int(now[-2:])+2}',
#       f'{now[:2]}{int(now[-2:])+3}']
print(ti)
served=''
print('now =====> ',now)

# ntptime.settime()
while True:
    now=timeFormatter()
    if served!=now and now in ti:
        print('---------------> ', now)
        serveFood(int(sp[ti.index(now)]), o, c, s )
        served=now
    try:
        conn, addr = serv.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        getreq, getind, now = '',0,timeFormatter()
        chstrs = ['feed=','trst=','addtime','remtime','chtime', 'tst=']
        for i in chstrs:
            if request.find(i)!=-1:
                getreq, getind=i, request.find(i)
                print(getreq,getind)
        
        if getreq=='feed=':
            check = request.find('feed=')
            gsp, o, c, s = request[check:].split(' HTTP/')[0].split('=')[-1].split(',')
            gsp, o, c, s = int(gsp), int(o), int(c), float(s)
            print('feed cat now: ',gsp, o, c, s)
            with open('servoset.txt','w') as f: f.write(f'{o}_{c}_{s}')
            led.value(1)
            serveFood(gsp, o, c, s )
            led.value(0)
        elif getreq=='tst=':
            check = request.find('tst=')
            tst = int(request[check:].split(' HTTP/')[0].split('=')[-1])
            print('set servo loc: ', tst)
            servo.duty(tst)            
        elif getreq=='addtime': parsefeedob(getRequestVal(request, 'addtime'), '+', True)
        elif getreq=='remtime': parsefeedob(getRequestVal(request, 'remtime'), '-', True)
        elif getreq=='chtime':  parsefeedob(getRequestVal(request, 'chtime'), '',  True)
        
        response = web_page()
        conn.send('HTTP/1.1 200 OK\n')
        conn.send('Content-Type: text/html\n')
        conn.send('Connection: close\n\n')
        conn.sendall(response)
        conn.close()
        gc.collect()
    except OSError:
        continue
