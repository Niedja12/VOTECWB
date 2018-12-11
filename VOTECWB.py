#!/usr/bin/python
# -*- coding: utf-8 -*-
from geopy.geocoders import Nominatim
import unicodedata

import cgi
import psycopg2

try:
    conn = psycopg2.connect("dbname = 'Projeto' port = '5432'  user= 'user' password = 'geolivre' host='localhost'")

except:
    print 'incorret'

# cabecalho que informa o browser para renderizar como HTML
print 'Content-Type: text/html; charset=UTF-8\n\n'
print '<html>'
print "<head>"
print "<title>"
print "teste niedja"
print "</title>"

#chamando leaflet on line
print """
    <meta charset="utf-8" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.3.4/dist/leaflet.css"
   integrity="sha512-puBpdR0798OZvTTbP4A8Ix/l+A4dHDD0DGqYW6RQ+9jxkRFclaxxQb/SJAWZfWAkuyeQUytO7+7N4QKrDh+drA=="
   crossorigin=""/>
   <link rel="stylesheet" href="../node_modules/leaflet-routing-machine/dist/leaflet-routing-machine.css" />"""
print """<script src="https://unpkg.com/leaflet@1.3.4/dist/leaflet.js"
   integrity="sha512-nMMmRyTVoLYqjP9hrbed9S+FzjZHW5gY1TWCHA5ckwXZBadntCNs8kEqAWdrb9O7rxbCaA4lKTIWjDXZxflOcA=="
   crossorigin=""></script>
   <script src="../node_modules/leaflet-routing-machine/dist/leaflet-routing-machine.js"></script>
   """

print "</head>"
print "<body>"
#comando html para selecionar arquivo
print """
 <form>
  Digite a Zona:<br>
  <input type="text" name="zona"><br>
  Digite a Seção:<br>
  <input type="text" name="secao"><br>
  Digite seu endereço, por exemplo: rua, número:<br>
  <input type="text" name="endereco">
  <br>
  <input type="submit" value="Enviar">
</form>"""

#lendo os dados do formulario
form = cgi.FieldStorage()
zona =  form.getvalue('zona')
secao =  form.getvalue('secao')
endereco1 =  form.getvalue('endereco')

#criando a view de acordo com a secao e zona escolhida
cur = conn.cursor()
cur.execute ("""Create or replace view zn_secoes as
         select *
         FROM tre_local_vot_zn_secoes_4674
         WHERE dg_n_zona = '%i' and dg_SECOES ilike '%s';""" % (int(zona), ('%'+str(secao)+'%')))
conn.commit()
cur.close()
conn.close()


geolocator  =  Nominatim (user_agent = "niedja@gmail.com")

try:
    location = geolocator.geocode(endereco1 + ", Curitiba")
except:
    print 'Este endereco nao existe'
#popup_endereco = location.address
lat_endereco = location.latitude
lon_endereco = location.longitude
popup_endereco = unicodedata.normalize('NFKD', location.address).encode('ascii', 'ignore')


#consulta endereco do local de votacao
try:
    conn = psycopg2.connect("dbname = 'Projeto' port = '5432'  user= 'user' password = 'geolivre' host='localhost'")

except:
    print 'incorret'
cur = conn.cursor()
cur.execute ("""
         select endereco
         FROM zn_secoes
         """)
end_zn_secoes = str(cur.fetchone()[0]) + ", Curitiba"
cur.execute ("""
         select latitude
         FROM zn_secoes
         """)
lat_zn_secoes = float(cur.fetchone()[0])
cur.execute ("""
         select longitude
         FROM zn_secoes
         """)
lon_zn_secoes = float(cur.fetchone()[0])

conn.commit()
cur.close()
conn.close()

lat_media = (lat_endereco+lat_zn_secoes)/2
lon_media = (lon_endereco+lon_zn_secoes)/2


#inserindo o mapa
print "<div id='map' style='width: 1200px; height: 600px'></div>"
print """
<script>
	var mymap = L.map('map').setView([""" +str(lat_media)+ """,""" +str(lon_media)+ """], 10);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoibWFyY2lhbm9kYWNvc3RhbGltYSIsImEiOiJjamV5eGsxZ3IwNGFrMndxb216dWwwenB1In0.maLUDU8v7Xi5PAOkjzPwMg'
    }).addTo(mymap);

    L.Routing.control({
    waypoints: [
        L.latLng(""" +str(lat_endereco)+ """,""" +str(lon_endereco)+ """),
        L.latLng(""" +str(lat_zn_secoes)+ """,""" +str(lon_zn_secoes)+ """)
    ],
    language: 'pt-BR',
    routeWhileDragging: false
    }).addTo(mymap);

    //inserindo a layers de secoes

  var zn_secoes = L.tileLayer.wms('http://localhost:8082/geoserver/Projeto/wms', {
    layers: 'Projeto:zn_secoes', transparent: 'true', format: 'image/png'
  }).addTo(mymap);

//inserindo a layer de divisa de bairros

 var bairros = L.tileLayer.wms('http://localhost:8082/geoserver/Projeto/wms', {
   layers: 'Projeto:divisa_de_bairros_4674', transparent: 'true', format: 'image/png'
 }).addTo(mymap);

  var secoes = L.tileLayer.wms('http://localhost:8082/geoserver/Projeto/wms', {
    layers: 'Projeto:tre_local_votacao_4674', transparent: 'true', format: 'image/png'
  }).addTo(mymap);

    L.marker([""" +str(lat_endereco)+ """,""" +str(lon_endereco)+ """]).addTo(mymap)
    .bindPopup('""" +str(popup_endereco)+ """')
    .openPopup();
L.marker([""" +str(lat_zn_secoes)+ """,""" +str(lon_zn_secoes)+ """]).addTo(mymap)
.bindPopup('Zona: """ +str(zona)+ """, Secao: """ +str(secao)+ """ ')
.openPopup();

var baseMaps = {
    "OpenStreetMap": mymap
};

var overlayMaps = {
    "Bairros": bairros,
    "Todos as seções": secoes

};

L.control.layers(baseMaps, overlayMaps,{collapsed:false}).addTo(mymap);


</script>"""

print "</body>"
print "</html>"
