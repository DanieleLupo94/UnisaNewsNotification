import requests as req
from lxml import html
import time

''' Si collega alla pagina url e controlla le news.
	Il campo cds viene usato per personalizzare le notifiche ed usare i file giusti.
	In caso di news viene inviata una notifica tramite IFTTT.
'''
def controllaCDS(url, cds):
	r = req.get(url)
	tree = html.fromstring(r.content)
	# La lista delle news è contenuta in un tag ul
	titoliNews = tree.xpath('//ul[@class="event-list event-left"]/li/div[@class="info"]/h4/a//text()')
	if len(titoliNews) == 0:
		# nella pagina unisa.it usano un h3 invece di un h4
		titoliNews = tree.xpath('//ul[@class="event-list event-left"]/li/div[@class="info"]/h3/a//text()')
	t = "### [" + time.asctime(time.localtime(time.time())) + "] Controllo news " + cds + " ###"
	scriviLog(t)
	# Apro il file delle news e leggo dall'inizio
	fileNews = open(getNomeFileNews(cds), "a+")
	fileNews.seek(0)
	lines = fileNews.readlines()
	fileNews.close()
	# Questo bool serve a sapere se sono state trovate notizie nuove
	notifica = False
	# Se la differenza fra le notizie presenti nel file e quelle trovate è < 0 allora di sicuro ci sono notizie nuove
	if ((len(lines) - len(titoliNews)) < 0):
		scriviLog("Non ci sono news da " + cds + " nel file quindi le aggiungo tutte.")
		for titolo in titoliNews:
			scriviNews(titolo, cds)
			notifica = True
	else:
		# Scorro le notizie (entrambe) e le confronto. Se sono diverse allora dico che ci sono novità.
		# So già che dare per assodato che la notizia a quella posizione è diversa solo se ci sono nuove notizie potrebbe non essere corretta.
		# Lo scopo è di notificare che la lista è cambiata quindi i falsi positivi non sono gravi.
		for indice in range(0, len(titoliNews)):
			line = pulisci(lines[len(lines) - len(titoliNews) + indice])
			titolo = pulisci(titoliNews[indice])
			if line != titolo:
				scriviNews(titoliNews[indice], cds)
				notifica = True
	if notifica:
		notificaIFTTT("Ci sono novità " + cds)
		scriviLog("Ci sono notifiche " + cds)
	else:
		scriviLog("Non si sono notifiche " + cds)
	
	
def getNomeFileNews(cds):
	return "./news" + cds

def scriviLog(testo):
	fileLog = open("./log", "a+")
	fileLog.write(testo)
	fileLog.write("\n")
	fileLog.close()

def scriviNews(testo, cds):
	nomeFile = "./news" + cds
	testo = testo.strip()
	fileNews = open(nomeFile, "a+")
	fileNews.write(testo)
	fileNews.write("\n")
	fileNews.close()
	
def pulisci(testo):
	testo = testo.replace(" ", "")
	testo = testo.strip()
	return testo

def notificaIFTTT(testo):
	urlWebhook = 'https://maker.ifttt.com/trigger/inviaNotifica/with/key/crgmhm7kuG2plVg8e7W1_V'
	req.post(urlWebhook, json={'value1': testo})
	urlWebhook = 'https://maker.ifttt.com/trigger/notificaUnisa/with/key/c0heZrBg8aD-o0gQRPWB6ULNbiG2_rvcz-rfQx2qanr'
	req.post(urlWebhook, json={'value1': testo})

def checkConnection(host='http://www.google.it'):
    try:
        req.get(host)
        return True
    except:
        return False

def main():
	while not checkConnection():
		time.sleep(60 * 10) # attesa di 10 minuti
	controllaCDS('https://corsi.unisa.it/informatica', 'informatica')
	controllaCDS('https://corsi.unisa.it/biologia', 'biologia')
	controllaCDS('https://corsi.unisa.it/scienze-biologiche', 'scienzeBiologiche')
	controllaCDS('https://web.unisa.it/home/news', 'generali')
	time.sleep(60 * 60 * 1) # controllo ogni ora
	main()

main()
