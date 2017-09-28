# coding: cp1252
import StringIO
import json
import logging
import random
import urllib
import urllib2
import datetime
import re #regexp
from num2es import TextNumber

# for sending images
from PIL import Image
import multipart

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.ext import db
import webapp2

TOKEN = '327996759:AAGg9UqWmdb5TKl6RAUxAJg7LylakZmgGBA'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)
    cishet = ndb.BooleanProperty(indexed=True, default=False)
    nick = ndb.StringProperty(indexed=True, default=False)
    points = ndb.IntegerProperty(indexed=True, default=False)

class Group(db.Model):
    # key name: str(chat_id)
    enabled = db.BooleanProperty(indexed=False)
    name = db.StringProperty(indexed=True)
    users = db.StringListProperty(indexed=True)
    recl_this_hour = db.ListProperty(bool)
    points = db.ListProperty(int)
    last_recl = db.IntegerProperty(indexed=False)


# ================================

def setEnabled(chat_id, yes, nick):
    es = EnableStatus.get_by_id(str(chat_id))
    if es is None:
        es = EnableStatus(points=0, cishet=True,id=str(chat_id))
    es.nick = nick
    es.enabled = yes
    es.put()

def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False

def groupStart(chat_id, name):
    es = Group.get_or_insert(str(chat_id))
    if not es or es.last_recl is None:
        es.last_recl = 0
    es.name = name
    es.enabled = True
    es.put()

def groupAdd(chat_id, user_id):
    grupo = Group.get_or_insert(str(chat_id))
    if not str(user_id) in grupo.users:
        grupo.users.append(str(user_id))
        grupo.points.append(0)
        grupo.recl_this_hour.append(False)
        grupo.put()
    else:
        return True

def addPoint(chat_id, user_id, nick):
    grupo = Group.get_or_insert(str(chat_id))
    if not str(user_id) in grupo.users:
        grupo.users.append(str(user_id))
        grupo.points.append(0)
        grupo.recl_this_hour.append(False)
    n = grupo.last_recl
    a = 0
    grupo.last_recl += 1
    i = grupo.users.index(str(user_id))
    if n < 3:
        grupo.points[i] += 2**(2-n)
        try:
            es = EnableStatus.get_or_insert(str(user_id))
        except:
            logging.info('problema con el juego')
            return 3
        if es and not grupo.recl_this_hour[i]:
            es.nick = nick
            es.points += 2**(2-n)
            grupo.recl_this_hour[i] = True
            es.put()
            a = 3
        elif es:
            a = 3
        else:
            grupo.last_recl -= 1
    grupo.put()
    return a

def getGlobalRank():
    es = EnableStatus.query(EnableStatus.points>0).order(-EnableStatus.points)
    rank = u''
    i = 1
    for user in es:
        rank = rank + str(i) + u'. ' + user.nick + ' - ' + str(user.points) + ' puntos\n'
        i += 1
        if i > 10:
            break
    return rank

def getGroupRank(group_id):
    grupo = Group.get_by_key_name(str(group_id))
    rank = u'Grupo ' + grupo.name +'\n'
    i = 1
    together = zip(grupo.points, grupo.users)
    sorted_together =  sorted(together, reverse=True)
    points = [x[0] for x in sorted_together]
    users = [x[1] for x in sorted_together]
    for user in users:
        nick = getName(user) # Optimizable, bastante, pero :S
        if not nick:
            nick = user
        rank = rank + str(i) + u'. ' + nick + ' - ' + str(points[i-1]) + ' puntos\n'
        i += 1
        if i > 10 or points[i-2] == 0:
            break
    return rank

def getName(user_id):
    es = EnableStatus.get_by_id(str(user_id))
    if es:
        return es.nick
    return False

def mwimwimwimwimwi(frase):
    frase = re.sub('c[ao]', 'qui', frase)
    frase = re.sub('C[ao]', 'Qui', frase)
    frase = re.sub('c[AO]', 'qUI', frase)
    frase = re.sub('C[AO]', 'QUI', frase)
    frase = re.sub(u'c[áóú]', u'quí', frase)
    frase = re.sub(u'C[áóú]', u'QUí', frase)
    frase = re.sub(u'c[ÁÓÚ]', u'quÍ', frase)
    frase = re.sub(u'C[ÁÓÚ]', u'QUÍ', frase)
    frase = re.sub(u'c[àòù]', u'quí', frase)
    frase = re.sub(u'C[àòù]', u'QUí', frase)
    frase = re.sub(u'c[ÀÒÙ]', u'quÍ', frase)
    frase = re.sub(u'C[ÀÒÙ]', u'QUÍ', frase)
    frase = re.sub('z[aou]', 'ci', frase)
    frase = re.sub('Z[aou]', 'Ci', frase)
    frase = re.sub('z[AOU]', 'cI', frase)
    frase = re.sub('Z[AOU]', 'CI', frase)
    frase = re.sub(u'z[áóú]', u'cí', frase)
    frase = re.sub(u'Z[áóú]', u'Cí', frase)
    frase = re.sub(u'z[ÁÓÚ]', u'cÍ', frase)
    frase = re.sub(u'Z[ÁÓÚ]', u'CÍ', frase)
    frase = re.sub(u'z[àòù]', u'cí', frase)
    frase = re.sub(u'Z[àòù]', u'Cí', frase)
    frase = re.sub(u'z[ÀÒÙ]', u'cÍ', frase)
    frase = re.sub(u'Z[ÀÒÙ]', u'CÍ', frase)
    frase = re.sub(u'(?<=[gG])u[aoiu]', u'üi', frase)
    frase = re.sub(u'(?<=[gG])U[aoiu]', u'Üi', frase)
    frase = re.sub(u'(?<=[gG])u[AOIU]', u'üI', frase)
    frase = re.sub(u'(?<=[gG])U[AOIU]', u'ÜI', frase)
    frase = re.sub(u'(?<=[gG])u[áóíú]', u'üí', frase)
    frase = re.sub(u'(?<=[gG])U[áóíú]', u'Üí', frase)
    frase = re.sub(u'(?<=[gG])u[ÁÓÍÚ]', u'üÍ', frase)
    frase = re.sub(u'(?<=[gG])U[ÁÓÍÚ]', u'ÜÍ', frase)
    frase = re.sub('(?<=[gG])[ao]', 'ui', frase)
    frase = re.sub('(?<=[gG])[AO]', 'UI', frase)
    frase = re.sub(u'(?<=[gG])u(?![iIíÍeEeÉèÈ])', 'ui', frase)
    frase = re.sub(u'(?<=[gG])U(?![iIíÍeEeÉèÈ])', 'UI', frase)
    frase = re.sub(u'(?<=[gG])[áóú]', 'uí', frase)
    frase = re.sub(u'(?<=[gG])[ÁÓÚ]', 'UÍ', frase)
    frase = re.sub(u'(?<=[gG])[àòù]', 'uí', frase)
    frase = re.sub(u'(?<=[gG])[ÀÒÙ]', 'UÍ', frase)
    frase = re.sub('(?<=[gG])e', 'i', frase)
    frase = re.sub('(?<=[gG])E', 'I', frase)
    frase = re.sub(u'(?<=[gG])é', 'í', frase)
    frase = re.sub(u'(?<=[gG])É', 'Í', frase)
    frase = re.sub(u'(?<=[gG])è', 'í', frase)
    frase = re.sub(u'(?<=[gG])È', 'Í', frase)
    frase = re.sub('(?<![qQgG])[aeo]', 'i', frase)
    frase = re.sub('(?<![qQgG])[AEO]', 'I', frase)
    frase = re.sub(u'[áéó]', u'í', frase)
    frase = re.sub(u'[ÁÉÓ]', u'Í', frase)
    frase = re.sub(u'[àèò]', u'í', frase)
    frase = re.sub(u'[ÀÈÒ]', u'Í', frase)
    return frase

def mimimimimi(frase):
    frase = re.sub('cu', 'qui', frase)
    frase = re.sub('Cu', 'Qui', frase)
    frase = re.sub('cU', 'qUI', frase)
    frase = re.sub('CU', 'QUI', frase)
    frase = re.sub(u'cú', u'quí', frase)
    frase = re.sub(u'Cú', u'QUí', frase)
    frase = frase.replace(u'ü', 'ui')
    frase = frase.replace(u'Ü', 'UI')
    frase = re.sub(u'(?<![qQgG])[u]', 'i', frase)
    frase = re.sub(u'(?<![qQgG])[U]', 'I', frase)
    frase = re.sub(u'[ú]', u'í', frase)
    frase = re.sub(u'[Ú]', u'Í', frase)
    return frase

def mwimwi(frase):
    frase = re.sub(u'cu(?![iIíÍ])', 'qui', frase)
    frase = re.sub(u'Cu(?![iIíÍ])', 'Qui', frase)
    frase = re.sub(u'cU(?![iIíÍ])', 'qUI', frase)
    frase = re.sub(u'CU(?![iIíÍ])', 'QUI', frase)
    frase = re.sub(u'cú(?![iIíÍ])', u'quí', frase)
    frase = re.sub(u'Cú(?![iIíÍ])', u'Quí', frase)
    frase = re.sub(u'cÚ(?![iIíÍ])', u'qUÍ', frase)
    frase = re.sub(u'CÚ(?![iIíÍ])', u'QUÍ', frase)
    frase = re.sub(u'(?<![qQgGcC])[u](?![iIíÍ])', 'i', frase)
    frase = re.sub(u'(?<![qQgGcC])[U](?![iIíÍ])', 'I', frase)
    frase = re.sub(u'(?<![cC])[ú](?![iIíÍ])', u'í', frase)
    frase = re.sub(u'(?<![cC])[Ú](?![iIíÍ])', u'Í', frase)
    return frase

# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):
    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        try:
            message = body['message']
        except:
            message = body['edited_message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        nick = fr.get('first_name')
        chat = message['chat']
        chat_id = chat['id']

#        if not text:
#            logging.info('no text')
#            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        def messagesend(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                ], [
                    ('photo', 'image.jpg', img),
                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        if not message is None and message.get('new_chat_member'):
            newmember = message.get('new_chat_member')
            name = chat['title']
            if newmember['id'] == 327996759:
                groupStart(chat_id, name)
                messagesend(u'¡Hola!, soy el bot Heterófobo para Telegram.')
            elif newmember['id'] == 53420924:
                messagesend(u'Hola mami :*')
            elif newmember['id'] == 235437:
                messagesend(u'Un saludo a la persona más bonita de este mundo: @' + newmember['username'] + u' \U0001F496\U0001F496')
            else:
                user_id = newmember['id']
                groupAdd(chat_id, user_id)
                respuesta = 'Hola, ' + newmember['first_name'] + ', te damos la bienvenida a ' + name
                messagesend(respuesta)

        if not text:
            text = ' '

        if text.startswith('/'):
            if text == '/start' and chat['type'] == 'private':
                setEnabled(chat_id, True, nick)
                respuesta = 'Bot activado, '+nick
                reply(respuesta)
            elif text == '/stop' and chat['type'] == 'private':
                reply('Bot desactivado')
                setEnabled(chat_id, False, nick)
            elif text == '/stop' or text == '/start' or text == '/start@heterofobot' or text == '/stop@heterofobot':
                reply(u'Envíame este comando por privado, por favor')
            elif text == '/ayuda' or text == '/help' or text == '/help@heterofobot' or text == '/ayuda@heterofobot':
                reply(u'Ayuda del bot Heterófobo\n Todavía en desarrollo')
            elif text == '/image':
                img = Image.new('RGB', (512, 512))
                base = random.randint(0, 16777216)
                pixels = [base+i*j for i in range(512) for j in range(512)]  # generate sample image
                img.putdata(pixels)
                output = StringIO.StringIO()
                img.save(output, 'JPEG')
                reply(img=output.getvalue())
            elif text == '/cita' or text == '/cita@heterofobot':
                autores = open('autores.txt', 'r')
                citas = open('citas.txt', 'r')
                Autoresnom = []
                Citasnom = []
                i = -1
                j = -1
                for line in autores:
                    Autoresnom.append(line)
                    i += 1
                for line in citas:
                    Citasnom.append(line)
                    j += 1
                ind = random.randint(0, i)
                jnd = random.randint(0, j)
                cita = '"'+Citasnom[jnd]+'" - '+Autoresnom[ind]
                cita = cita.decode('utf-8')
                cita = cita.replace('\n', '')
                autores.close()
                citas.close()
                messagesend(cita)
            elif chat['type'] == 'private':
                reply('No he entendido el comando')

        # CUSTOMIZE FROM HERE
        elif text.startswith('!'):
            if text.startswith('!uneme') and not chat['type'] == 'private':
                user_id = fr['id']
                if not groupAdd(chat_id, user_id):
                    reply(u'A partir de ahora aparecerás en la lista del grupo')
                else:
                    reply('Ya estabas en la lista del grupo')
            elif text.startswith('!ranking') and chat['type'] == 'private':
                rank = getGlobalRank()
                messagesend(rank)
            elif text.startswith('!ranking'):
                if text.startswith('!ranking grupo'):
                    rank = getGroupRank(chat_id)
                    messagesend(rank)
                else:
                    rank = getGlobalRank()
                    messagesend(rank)
            elif text.startswith('!mimi') or text.startswith('!mwimwi'):
                if message.get(u'reply_to_message'):
                    mess = message.get(u'reply_to_message')
                    burla = [[]] * 2
                    burla[1] = mess.get(u'text')
                    message_id = mess.get('message_id')
                else:
                    burla = text.split(None, 1)
                if len(burla)>1 and not burla[1] is None:
                    burla = burla[1]
                    burla = mwimwimwimwimwi(burla)
                    if text[2] == 'i':
                        burla = mimimimimi(burla)
                    else:
                        burla = mwimwi(burla)
                    reply(burla)
                else:
                    reply('Buen intento ;)')
            elif text.startswith('!clear'):
                if len(text)>=7 and text[6] == 'l':
                    mensaje = '.'+'\n'*150+'.'
                    messagesend(mensaje)
                elif len(text)>=7 and text[6] == 's':
                    mensaje = '.'+'\n'*30+'.'
                    messagesend(mensaje)
            elif chat['type'] == 'private':
                reply(u'Este comando únicamente sirve en grupos')
        elif 'who are you' in text:
            reply('telebot starter kit, created by yukuku: https://github.com/yukuku/telebot')
        elif 'what time' in text:
            reply('look at the corner of your screen!')
        else:
            if getEnabled(chat_id):
                reply(u'¡Recibí tu mensaje! (pero no sé responder a él)')
            else:
                logging.info('not enabled for chat_id {}'.format(chat_id))
        hoy = datetime.datetime.now()
        hoy = hoy.day
        dia = TextNumber(hoy)
        dia = dia.text
        if not chat['type'] == 'private' and dia in text.lower():
            user_id = fr['id']
            a = addPoint(chat_id, user_id, nick)
            if a == 1:
                reply(u'No estás en la base de datos, únete con "/start" por privado')
            elif a == 2:
                reply('Encontrado')

class ZeroHandler(webapp2.RequestHandler):
    def get(self):
        hoy = datetime.datetime.now()
        minuto = hoy.minute
        dia = hoy.day
        if minuto == dia:
            grupos = Group.all(keys_only=True)
            grupos = Group.get_by_id(grupos)
            k = len(grupos)
            for y in range(0, k):
                grupos[y].last_recl = 0
                n = len(grupos[y].recl_this_hour)
                for x in range(0, n):
                    grupos[y].recl_this_hour[x] = False
            grupos.put()

app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
    ('/setzero', ZeroHandler),
], debug=True)
