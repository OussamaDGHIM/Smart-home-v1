import sqlite3
import socket
import subprocess
import RPi.GPIO as GPIO
from mfrc522 import *
from time import *

import time

# ------------------------------------------


AO_pin = 0
A1_pin = 1  # flame sensor AO connected to ADC chanannel 0
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
# SPICLK = 21
# SPIMISO = 19
# SPIMOSI = 20
# SPICS = 16
# RPWM = 17;
# LPWM = 18;

# L_EN = 22;
# R_EN = 23;

# in1 =27
# in2 = 24
# en = 25
SPICLK = 40
SPIMISO = 35
SPIMOSI = 38
SPICS = 36
RPWM = 11
LPWM = 12

L_EN = 15
R_EN = 16

in1 = 13
in2 = 18
en = 22

# -------------------------------------------
Host = ''
PORT = 21567
ADDR = (Host, PORT)
BUFSIZE = 1024
PORTSEND = 7801

# Reserve a port for your service.

# ---------------------------------------

socketserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socketserver.bind(ADDR)
db = sqlite3.connect("SmartcarDB")
db.execute("create table  smartcarpassage(motPass  text ,nom text)")
db.execute("create table gestionvoiture(Smartcar text ,radar txt,batterie int)")
db.execute("insert into gestionvoiture(Smartcar,radar) values(?,?)", ("Smartcar", "desactiver"))
db.execute("create table  smartcardpfils2(prenom  text ,dateN text,poid int,sexe text,image blob,rfidN text,path text,etat_de_connextion txt,limitation_vitesse int,limitation_accer txt ,bolquager txt)")

# db.execute("create table  smartcardpfils(prenom  text ,dateN text,poid int,sexe text,image blob,rfidN long)")

# -----------------------------------------

# port init

GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)
# gpio.setmode(gpio.BOARD)


# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(RPWM, GPIO.OUT)
GPIO.setup(LPWM, GPIO.OUT)
GPIO.setup(L_EN, GPIO.OUT)
GPIO.setup(R_EN, GPIO.OUT)
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)

GPIO.output(R_EN, True)
GPIO.output(L_EN, True)
rpwm = GPIO.PWM(RPWM, 100)
lpwm = GPIO.PWM(LPWM, 100)
rpwm.ChangeDutyCycle(0)
lpwm.ChangeDutyCycle(0)
p = GPIO.PWM(en, 100)
rpwm.start(0)
lpwm.start(0)
p.start(0)


# read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
    if ((adcnum > 7) or (adcnum < 0)):
        return -1
    GPIO.output(cspin, True)

    GPIO.output(clockpin, False)  # start clock low
    GPIO.output(cspin, False)  # bring CS low

    commandout = adcnum
    commandout |= 0x18  # start bit + single-ended bit
    commandout <<= 3  # we only need to send 5 bits here
    for i in range(5):
        if (commandout & 0x80):
            GPIO.output(mosipin, True)
        else:
            GPIO.output(mosipin, False)
        commandout <<= 1
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)

    adcout = 0
    # read in one empty bit, one null bit and 10 ADC bits
    for i in range(12):
        GPIO.output(clockpin, True)
        GPIO.output(clockpin, False)
        adcout <<= 1
        if (GPIO.input(misopin)):
            adcout |= 0x1

    GPIO.output(cspin, True)

    adcout >>= 1  # first bit is 'null' so drop it
    return adcout


# ------------------------------------------
voltage = 0.0
send = ''
droide_deg0 = False
droide_deg40 = False
gauche_deg0 = False
gauche_deg40 = False
send=''
my_timer=0
prenomfilsvit=''
terminer=False
def countdown():
    global  my_timer
    global terminer
    #my_timer =60
    for  x in range(60):
       my_timer = my_timer-1
       sleep(1)

    terminer = True
    return terminer
while True:

    msg2 = ''
    socketserver.listen(5)
    client, address = socketserver.accept()

    confirmer = client.recv(BUFSIZE).decode()
    lst = list(address)
    lst[1] = PORTSEND
    address = tuple(lst)
    print(msg2)
    socketclient1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if confirmer == "inscriptionParent":
        # socketclient1.close()
        while True:
            # mot=str()
            socketserver.listen(5)
            client, address1 = socketserver.accept()
            print("{} connected2".format(address1))
            print("attender")
            response = client.recv(1024).decode()
            base = response.split("////")
            print(base[0])
            print(base[1])
            db.execute("insert into smartcardp(motPass,nom) values(?,?)", (base[0], base[1]))
            db.commit()
            break
    # break
    elif confirmer == "validation":
        # if confirmer=="confirmer":
      while True :
        socketserver.listen(5)
        client, address = socketserver.accept()
      #  print("{} connected".format(address))

        confirmer = client.recv(BUFSIZE).decode()
        #  while True:
        print("connectpage")
        #     socketserver.listen(5)
        #    client2, addr1 = socketserver.accept()
        #     print("{} connected2".format(addr1))
        print("attender")
        ch = confirmer.split("////")
        print(ch)
        nomvalide = "'" + ch[0] + "'"
        passvalide = "'" + ch[1] + "'"

        print(nomvalide, passvalide)
        result = db.execute(f'''select * from smartcardp where motPass={passvalide} and nom={nomvalide}''')

        if len(result.fetchall()) == 0:
            print("ne exist pas")
          #  msg3 = "votre profile n'exist pas "
          #  socketclient1.connect(('192.168.43.1', PORTSEND))
           # socketclient1.send(msg2.encode())
         #   socketclient1.close()
        # break
        else:
            print("exist")
            msg2 = "oui"
            #   socketclient1.send(msg2.encode())
            result = db.execute(f'''select * from smartcardp where motPass={passvalide} and nom={nomvalide}''')
            for values in result:
                send = msg2
            print(send)
            socketclient1.connect(('192.168.43.1', PORTSEND))
            socketclient1.send(send.encode())
            socketclient1.close()
            break


    elif confirmer == "batterie":
        print("Pagebatterie")

        while True:
            ad_value = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
            voltage = ad_value * (3.3 / 1024) * 5
            voltagerou = round(voltage, 1)
            if (voltagerou >= 12.6):
                msg2 = "100"

            elif (voltagerou < 12.6 and voltagerou >= 12.0):
                msg2 = "75"

            elif (voltagerou < 12.0 and voltagerou >= 11.0):
                msg2 = "50"

            elif (voltagerou < 11.0):
                msg2 = "25"

            socketclient2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socketclient2.connect(('192.168.43.1', 7802))
            socketclient2.send(msg2.encode())
            socketclient2.close()
            #  voltage = voltage + 0.1
            # time.sleep(1)
            break


    elif confirmer == "prise de controle":
        while True:
            # mot=str()
            socketserver.listen(5)
            client, address1 = socketserver.accept()
            # print("{} connected2".format(address1))
            #  print("attender")
            vitesse = client.recv(1024).decode()
            if (vitesse == "sortie" or vitesse == "batterie"):
                break
            elif (vitesse != "prise de controle"):
                vitesse1 = vitesse.split("/")
                if(vitesse[0]=='sortie'):
                    break
                Convert_Vitesse_axe_x = float(vitesse1[0])
                Convert_Vitesse_axe_y = float(vitesse1[1])

                if (Convert_Vitesse_axe_x > 0.0 and Convert_Vitesse_axe_x < 8.0):
                    pwm = int(16 * (7.0 - Convert_Vitesse_axe_x))
                    print(pwm, " m/s")
                    rpwm.ChangeDutyCycle(0)
                    lpwm.ChangeDutyCycle(pwm)
                    if (Convert_Vitesse_axe_y == 1):

                        if (droide_deg0 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens hourair")

                    #  print("vide")
                    elif (Convert_Vitesse_axe_y == 2):
                        if (droide_deg40 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide2 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide2  sens hourair")
                        droide_deg0 = True
                    # print("vide")
                    elif (Convert_Vitesse_axe_y >= 3):
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg40 = True
                    elif (Convert_Vitesse_axe_y == -1):
                        if (gauche_deg0 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("gauche1 sens hourair")
                    elif (Convert_Vitesse_axe_y == -2):
                        if (gauche_deg40 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("gauche2 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens hourair")
                        droide_deg0 = True

                    elif (Convert_Vitesse_axe_y <= -3):
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg40 = True

                    else:
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg0 = False
                        droide_deg40 = False
                        gauche_deg0 = False
                        gauche_deg40 = False
                        print("avant pur")
                elif (Convert_Vitesse_axe_x < 0.0 and Convert_Vitesse_axe_x > -8.0):
                    pwm = int(16 * (7.0 - (Convert_Vitesse_axe_x * -1.0)))
                    print(pwm, " m/ss")
                    rpwm.ChangeDutyCycle(pwm)
                    lpwm.ChangeDutyCycle(0)
                    if (Convert_Vitesse_axe_y == 1):
                        if (droide_deg0 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens hourair")

                    #  print("vide")
                    elif (Convert_Vitesse_axe_y == 2):
                        if (droide_deg40 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide2 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide2  sens hourair")
                        droide_deg0 = True
                    # print("vide")
                    elif (Convert_Vitesse_axe_y >= 3):
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg40 = True
                    elif (Convert_Vitesse_axe_y == -1):
                        if (gauche_deg0 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("gauche1 sens hourair")
                    elif (Convert_Vitesse_axe_y == -2):
                        if (gauche_deg40 == True):
                            GPIO.output(in1, GPIO.LOW)
                            GPIO.output(in2, GPIO.HIGH)
                            p.ChangeDutyCycle(15)
                            print("gauche2 sens antihourair")
                        else:
                            GPIO.output(in1, GPIO.HIGH)
                            GPIO.output(in2, GPIO.LOW)
                            p.ChangeDutyCycle(15)
                            print("droide1 sens hourair")
                        droide_deg0 = True

                    elif (Convert_Vitesse_axe_y <= -3):
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg40 = True

                    else:
                        GPIO.output(in1, GPIO.LOW)
                        GPIO.output(in2, GPIO.LOW)
                        p.ChangeDutyCycle(0)
                        droide_deg0 = False
                        droide_deg40 = False
                        gauche_deg0 = False
                        gauche_deg40 = False
                        print("arrier pur")
    elif confirmer == "Radar":
        print("pageRader")
        socketserver.listen(1)
        clientRadar, address1 = socketserver.accept()
        print("{} connected".format(address1))
        print("attender")
      #  voltage = 12

        etat_radar = clientRadar.recv(1024).decode()
        etat_radar = etat_radar.split("#")
        if (etat_radar[0] == "Activer"):
            db.execute(f'''update gestionvoiture set radar = '30' where  Smartcar = 'Smartcar' ''')
            db.commit()
            while True:
                socketserver.listen(1)
                clientRadar, address1 = socketserver.accept()
                print("{} connected".format(address1))
                print("attender")
           # voltage = 12
                acceptationchanger = clientRadar.recv(1024).decode()
                acceptationchanger = acceptationchanger.split("#")
                if (acceptationchanger[0] == "Confirmer"):
                    print("acception changer ")
                    enrigValeur = "'" + acceptationchanger[1] + "'"
                    db.execute(f'''update gestionvoiture set radar = {enrigValeur} where  Smartcar = 'Smartcar' ''')
                    db.commit()
                elif (acceptationchanger[0] == "Annuler"):
                    print("annuler")
                elif (acceptationchanger[0] == "Stop"):
                    print("stop")
                    db.execute(f'''update gestionvoiture set radar = 'desactiver' where  Smartcar = 'Smartcar' ''')
                    db.commit()

                else:
                    break
        elif etat_radar[0] == "desactiver":
                 db.execute(f'''update gestionvoiture set radar = 'desactiver' where  Smartcar = 'Smartcar' ''')
                 db.commit()
        else:
            break
            break

           # valeur_obstagle = clientRadar.recv(1024).decode()
         #   while True:
          #      ad_value = readadc(A1_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
           #     v = (ad_value / 1023.0) * 3.3
            #    dist = 13 * pow(v, -1)
            #    dist1 = int(dist)
             #   data2 = int(valeur_obstagle)
             #   if (data2 > 30 or data2 < 4):
              #      print("Obstacle")
             #       break
            #    elif (data2 >= dist1):
                    #             #       GPIO.output(load, GPIO.HIGH)
             #       print("distance superieur")
            #    print("***********")
            #    print(" distance est: " + str("%.1f" % dist1) + "Cm")
             #   print("***********")
             #   print(' ')
             #   time.sleep(0.7)

    #   CardRead =SimpleMFRC522()
    #    id = CardRead.read_id()
    #  print("ok")
    # socketclient2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socketclient2.connect(('192.168.43.1', 7810))
    # msg=id
    # socketclient2.send(msg.encode())
    # socketclient2.close()
    #

    elif (confirmer == "inscription fils"):
        socketserver.listen(1)
        inscription, address1 = socketserver.accept()
        mesage = inscription.recv(1024).decode()
        print(mesage)
        table_inscrir = mesage.split("#")

        while True:
            s = socket.socket()  # Create a socket object
            portimg = 21568
            s.bind(('', portimg))
            print("image")
            s.listen(1)
            conn, addr = s.accept()
            print('client connected ... ', addr)
            imagename = str(table_inscrir[0]) + ".png"
            f = open(imagename, 'wb')

            while True:
                data = conn.recv(9999999)
                if not data: break
                print(data)
                f.write(data)
            # print('writing file ....')

            f.close()
            print("finished writing file")
            conn.close()
            print('client disconnected')
            with open(imagename, "rb") as binary_image:
                binary_code = binary_image.read()
            db.execute("insert into smartcardpfils(prenom,dateN,poid,sexe,image) values(?,?,?,?,?)", (
            str(table_inscrir[0]), str(table_inscrir[1]), int(table_inscrir[2]), str(table_inscrir[3]), binary_code))
            db.commit()
            break
    elif confirmer == "Page3":
                print("Page3")
                var = db.execute("select * from smartcardpfils2")
                for record in var:
                    print(record[0], record[1], record[2], record[3])
                    socketclient2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    socketclient2.connect(('192.168.43.1', 7811))
                    msg = str(record[0]) + "#" + str(record[1]) + "#" + str(record[2]) + "#" + str(
                        record[3]) + "#" + str(record[6])
                    socketclient2.send(msg.encode())

                #  sleep(0.5)
                socketclient2.close()

                while True :
                 print("listen")
                 socketserver.listen(5)
                 client, address1 = socketserver.accept()
                 option = client.recv(1024).decode()
                 print(option)
                 listoption = option.split("#")
                 print(listoption[0])
                 print(listoption[1])
                # print(option)
                 if listoption[0]=="inscription":

                  print("fils")
                  socketserver.listen(1)
                  inscription, address1 = socketserver.accept()
                  mesage = inscription.recv(1024).decode()
                  print(mesage)
                  if mesage=="RFID" :
                      try:
                          while True:
                              # print("Bonjour")

                              id, txt = CardRead.read()

                              if id == None:
                                  print("salut")
                                  gpio.output(load, gpio.LOW)



                              else:

                                  print("ok")
                                  socketclient2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                  socketclient2.connect(('192.168.43.1', 7810))
                                  msg2 = str(id)
                                  print(msg2)
                                  socketclient2.send(msg2.encode())
                                  socketclient2.close()
                                  socketserver.listen(1)
                                  inscription, address1 = socketserver.accept()
                                  mesage = inscription.recv(1024).decode()
                                  table_inscrir = mesage.split("#")
                                  break
                              #
                              #  if gpio.input(load):
                              #     gpio.output(load,gpio.LOW)
                              #    print("load Statu OFF")
                              #   gpio.output(load,gpio.HIGH)
                              #            time.sleep(1)
                              # else:
                              #  gpio.output(load,gpio.HIGH)
                              #  print("load Statu ON")
                              #  time.sleep(1)


                      except KeyboardInterrupt:
                          gpio.cleanup()


                  while True:
                     s = socket.socket()  # Create a socket object
                     portimg = 21568
                     s.bind(('', portimg))
                     print("image")
                     s.listen(1)
                     conn, addr = s.accept()
                     print('client connected ... ', addr)
                     imagename = str(table_inscrir[0]) + ".jpeg"
                     f = open(imagename, 'wb')

                     while True:
                         data = conn.recv(9999999)
                         if not data: break
                         print(data)
                         f.write(data)
                     # print('writing file ....')

                     f.close()
                     print("finished writing file")
                     conn.close()
                     print('client disconnected')
                     with open(imagename, "rb") as binary_image:
                         binary_code = binary_image.read()
                     db.execute("insert into smartcardpfils2(prenom,dateN,poid,sexe,image,path) values(?,?,?,?,?,?)", (
                     str(table_inscrir[0]), str(table_inscrir[1]), int(table_inscrir[2]), str(table_inscrir[3]),
                     binary_code, str(table_inscrir[4])))
                     db.commit()
                     break


                # socketserver.listen(5)
                # client, address1 = socketserver.accept()
                # option = client.recv(1024).decode()

                 msg="'"+str(listoption[1])+"'"
                # print(msg)
                 if listoption[0]=="Supprimer":
                    print("comptesupprimer")
                    db.execute(f'''delete  from smartcardpfils2 where prenom ={msg}''')
                    db.commit()
                   # db.close()
                 elif listoption[0]=="Bloquer":
                     db.execute(f'''update smartcardpfils2 set bolquager = 'Bloquer' where  prenom = {msg} ''')
                     db.commit()
                     print("bloquer")
                 elif listoption[0]=="Debloquer":
                     db.execute(f'''update smartcardpfils2 set bolquager = 'Debloquer' where  prenom = {msg} ''')
                     db.commit()
                     print("Debloquer")
                 elif listoption[0]=="Profile" :
                     print("ok")

                     socketserver.listen(5)
                     client, address1 = socketserver.accept()
                     msgoprionprof = client.recv(1024).decode()
                     verifer=msgoprionprof.split("#")
                     if verifer[0]=="limitationvitesse" :
                         socketserver.listen(5)
                         client, address1 = socketserver.accept()
                         msgoprionprof = client.recv(1024).decode()
                         tablemsg=msgoprionprof.split("#")
                         colon=int(tablemsg[0])
                         cond="'"+str(tablemsg[1])+"'"
                         db.execute(f'''update smartcardpfils2 set limitation_vitesse = {colon} where  prenom = {cond} ''')
                         db.commit()
                         print("confirmer")
                     elif verifer[0] == "modifierprofile ":
                         print("salut")
                         socketserver.listen(1)
                         inscription, address1 = socketserver.accept()
                         mesage = inscription.recv(1024).decode()
                         print(mesage)
                         table_inscrir = mesage.split("#")

                         while True:
                             s = socket.socket()  # Create a socket object
                             portimg = 21568
                             s.bind(('', portimg))
                             print("image")
                             s.listen(1)
                             conn, addr = s.accept()
                             print('client connected ... ', addr)
                             imagename = str(table_inscrir[0]) + ".jpeg"
                             f = open(imagename, 'wb')

                             while True:
                                 data = conn.recv(9999999)
                                 if not data: break
                                 print(data)
                                 f.write(data)
                             # print('writing file ....')

                             f.close()
                             print("finished writing file")
                             conn.close()
                             print('client disconnected')
                             cond="'"+str(table_inscrir[5])+"'"
                             path="'"+str(table_inscrir[4])+"'"
                             sexe="'"+str(table_inscrir[3])+"'"
                             with open(imagename, "rb") as binary_image:
                                 binary_code = binary_image.read()
                             sqlimg=bytearray(binary_code)
                            # db.execute( f'''update smartcardpfils2 set prenom = {str(table_inscrir[0])} where prenom={cond}  ''')
                             db.execute( f'''update smartcardpfils2 set dateN = {str(table_inscrir[1])}  where prenom={cond}  ''')
                             db.execute( f'''update smartcardpfils2 set poid = {str(table_inscrir[2])}  where prenom={cond}  ''')
                             db.execute( f'''update smartcardpfils2 set sexe = {sexe}  where prenom={cond}  ''')
                            # db.execute( f'''update smartcardpfils2 set image = {sqlimg}  where prenom={cond}  ''')
                             db.execute( f'''update smartcardpfils2 set path = {path}  where prenom={cond}  ''')

                             db.commit()
                             print("profile modifier")
                             break
                     elif verifer[0]=="limitation" :
                         print(verifer[1])
                         prenomfilsvit = "'"+str(verifer[2])+"'"
                         my_timer = int(verifer[1])
                         countdown_thread = threading.Thread(target=countdown)
                         countdown_thread.start()
                         db.execute(
                             f'''update smartcardpfils2 set bolquager = 'bloquer' where  prenom = {prenomfilsvit} ''')
                         db.commit()
                     #    print(prenomfilsvit)
                       """  while True :
                          if (terminer == True):
                             db.execute(
                                 f'''update smartcardpfils2 set bolquager = 'bloquer' where  prenom = {prenomfilsvit} ''')
                             db.commit()
                             print("nnn")
                             break

                         print(("config"))
"""


print("Close")
client.close()
db.close()
socketserver.close()

# from socket import *

#                GPIO.output(load, GPIO.LOW)


# port init


# def main():
#         init()
#        time.sleep(2)
#         print("will detect voltage")
#        while True:
#                 ad_value = readadc(AO_pin, SPICLK, SPIMOSI, SPIMISO, SPICS)
#               voltage= ad_value*(3.3/1024)*5
#               phoneServer=socket(AF_INET, SOCK_STREAM)
#               phoneServer.connect(192.168.43.1:7801')
#              phoneServer.send(voltage.encode())
#             phoneServer.close()
#             print("***********")
#            print (" Voltage is: " + str("%.2f"%voltage)+"V")
#           print("***********")
#           print#
# time.sleep(0.5)


# if __name__ =='__main__':
#        try:
#           main()
#      except KeyboardInterrupt:
#             pass
# GPIO.cleanup()


#
# cmd ="python Cle_projet.py"
# p= subprocess.Popen(cmd,shell=False)