import nltk
from nltk.tag.stanford import StanfordNERTagger

st = StanfordNERTagger('stanford-ner/all.3class.distsim.crf.ser.gz', 'stanford-ner/stanford-ner.jar')
text = "/produkt/epson-workforce-pro-wf-4830dtwf-multifunktion-printer/23BF6R/"

for sent in nltk.sent_tokenize(text):
    tokens = nltk.tokenize.word_tokenize(sent)
    tags = st.tag(tokens)
    for tag in tags:
        # if tag[1]=='PERSON': 
        print(tag)
