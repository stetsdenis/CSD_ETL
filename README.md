# CSD_ETL
Example of ETL flow using Dataddo APIs (with OAuth 2.0 authentication).

The ETl flow is managed through interfacing with the Dataddo API.

#Tip: In order to simplify the API call, create a Dataddo user with "direct" registration, meaning without using external guarantors (Google, Facebook, etc.).

The web app consists of 3 graphical interfaces with which the user can interact:

-Login: Allows the user to initiate authentication via the OAuth 2.0 protocol. There are two scenarios: 
    1.1) Login -> non-existent OAuthID -> create new OAuth (handshake process with Google server); 
    1.2) Login -> existing OAuthID -> use the first available authorizer for G4A.

-CreateFlow: Front-end interface that allows the selection of metrics and dimensions (managed with JavaScript using asynchronous promises). 
             All authentication and flow creation logic is handled in the backend.

-Success: Redirect to a success page with a link to the destination (in this case, Google Sheets).



