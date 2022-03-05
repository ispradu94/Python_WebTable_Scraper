#
# Author: Ispas Radu
# Datetime: 05.03.2022
#
# Description: Simple Pyhton WebTable Scraper
#
# +----------------------------------+---------+
# |               Col1               |  Col2   |
# +----------------+-----------------+---------+
# |    Subcol1     |     Subcol2     |   Data  |
# +----------------+-----------------+---------+
#

from unittest import skip
import pandas as pd
import requests
from bs4 import BeautifulSoup
import math
import time
start_time = time.time()


#   Round Decimals Down
# -------------------------------------------------------------- #
# > SOURCE: https://kodify.net/python/math/round-decimals/
# -------------------------------------------------------------- #
def round_decimals_down(number:float, decimals:int=2):

    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    elif decimals == 0:
        return math.floor(number)

    factor = 10 ** decimals
    return math.floor(number * factor) / factor
# -------------------------------------------------------------- #


# Custom Url For Scrape
#url = 'http://static.bacalaureat.edu.ro/2021/rapoarte_sept/IF/lista_unitati/1263/rezultate_finale/dupa_medie/page_1.html'
url = 'http://static.bacalaureat.edu.ro/2021/rapoarte/IF/lista_unitati/1263/rezultate_finale/dupa_medie/page_1.html'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Dumb Check for page numbers
pages = soup.select('td')
el_pages = pages[8].select("option")
max_pages = int(str(el_pages[len(el_pages)-1]).split('"')[3])


# Run over all pages
results_df = pd.DataFrame()
for page in range(1,max_pages+1):

    url = 'http://static.bacalaureat.edu.ro/2021/rapoarte/IF/lista_unitati/1263/rezultate_finale/dupa_medie/page_{0}.html'.format(page)
    print("Current Page : {0}   | URL : {1}".format(page,url))
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get Table by HTML ID
    table = soup.find('table', id="mainTable")

    #print("================================== START HERE ==================================")
    rows = table.find_all('tr')

    # Init Every Col.
    nr_crt                          = ""
    cod_candidat                    = ""
    Promotie_Anterioara             = ""
    Forma_Invatamant                = ""
    Specializare                    = ""
    LB_ROM_Competente               = ""
    LB_ROM_Scris                    = ""
    LB_ROM_Contestatie              = ""
    LB_ROM_Nota_Finala = 0.0
    LB_MODERNA_STUDIATA             = ""
    LB_MODE_NOTA                    = ""
    DISCIP_OBLIGATORIE              = ""
    DISCIP_LA_ALEGERE               = ""
    COMPETENTE_DIGITALE_NOTA        = ""
    DISCIP_OBLIGATORIE_NOTA         = ""
    DISCIP_OBLIGATORIE_CONTESTATIE  = ""
    DISCIP_OBLIGATORIE_NOT_FINALA = 0.0
    DISCIP_LA_ALEGERE_NOTA          = ""
    DISCIP_LA_ALEGERE_CONTESTATIE   = ""
    DISCIP_LA_ALEGERE_NOT_FINALA = 0.0

    # Parsing DataFrame
    row_passed = 0 # First 2 rows of the pages are empty.
    for row in rows:

        data = row.find_all('td')
        row_counter = len(data)

        # Build by row type - Doubled Rows
        match row_counter:
            case 17:
                nr_crt = data[0].text

                tmp = str(data[1]).split('["')
                cod_candidat = tmp[1].split(' <br>')[0]

                Promotie_Anterioara             = data[2].text
                Forma_Invatamant                = data[3].text
                Specializare                    = data[4].text
                LB_ROM_Competente               = data[5].text
                LB_ROM_Scris                    = data[6].text
                LB_ROM_Contestatie              = data[7].text
                try:
                    LB_ROM_Nota_Finala = float(data[8].text)
                except:
                    LB_ROM_Nota_Finala = 0.0
                LB_MODERNA_STUDIATA             = data[10].text
                LB_MODE_NOTA                    = data[11].text
                DISCIP_OBLIGATORIE              = data[12].text
                DISCIP_LA_ALEGERE               = data[13].text
                COMPETENTE_DIGITALE_NOTA        = data[14].text
                row_passed = row_passed + 1
            case 10:
                DISCIP_OBLIGATORIE_NOTA         = data[4].text
                DISCIP_OBLIGATORIE_CONTESTATIE  = data[5].text
                try:
                    DISCIP_OBLIGATORIE_NOT_FINALA   = float(data[6].text)
                    DISCIP_LA_ALEGERE_NOT_FINALA    = float(data[9].text)
                except:
                    DISCIP_OBLIGATORIE_NOT_FINALA = 0.0
                    DISCIP_LA_ALEGERE_NOT_FINALA = 0.0

                DISCIP_LA_ALEGERE_NOTA          = data[7].text
                DISCIP_LA_ALEGERE_CONTESTATIE   = data[8].text

                row_passed = row_passed + 1
            case 0:
                skip

        if( row_passed > 1 and row_passed % 2 == 0):
            media = ( float(LB_ROM_Nota_Finala) + float(DISCIP_OBLIGATORIE_NOT_FINALA) + float(DISCIP_LA_ALEGERE_NOT_FINALA) ) / 3
            media = round_decimals_down(media)
            formatted_media = "{:.2f}".format(media)
            rezultat = ""
            if(media >= 6.0 and float(LB_ROM_Nota_Finala) >= 5.0 and float(DISCIP_OBLIGATORIE_NOT_FINALA) >= 5.0 and float(DISCIP_LA_ALEGERE_NOT_FINALA) >= 5.0 ):
                rezultat = "REUSIT"
            else:
                if( media >= 6.0 and float(LB_ROM_Nota_Finala) <= 0.0 or float(DISCIP_OBLIGATORIE_NOT_FINALA) <= 0.0 or float(DISCIP_LA_ALEGERE_NOT_FINALA) <= 0.0 ):
                    rezultat = "NEPREZENTAT"
                else:
                    #print("RESPINS: {0}|{1}|{2}".format(media,LB_ROM_Nota_Finala,DISCIP_OBLIGATORIE_NOT_FINALA,DISCIP_LA_ALEGERE_NOT_FINALA))
                    rezultat = "RESPINS"
                # # Lipsa Dat Afara din Examen # #

            temp_df = pd.DataFrame([[nr_crt,cod_candidat,Promotie_Anterioara,Forma_Invatamant,Specializare,
                                LB_ROM_Competente,LB_ROM_Scris,LB_ROM_Contestatie,LB_ROM_Nota_Finala,
                                LB_MODERNA_STUDIATA,LB_MODE_NOTA,
                                DISCIP_OBLIGATORIE,DISCIP_OBLIGATORIE_NOTA,DISCIP_OBLIGATORIE_CONTESTATIE,DISCIP_OBLIGATORIE_NOT_FINALA,
                                DISCIP_LA_ALEGERE,DISCIP_LA_ALEGERE_NOTA,DISCIP_LA_ALEGERE_CONTESTATIE,DISCIP_LA_ALEGERE_NOT_FINALA,
                                COMPETENTE_DIGITALE_NOTA,str(formatted_media),rezultat]], 
                        columns = ['Nr. crt.','Codul candidatului','Promotie anterioară','Forma învăţământ','Specializare',
                                'Lb.Rom Competente','Lb.Rom Scris','Lb.Rom Contestatie','Lb.Rom Nota_Finala',
                                'Lb.Moderna Studiata','Lb.Moderna Nota',
                                'Discip.Obligatorie','Discip.Obligatorie Nota','Discip.Obligatorie Contestatie','Discip.Obligatorie Nota Finala',
                                'Discip.La Alegere ','Discip.La Alegere Nota','Discip.La Alegere Contestatie','Discip.La Alegere Nota Finala',
                                'Competente Digitale Nota','Media','Rezultat'])
            #results_df = results_df.append(temp_df).reset_index(drop=True) #Append is deprecated
            results_df = pd.concat([results_df,temp_df])
        else:
            skip

print(results_df)
results_df.to_csv('BAC_Data.csv',encoding='utf-8-sig') # encoding for no strange characters

print("--- %s seconds ---" % (time.time() - start_time))