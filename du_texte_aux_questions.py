import string
import nltk  # 3.4.1
import os
from rake_nltk import Rake  # 1.0.4
from nltk.tokenize.treebank import TreebankWordDetokenizer as TWD
from nltk.corpus import stopwords

from nltk.tag import StanfordPOSTagger

java_path = "C:/jdk1.8.0_281/bin/java.exe"
os.environ['JAVAHOME'] = java_path

jar = 'C:/Users/user/PycharmProjects/Projet AI/stanford/stanford-postagger-4.2.0.jar'
model = 'C:/Users/user/PycharmProjects/Projet AI/stanford/models/french-ud.tagger'

pos_tagger = StanfordPOSTagger(model, jar, encoding='utf8')

nltk.download("averaged_perceptron_tagger")
nltk.download("punkt")
nltk.download("stopwords")


class Document:
    def __init__(self, raw_string):
        """
        raw_string - string of a document
        Constructor for document, creates a document containing sentences
        """

        self._raw_string = raw_string
        raw_sentences = nltk.sent_tokenize(self._raw_string)
        self._sentences = [Sentence(sentence) for sentence in raw_sentences]

    def format_questions(self):
        """
        Turns questions into form suitable for server
        Returns List of tuples in form (question, answer)
        """

        questions = self._get_questions()

        return questions

    def _get_questions(self):
        """
        Returns a dictionary of questions containing on question
            from each sentence
        Returns dict of form {word: question}
        """

        questions = []
        for sentence in self._sentences:
            for key, value in sentence.get_questions().items():
                temp = (key, value)
                questions.append(temp)

        return questions

    def __str__(self):
        """
        Returns original document raw string
        """

        return self._raw_string

    @property
    def sentences(self):
        return self._sentences


class Sentence:
    def __init__(self, raw_string):
        """
        raw_string - string of a single sentence
        Constructor for sentence, creates one sentence with questions
        """

        self._raw_string = raw_string
        self._words = nltk.word_tokenize(self._raw_string)

        # preprocess possible keywords and possible questions
        # for quicker runtime access
        self._preprocess_keywords()
        self._preprocess_questions()

    def get_questions(self):
        """
        Gets all questions for sentence
        Returns dict of form {word: question}
        """

        return self._questions

    def _preprocess_questions(self):
        """
        Preprocesses clean words to create blanked questions
            using all clean words
        """

        self._questions = dict()

        # reperer les mots importants
        clean_words = [word.lower() for word in self._words if self._is_clean(word)]
        dt = TWD()

        for word in clean_words:
            # verification en miniscule
            lower_words = [word.lower() for word in self._words]

            words_copy = self._words.copy()
            # mettre un espace
            for index in [index for index, value in enumerate(lower_words) if value == word]:
                words_copy[index] = "_____"
            self._questions[word] = dt.detokenize(words_copy)

    def _is_clean(self, word):
        """
        word - full case word
        Applies rules to determine if word is good
        Returns true if word is usable, false otherwise
        """

        word_pos = pos_tagger.tag([word])[0][1]

        # si  c'est un mot clé
        if not word.lower() in self._keywords:
            return False

        # normal ascii, no punctuation
        for char in word:
            if not char in string.printable:
                return False
            if char in string.punctuation:
                return False

        CURRENT = ["PROPN", "ADJ", "NUM", "ADV", "NOUN", "X"]
        # adj and noun only
        if not word_pos in CURRENT:
            return False

        # removes words like "use" (NN), but allows abbreviations
        if ((word_pos == "NOUN" or word_pos == "ADJ") and len(word) <= 4) or (word_pos == "PROPN" and len(word) <= 5):
            if word.islower() or word[:1].isupper() and word[1:].islower():
                return False

        # removes small unimportant words
        if word in stopwords.words("french"):
            return False

        return True

    def _preprocess_keywords(self):
        """
        Preprocesses RAKE keywords to be used in
            question preprocessing
        Keywords will be all lowercase
        """

        r = Rake(language='french', max_length=1)
        r.extract_keywords_from_text(self._raw_string)
        self._keywords = r.get_ranked_phrases()

    def __str__(self):
        """
        Returns original sentence raw string
        """

        return self._raw_string
