from django.shortcuts import render,redirect
import requests
import json

from django.middleware.csrf import get_token
from django.http import JsonResponse

from decouple import Config

#******************START: qui definisco variabili e costanti globali che si scambiano le funzioni******************

#credenziali Dataddo
CREDENTIAL = Config("CREDENTIAL")
OAUTH_ID_GOOGLE_SHEETS = Config("OAUTH_ID_GOOGLE_SHEETS")
PROPERTY_ID = Config("PROPERTY_ID")
ACCOUNT_ID = Config("ACCOUNT_ID")

#info dell'app creata su google developer console
OAUTH_CONFIG = Config("OAUTH_CONFIG")

#esempio per rif. callback
# OAUTH_CONFIG = {
#     "config": {
#         "clientId": "il_tuo_client_id",
#         "clientSecret": "il_tuo_client_secret",
#         "redirectUri": "http://localhost:8000/login/google_analytics_callback/",
#         "serviceId": "google_analytics4_custom"
#     }
# }

#variabili dell'header dataddo
access_token = ''
realm_id = ''
provider = ''

#base per chiamate API dataddo
API_URL = "https://headless.dataddo.com/customer-api/v1"


#******************END: qui definisco variabili e costanti globali che si scambiano le funzioni********************

#ridirect per landing page di successo
def redirectSuccess(request):
    return render(request, 'success.html')
# Esegui il reindirizzamento alla URL per startare il flow

def start_flow(request):
    return render(request, 'createFlow.html')

#gestione del login e della callback per l'Oauth 
def login_handler(request, provider=None):
    if provider == None:                                        #se provider vuoto allora è una richiesta di login diretta
        return render(request, 'login.html')  
     
    elif provider == 'google_analytics_callback':               #se provider uguale a GA4, gestisci callback e poi rimanda a pagina per definizione flow      
        google_analytics_callback(request)  
        return redirect('/startFlow')

#step 1: gestisce inzio oAuth 2.0 per authorizer Dataddo
def startAuthentication(request):
    #dichiaro utilizzo di variabili globali per inizializzazione
    #verrà fatto qui e saranno usate successivamente dalle altre funzioni 
    global access_token
    global realm_id
    global provider

    global oAuthId

    #definite le var sopra, posso definire il dict. dell'header
    global header

    # Effettua il login su Dataddo e ottieni il redirect URL per l'autenticazione OAuth
    #*************START: INIT variabili globali*************
    response_login = login_dataddo()
    access_token = response_login.get("access_token")
    realm_id = str(response_login.get("realm_id"))   #no int, parsa a stringa
    provider = response_login.get("provider")
    #*************END: INIT variabili globali***************

    #header con i dati per le chiamate al server dataddo, forniti dopo log
    header = {
            "Authorization": "Bearer "+ access_token,
            "X-realm-id": realm_id,
            "X-provider": provider
        }
    
    #controlla se esiste già un autenticatore per google_analytics4_custom 
    response = requests.get(url=API_URL+"/connectors/google_analytics4/actions/authorization", headers=header)

    #seconda condizione valuta se risposta json valorizzata
    if response.status_code == 200 and response.json():                     
        oAuthId  = response.json()[0]["id"]  #prendi il primo authorizer disponibile
        #manda reply json per rimandare a inizio creazione flow
        return JsonResponse({'redirect_url': '/startFlow/'})            
    else:
        # Ottieni l'URL di reindirizzamento per l'autenticazione OAuth con Google
        redirect_url = get_redirect_url()
        #manda reply json per continuo auth
        return JsonResponse({'redirect_url': redirect_url})  

        # # Apri il browser per l'autenticazione OAuth con Google
        # return webbrowser.open(redirect_url)

#esegue il login con le credenziali per abilitare accesso alle API
def login_dataddo():
    try:
        response = requests.post(url=API_URL+"/auth", json=CREDENTIAL)
        if response.status_code == 200:
            return response.json()
        else:
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise

#gestisce inizio autenticazione oAuth 2.0  ---> STEP 1
def get_redirect_url():
    try:
        response = requests.post(url=API_URL+"/services/google_analytics4_custom/oauth-request-url", json=OAUTH_CONFIG, headers=header)
        if response.status_code == 200:
            return response.json().get("url")
        else:
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise

#proseguo autenticazione oAuth 2.0, termina auth e ottieni oAuthId----> STEP 2 
def google_analytics_callback(request):
    global oAuthId

    #prendo url con code fornito da Google
    callback_url = request.build_absolute_uri()

    #ho bisogno di payload che contiene sia OAUTH_CONFIG che l'url
    oauth_config_callback = OAUTH_CONFIG.copy()             #copio OAUTH_CONFIG in nuova dict.
    oauth_config_callback["callbackUrl"] = callback_url     #aggiungo url 

    try:
        response = requests.post(url=API_URL+"/services/google_analytics4_custom/oauth-process-callback", json = oauth_config_callback, headers=header)
        if response.status_code == 200:
            oAuthId = response.json().get("id")             # <------- ottengo id authorizer
            print(oAuthId)   #per debug
            return response.json()
        else:
            print(response)
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise

#def metodo gestione token, NB tutte le POST HTML hanno bisogno di gestione con csrf_token
def csrf_token(request):

    # Otteniamo il token CSRF dal middleware CSRF
    csrf_token = get_token(request)

    # Restituiamo il token CSRF come risposta JSON
    return JsonResponse({'csrfToken': csrf_token})

def get_dimensions(request):
    
    # Dati per la richiesta POST
    data = {
        'oAuthId': oAuthId,
        'propertyId': PROPERTY_ID               
    }

    # Esegui la richiesta POST per ottenere le dimensioni
    response = requests.post(API_URL+'/connectors/google_analytics4/actions/dimension', json=data, headers=header)
    dimensions = response.json()

    #ritorno al front end per gestione Javascript
    return JsonResponse({'dimensions': dimensions})

def get_metrics(request):

    # Dati per la richiesta POST
    data = {
        'oAuthId': oAuthId,
        'propertyId': PROPERTY_ID
    }

    # Esegui la richiesta POST per ottenere le metriche
    response = requests.post(API_URL+'/connectors/google_analytics4/actions/metric', json=data, headers=header)
    metrics = response.json()

    #ritorno al front end per gestione Javascript
    return JsonResponse({'metrics': metrics})

def create_destination():
    # Dati per la richiesta POST
    data = {
            "type":"google_sheets",
            "allow_empty":"true",
            "destinationId":"google_sheets",
            "label":"Google Sheets",
            "oAuthId": OAUTH_ID_GOOGLE_SHEETS          #valore costante per test
            }

    try:
        response = requests.post(url=API_URL+"/destinations", json=data, headers=header)
        if response.status_code == 201:
            return response.json()
        else:
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise

def create_source(metric, dimension):

    data = {"connectorId":"google_analytics_4",
            "templateId":"index",
            "allow_empty":"true",
            "oAuthId":oAuthId,
            "accountId": ACCOUNT_ID,
            "propertyId": PROPERTY_ID,
            "usePropertyId":"false",
            "useInsertDate":"false",
            "useDataddoHash":"false",
            "label":"Google Analytics 4",
            "metric": metric,
            "dimension": dimension,
            "sync_frequency":"month",
            "day_of_week":"2",
            "day_of_month":"1",
            "hour":"6",
            "minute":"5",
            "timezone":"UTC",
            "dateRange":"{{1y1}}",          #365 g di storico dati 
            "dateRangePreview":"{{1d1}}",
            "search":"",
            "request":"null",
            "type":"googleAnalytics4",
            "storageStrategy":"incremental"}

    try:
        response = requests.post(url=API_URL+"/connectors/google_analytics_4/create-source", json=data, headers=header)
        if response.status_code == 200:
            return response.json()
        else:
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise

def createFlow(request):

    data = json.loads(request.body)         # Ottieni i dati inviati dal frontend come un dizionario --> VALORI SELEZIONATI DA UTENTE
    metrics = data.get('metrics',[])        # Ottieni i valori di 'metrics'
    dimensions = data.get('dimensions',[])  # Ottieni i valori di 'dimensions'

    #destinazione va creata utilizzando un oAuth che autorizzi Google Sheets    <--- TBD !!!
    storageId = create_destination().get("id")

    #ho già un authorizer per sorgente, definisco Source
    sources = create_source(metric=metrics,dimension=dimensions).get("id")

    #payload per creazione 
    data = {"write_mode":"insert",
            "write_header":"true",
            "spreadsheet_new":"true",
            "spreadsheet_document_name":"CSD Flow SpreadSheet Result",
            "spreadsheet_sheet_name":"-->RESULTS HERE<---",
            "stream":"false",
            "sources":[sources],
            "operations":[],
            "storageId":storageId,
            "app":"null",
            "label":"Unnamed Flow",
            "rules":[],
            "uniqueColumns":[],
            "loadImmediately":"true"}

    try:
        response = requests.post(url=API_URL+"/flows", json=data, headers=header)
        if response.status_code == 201:
            return JsonResponse({'redirect_url': '/success/'})      #tutto okay ritorna richiesta di ridirect a pagina successo
        else:
            raise
    except requests.exceptions.RequestException as e:
        print('Errore :', e)
        raise
