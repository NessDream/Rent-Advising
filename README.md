(english version below)


### Objectif de l'outil
Ce projet vise à fournir une aide au choix d'un logement via une page web interactive. Affiche un plan de ville où les principaux points (stations de métro) sont évalués sur deux critères :
- distance au lieu de travail
- prix des logments au mètre carré  

Le plan facilite donc la zone de recherche, avec un code couleur intuitif.

### Utilisation
Il suffit de lancer le fichier FLASK.ipynb, et de se rendre sur le port local 5000 (simplement cliquer sur le lien fourni en output de cellule).  
Sur la page d'accueil, saisir l'adresse de son lieu de travail (région parisienne uniquement pour le moment), puis cliquer sur OK.

## Réalisation

#### APIs
Les API utilisées sont les suivantes :
- [Geo API](https://geo.api.gouv.fr/adresse) : Permet de récupérer les coordonnées GPS d'un point à partir d'une adresse en texte libre
- [CQUEST](https://www.data.gouv.fr/fr/reuses/micro-api-dvf-demande-de-valeurs-foncieres/): Permet de récupérer le prix moyen au mètre carré des derières ventes effectuées autour d'un point donnée (via ses coordonnées GPS).
- [Navitia](https://www.navitia.io) : Permet de récupérer le temps de transport entre deux points GPS

####  Fichiers
Les différents fichiers sont les suivants :
- **FLASK.ipynb** : Notebook jupyter, pour faciliter la mise en place du serveur Flask.  
    Importe les fonctions du fichier all_functions.py, crée l'application Flask, affiche les pages html et css sur le port par défaut, 5000
- **all_functions.py** : implémente toutes les fonctions utilisées, qui font appel aux diverses API. On a par exemple :
    - get_coordonnees(adresse) : renvoie des coordonnées GPS à partir d'un adresse en string, en utilisant l'api Geo
    - get_price(coordonnees) : renvoie le prix moyen au mètre carré d'un point GPS, en utilisant l'api Cquest
    - score_price(price) : renvoie un score entre 0 et 1 d'un prix
    - score_duration(duration) : renvoie un score entre 0 et 1 d'un temps de transport
    - score_station(duration, price) : renvoie un score entre 0 et 1 d'une station, en faisant la moyenne harmonique du prix et de la durée de transport
    - get_station(coordonnees) : renvoie les stations à moins d'un certain temps de transport, avec toutes leurs caractéristiques (nom, prix, durée jusqu'à l'adresse sélectionnée, coordonnees)
- templates/**index.html** : page d'accueil de l'application. Contient un form où l'utilisateur entre son adresse en texte libre.
- templates/**map.html** : page présentant la carte interactive (leaflet) à l'utilisateur.
    Contient un bouton permettant de retourner à l'accueil.  
    La majorité du code javascript a été emprunté à un template fourni par navitia.  
- static/CSS/**main.css** : contient le css du style des pages

En plus de ces fichiers directement liés à l'application, on retrouve quelques fichiers expliquant notre approche pour la réalisation de celle-ci.
- **Scoring.ipynb** : notebook présentant la mise au point des modèles de scoring
- **Prix des stations.ipynb** : notebook utilisant l'API Cquest pour récupérer les données de prix de stations. Celles-ci ont été enregistrées en statique dans le fichier data/station_price_full.pkl afin d'améliorer le temps de chargement de la page, cette API étant assez longue à répondre pour beaucoup de demandes.

  
    
      
        
        
        
**################### english version ###################**
# Rent Advising

### Tool objective
This project aims to provide assistance in the choice of accommodation via an interactive web page. Displays a city map where the main points (metro stations) are evaluated on two criteria :
- distance from the workplace
- housing prices per square metre  

The map makes the search area easy to navigate, with intuitive colour coding.

### Usage
Just launch the FLASK.ipynb file, and go to the local port 5000 (just click on the link provided in cell output).  
On the home page, enter the address of his workplace (Paris area only for the moment), then click on OK.

## Realization

#### APIs
The APIs used are the following:
- [Geo API](https://geo.api.gouv.fr/adresse) : Allows you to retrieve the GPS coordinates of a point from a free text address.
- [CQUEST](https://www.data.gouv.fr/fr/reuses/micro-api-dvf-demande-de-valeurs-foncieres/): Allows you to retrieve the average price per square meter of the last sales made around a given point (via its GPS coordinates).
- Navitia](https://www.navitia.io): Allows you to retrieve the transport time between two GPS points.

#### Files
The different files are as follows:
- **FLASK.ipynb** : Notebook jupyter, to facilitate the installation of the Flask server.  
    Imports the functions from the all_functions.py file, creates the Flask application, displays the html and css pages on the default port, 5000
- **all_functions.py**: implements all the functions used, which call the various APIs. We have for example :
    - get_coordonnees(address) : returns GPS coordinates from a string address, using the Geo api
    - get_price(coordinates) : returns the average price per square meter of a GPS point, using the Cquest api
    - score_price(price): returns a score between 0 and 1 of a price
    - score_duration(duration): returns a score between 0 and 1 of a transport time
    - score_station(duration, price): returns a score between 0 and 1 of a station, as a harmonic average of price and travel time.
    - get_station(coordinates): returns stations with less than a certain transport time, with all their characteristics (name, price, time to the selected address, coordinates)
- templates/**index.html**: application home page. Contains a form where the user enters his address in free text.
- templates/**map.html** : page presenting the interactive map (leaflet) to the user.
    Contains a button to return to the home page.  
    Most of the javascript code has been borrowed from a template provided by navitia.  
- static/CSS/**main.css** : contains the css of the style of the pages.

In addition to these files directly related to the application, there are a few files explaining our approach to the realization of the application.
- **Scoring.ipynb**: notebook presenting the development of the scoring models
- **Station prices.ipynb** : notebook using the Cquest API to retrieve station price data. These data have been recorded statically in the file data/station_price_full.pkl in order to improve the page loading time, this API being quite long to answer for a lot of requests.
