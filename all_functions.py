import urllib.request, json, requests
import pandas as pd
import numpy as np
from scipy.stats import norm



############################# COORDONNEES - API ADRESSE #########################################
def get_coordonnees(adresse) :
    adresse_processed = adresse.replace(" ","+")
    rhandbefD = urllib.request.urlopen('https://api-adresse.data.gouv.fr/search/?q='+adresse_processed)
    rhandD = ''
    for line in rhandbefD :
             rhandD += line.decode().strip()
    dictio = json.loads(rhandD)

    coordonnees = dictio["features"][0]["geometry"]["coordinates"]
    return(coordonnees)


def invert_coord(coord):
    return([coord[1], coord[0]])


############################### PRIX - API CQUEST ###############################################
def get_price(coordonnees, area=200):
    fhandD = ''
    fhandbefD = urllib.request.urlopen('http://api.cquest.org/dvf?lat='+ str(coordonnees[1])
                                       + '&lon='+ str(coordonnees[0]) + '&dist='+str(area))
    for line in fhandbefD :
        fhandD += line.decode().strip()
    dictio = json.loads(fhandD)

    [valeur_fonciere, surface, price] = [[] for i in range(3)]

    for i in range(len(dictio["features"])):
        if "valeur_fonciere" in dictio["features"][i]["properties"] :
            if "surface_relle_bati"  in dictio["features"][i]["properties"] :
                valeur_fonciere.append(dictio["features"][i]["properties"]["valeur_fonciere"])
                surface.append(dictio["features"][i]["properties"]["surface_relle_bati"])
                #Outliers
                if valeur_fonciere[i]>60*10**3 and valeur_fonciere[i]<10*10**6 :
                    if surface[i]>10 :
                        prix_metre = valeur_fonciere[i]/surface[i]
                        if prix_metre <= 25*10**3:
                            price.append(prix_metre)
                        else:
                            price.append(None)
                    else :
                        price.append(None)
                else :
                    price.append(None)
            else :
                valeur_fonciere.append(None)
                surface.append(None)
                price.append(None)
        else :
            valeur_fonciere.append(None)
            surface.append(None)
            price.append(None)

    price_filtered = list(filter(None, price))
    #print("% d'apparts utiles : ",round(100*len(price_filtered)/len(price)),"%")
    price_mean = np.mean(price_filtered)
    #print("Prix moyen des apparts au m² : ",price_mean)
    return(price_mean)




##################################### STATION - NAVITIA ######################################
def get_station(coordonnees, prices, temps_max=3600):
    navitia_url = str('https://api.navitia.io/v1/coverage/fr-idf/journeys?from='+str(coordonnees[0])+';'+str(coordonnees[1])+'&max_duration='+str(temps_max)+"&forbidden_uris[]=physical_mode:Bus")#"&allowed_id[]=physical_mode:Metro&allowed_id[]=physical_mode:RER")
    navitia_token = '4e8a1312-13a2-4fb8-9e98-aa9cd51b6a11'
    time_json = requests.get(navitia_url, headers={'Authorization': navitia_token})
    time = ''
    for line in time_json :
        time += line.decode().strip()
    dictio = json.loads(time)

    journeys = [[] for i in range(1)]
    name_station, duration, price, coord_station, lon, lat = [[] for i in range(6)]

    for i in range (len(dictio["journeys"])):

        name_station.append(dictio["journeys"][i]["to"]["name"])
        duration.append(round(dictio["journeys"][i]["duration"]/60, 1))
        lon.append(dictio["journeys"][i]["to"]["stop_point"]["coord"]["lon"])
        lat.append(dictio["journeys"][i]["to"]["stop_point"]["coord"]["lat"])
        coord_station.append([lon[i],lat[i]])
        if name_station[-1] in prices.name_station.tolist():
            price.append(prices[prices["name_station"]== name_station[-1]].iloc[0]['price'])
        else :
            price.append(np.nan)

    coord_station = [invert_coord(coord) for coord in coord_station]

    scores = score_all(duration, price, temps_moyen=20)

    df = pd.DataFrame(list(zip(name_station,duration,coord_station,price,scores)),
                      columns=["name_station","duration","coord_station","price","score"])

    data_set = {
        "journeys" : {},
    }

    for i in range(len(df)):
        data_set["journeys"][i] = {
            "name_station" : df["name_station"][i],
            "duration" : df["duration"][i],
            "coord_station" : df["coord_station"][i],
            "price" : df["price"][i],
            "score" : df["score"][i]
        }

    return(data_set)

def meilleur_score (data_set, adresse) :
    data_set2 = []
    j = 0
    for i in range(len(data_set["journeys"])):
        if data_set["journeys"][i]["score"] > 0.8 :
            j+=1
            data_set2.append(str(j)+") "+ str(data_set["journeys"][i]["name_station"])+" pour un temps de trajet de " + str(data_set["journeys"][i]["duration"]) + "min" +  " le prix au mètre carré : " + str(round(data_set["journeys"][i]["price"],0)) + "€" + " ce qui nous donne un score de  " +  str(round(data_set["journeys"][i]["score"],3)))
    return(data_set2)

####################################### SCORES ##########################################
price_moyen = 10*10**3
temps_moyen = 30
scoring = 'harmonic'  #ou bien 'rmse'

def score_duration(duration, temps_moyen=30):
    mu = temps_moyen*0.6
    sigma = temps_moyen*0.30
    if duration <= mu:
        score = 1
        return(score)
    else:
        score = norm.pdf(duration, mu, sigma)*np.sqrt(2*np.pi)*sigma
        return(score)


def score_price(price, price_moyen=10*10**3):
    #On remet le prix/m² en loyer/m²:
    mu = price_moyen*0.2
    sigma = price_moyen*0.6
    if price <= mu:
        score = 1
        return(score)
    else:
        score = norm.pdf(price, mu, sigma)*np.sqrt(2*np.pi)*sigma
        return(score)


def score_station(duration, price, temps_moyen=30, price_moyen=11*10**3, scoring=scoring):
    score_prix = score_price(price, price_moyen)
    score_duree = score_duration(duration, temps_moyen)
    if scoring == 'rmse':
        return(round(np.sqrt(score_prix**2 + score_duree**2)/1.4142,3))
    else :
        return(round(   np.sqrt((score_prix*score_duree*2)/(score_prix+score_duree))   , 3))

def score_all(liste_duration, liste_prix, temps_moyen=temps_moyen, price_moyen=price_moyen):
    scores = []
    for prix, duree in zip(liste_prix, liste_duration):
        scores.append(score_station(duree, prix, temps_moyen, price_moyen))
    return(scores)
