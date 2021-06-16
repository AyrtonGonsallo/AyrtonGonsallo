import nltk
from nltk.tag import StanfordPOSTagger
from rake_nltk import Rake

from du_texte_aux_questions import Document

jar = './stanford/stanford-postagger-4.2.0.jar'
model = './stanford/models/french-ud.tagger'
import os
java_path = "C:/jdk1.8.0_281/bin/java.exe"
os.environ['JAVAHOME'] = java_path
c = "Dans cette analyse garantie 100% spoilers, nous allons, comme à notre habitude, décrypter la série de Lauren Schmidt Hissrich. Nous reviendrons sur les divers rebondissements de l'intrigue et les mystères de ce monde fantastique riche en magie et créatures fantastiques."
'''pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8' )


liste = nltk.sent_tokenize(c)
res = pos_tagger.tag(liste)
print(res)'''

qu = Document(c).format_questions()
for q in qu:
    print(q[1]+"-"+q[0])