import random
from datetime import date

autores = open('autores.txt')
citas = open('citas.txt')
autoresNom = []
citasNom = []
i = -1
j = -1
for line in autores:
    autoresNom.append(line)
    i += 1
for line in citas:
    citasNom.append(line)
    j += 1
ind = random.randint(0, i)
jnd = random.randint(0, j)
cita = '"'+citasNom[jnd]+'" - '+autoresNom[ind]
cita = cita.decode('utf-8')
cita = cita.replace('\n', '')
hoy = date.today()
hoy = hoy.day
dia = TextNumber(hoy)
if dia in text:
    reply('Encontrado')
autores.close()
citas.close()
