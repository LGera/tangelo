import requests
import pandas as pd
import json
import time
import numpy as np
from IPython.display import HTML
from hashlib import sha512
import codecs
from flask import Flask, render_template
import base64
import hashlib
import sqlite3

app = Flask(__name__)


@app.route('/')
def index():
    datos=requests.get('https://restcountries.com/v2/all')
    datosJson=datos.json()
    dfhmtl = pd.DataFrame(datos)

    list = json.dumps(datosJson)
    start_time=time.time()
    
    text_file = codecs.open("data/data.json", "w", encoding="utf-8")
    text_file.write(list)
    text_file.close()
    #df = pd.read_json('data/data.json')
    f = open('data/data.json')
    lista = json.load(f)
    
    listaDF = [[0 for x in range(4)] for y in range(len(lista))]

    x=0
    for i in lista:
        
        m = hashlib.sha1()
        m.update(i['languages'][0]['nativeName'].encode(encoding = 'UTF-8', errors = 'strict'))
        #print(m.hexdigest())
        listaDF[x][0]=i['name']
        if 'capital' in lista[x]:
            listaDF[x][1]=i['capital']
        else:
            listaDF[x][1]=''
        listaDF[x][2]=m.hexdigest()
        # listaDF[x][3]=str(time.time()*1000 - start_time*1000)+' en ms'
        listaDF[x][3]=time.time()*1000 - start_time*1000
        x=x+1
    
    
    
   
    df = pd.DataFrame(listaDF)
    df = df.rename(columns={0: 'Región',1:'City Name',2:'Language',3:'Tiempo en ms'})
    print(df['Tiempo en ms'].min())
    print(df['Tiempo en ms'].max())
    print(df['Tiempo en ms'].mean())
    min = np.power(df['Tiempo en ms'].min(), 3, dtype=np.float64)
    max = np.power(df['Tiempo en ms'].max(), 3, dtype=np.float64)
    mean = np.power(df['Tiempo en ms'].mean(), 3, dtype=np.float64)
    html = df.to_html("templates/index.html")

    conexion=sqlite3.connect('data/baseDatos.db')

    cursor=conexion.cursor()
    # cursor.execute("CREATE TABLE IF NOT EXISTS tiempos (tiempoMinimo double, tiempoMaximo double, tiempoPromedio double)")
    tiempos=[
        (df['Tiempo en ms'].min()),(df['Tiempo en ms'].max()),(df['Tiempo en ms'].mean())
    ]
    cursor.execute("INSERT INTO tiempos VALUES (?,?,?)",tiempos)
    conexion.commit()
    conexion.close()

    return render_template('index.html',datos=datosJson)




if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 