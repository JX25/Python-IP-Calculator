import sys
import socket
import json
import netifaces
import ipaddress
from netaddr import IPNetwork, IPAddress


def ipCalculator(ipAddress):
    ip = IPNetwork(ipAddress)
    #Informacja o ip:
    ipInfo = "Dane dla adresu: "+ipAddress
    #Adres sieci:
    siecD = str(ip.network)
    siecB = str(ip.network.bits())
    ipInfo += "\nAdres sieci (dziesietnie): " + siecD
    ipInfo += "\nAdres sieci (binarnie): " + siecB
    #Klasa sieci:
    klasa =getIPClass(ipAddress)
    if klasa == "nie mozna okreslic klasy adresu":
        print("Niepoprawna maska dla podanego adresu")
        return
    ipInfo += "\nKlasa adreesu: " + klasa
    #Maska sieci dziesietnie i binarnie
    maskaD = str(ip.netmask)
    maskaB = str(ip.netmask.bits())
    ipInfo += "\nMaska sieci (dziesietnie): " + maskaD
    ipInfo += "\nMaska sieci (binarnie): " + maskaB
    #Adres rozgloszeniowy dziesietnie i binarnie
    broadcastD = str(ip.broadcast)
    broadcastB = str(ip.broadcast.bits())
    ipInfo += "\nAdres rozgloszeniowy sieci (broadcast) (dziesietnie): " + broadcastD
    ipInfo += "\nAdres rozgloszeniowy sieci (broadcast) (binarnie): " + broadcastB
    #Adres pierwszego hosta dziesietnie i binarnie
    firstHostD = str(ip.network+1)
    firstHostB = str((ip.network+1).bits())
    ipInfo += "\nAdres pierwszego hosta (dziesietnie): " + firstHostD
    ipInfo += "\nAdres pierwszego hosta (binarnie): " + firstHostB
    #Max ilosc hostow w danej podsieci dziesietnie i binarnie
    maxHostsD = str(int(ip.hostmask)-1)
    maxHostsB = "{0:08b}".format(int(ip.hostmask)-1)
    ipInfo += "\nMaksymalna ilosc hostow w danej sieci (dziesietnie): " + maxHostsD
    ipInfo += "\nMaksymalna ilosc hostow w danej sieci (binarnie): " + maxHostsB
    #Wyswietlanie na ekranie
    print(ipInfo)
    #Zapis do pliku
    ipInfoJSON2 = {
        "ip": ipAddress,
        "networkIPdecimal": siecD,
        "networkIPbinary": siecB,
        "addressClass": klasa,
        "subnetmaskDecimal": maskaD,
        "subnetmaskBinary": maskaB,
        "broadcastDecimal": broadcastD,
        "broadcastBinary": broadcastB,
        "firstHostDecimal": firstHostD,
        "firstHostBinary": firstHostB,
        "maxHostsDecimal": maxHostsD,
        "maxHostsBinary": maxHostsB
    }
    with open('ipInfo.json', 'w') as outfile:
        json.dump(ipInfoJSON2, outfile, indent=2)


def checkIP(addressIP):
    addressIP = addressIP.split("/")
    adres = addressIP[0]
    maska = int(addressIP[1])
    if adres.count(".") != 3: return False
    oktety = [int(n) for n in adres.split(".")]
    if maska <= 0 or maska > 32: return False
    if oktety[0] < 0 or oktety[0] > 255: return False
    if oktety[1] < 0 or oktety[1] > 255: return False
    if oktety[2] < 0 or oktety[2] > 255: return False
    if oktety[3] < 0 or oktety[3] > 255: return False
    return True


def getIPClass(ipAddress):
    addressIP = ipAddress.split("/")
    adres = addressIP[0]
    maska = int(addressIP[1])
    oktety = [int(n) for n in adres.split(".")]
    if oktety[0] >= 0 and oktety[0]<=127 and maska>=8:
        if oktety[0] == 10:
            return "prywatny klasa A"
        else:
            return "publiczny klasa A"
    if oktety[0] >=128 and oktety[0] <= 191 and maska>=16:
        if oktety[0] == 172 and oktety[1] >= 16 and oktety[1] <= 31:
            return "prywatny klasa B"
        else:
            return "publiczny klasa B"
    if oktety[0] >= 192 and oktety[0] <=223 and maska>=24:
        if oktety[0] == 192 and oktety[1] == 168:
            return "prywatny klasa C"
        else:
            return "publiczny klasa C"
    if oktety[0] >= 224 and oktety[0] <= 239:
        return "publiczny klasa D"
    if oktety[0] >= 240 and oktety[0] <= 255:
        return "publiczny klasa E"
    return "nie mozna okreslic klasy adresu"


def getIPaddress():
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as jsonData:
            addressIP = json.loads(jsonData.read())
            addressIP = addressIP["ipAddress"]
            if checkIP(addressIP) == False:
                print("Podany adres IP jest nie poprawny!")
                addressIP = "error"
                return addressIP
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
        except socket.error:
            print("Problem z uzyskaniem ip")
            exit(1)
        addressIP = s.getsockname()[0]
        for i in netifaces.interfaces():
            try:
                if( addressIP == netifaces.ifaddresses(i)[netifaces.AF_INET][0]['addr']):
                    mask = netifaces.ifaddresses(i)[netifaces.AF_INET][0]['netmask']
                    mask = IPAddress(mask).netmask_bits()
                    addressIP += "/" + str(mask)
                    addressIP = ipaddress.IPv4Network(addressIP)
            except: pass
        s.close()
    return addressIP


def main():
    ip = getIPaddress()
    if ip == "error":
        print("Nie mozna okreslic wlasnosci podanego adresu!")
        return
    else:
        ipCalculator(ip)


main()
