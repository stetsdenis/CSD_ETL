# CSD_ETL
Example of ETL flow using Dataddo APIs (with OAuth 2.0 authentication).

Il flusso ETl viene gestito tramite interfacciamento con API Dataddo. 

Tip n°1 : Al fine di semplificare la chiamata alle loro API, creare un utenza Dataddo con registrazione "diretta", ovvero senza usare garanti esterni (Google, Facebook, ecc...).

La web app si compone di 3 interfacce grafiche con cui l'utente può interagire:

1)Login : permette all'utente di "lanciare" autenticazione tramite protocollo OAuth 2.0, abbiamo allora due scenari:
    1.1)Login -> oAuthID non esistente -> crea nuova oAuth (processo di handshake con server Google);
    1.2)Login -> oAuthID esistente -> usa prima authorizer disponibile per G4A;

2)CreateFlow : interfaccia front end che permette la selezione di metriche e dimensioni (gestione javascript con promise asincrone).
               Tutte le logiche di autenticazione e creazione del flow sono gestite in backend.

3)Success : Redirect su pagina di successo con link verso destination (in questo caso Google Sheets).



