import spacy

try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    NLP = spacy.blank("en")
    NLP.add_pipe("sentencizer")