import wolframalpha
from nltk import word_tokenize, pos_tag, ne_chunk, tree2conlltags
import google
import wikipedia
import collections
import re


# ===============================================================
# Determiner le type de question location, date, person ,definition
def classifier_questions(question):
    q = question.lower().split()
    print(q[0], q[1])
    if q[0] == 'where':
        return 'Location'
    elif 'year' in question:
        return 'Date'
    elif 'country' in question:
        return 'Country'
    elif q[0] == 'who':
        return 'Person'
    elif q[0] == 'what':
        return 'Definition'
    else:

        return 'None'


# ===============================================================
###########################################################################
def google_search(question):
    first_page = google.search(question, 1)  # renvoie un tableau d'elements avec un attr description
    # print first_page
    top_three_result = []
    i = 0
    while i < 5:
        top_three_result.append(first_page[i].description)
        i += 1

    first_search = ''.join(top_three_result).encode('ascii', 'replace')
    # print first_search

    ne_tree = (ne_chunk(pos_tag(word_tokenize(first_search))))

    iob_tagged = tree2conlltags(ne_tree)

    ss = [tuple(map(str, eachTuple)) for eachTuple in iob_tagged]
    question_type = classifier_questions(question)
    print("question_type: "), question_type
    if question_type == 'None':
        ans = "Oops! I don't know."
    else:
        google_answer = []
        if question_type == 'Person':
            for i in range(len(ss)):
                if ss[i][2] == 'B-PERSON' or ss[i][2] == 'I-PERSON':
                    google_answer.append(ss[i][0])
        elif question_type == 'Country':
            print("country identified")
            for i in range(len(ss)):
                if ss[i][2] == 'B-GPE' or ss[i][2] == 'I-GPE':
                    google_answer.append(ss[i][0])
        elif question_type == 'Location':
            for i in range(len(ss)):
                if ss[i][2] == 'B-LOCATION' or ss[i][2] == 'I-LOCATION':
                    google_answer.append(ss[i][0])
        elif question_type == 'Date':
            for i in range(len(ss)):
                if ss[i][2] == 'B-DATE' or ss[i][2] == 'I-DATE':
                    google_answer.append(ss[i][0])
        print("google: "), google_answer
        if not google_answer:
            ans = "Oops, I don't know! "
        else:
            print("inside else")
            counts = collections.Counter(google_answer)
            print("counts: "), counts
            t = counts.most_common(4)
            candidate_answer = [seq[0] for seq in t]
            print("candidate_answer")
            new_list = sorted(google_answer, key=lambda x: -counts[x])
            print("new_list"), new_list
            ans = ' '.join(new_list)
            for i in range(len(candidate_answer)):
                candidate_answer[i] = 'Candidate Answer ' + str(i+1)+' ' + candidate_answer[i]
            candidate_answer = '\n'.join(candidate_answer)
            ans = candidate_answer
    return ans
##################################################################################


def wiki_search(question):
    l = question.split(' ')
    if len(l) > 2:
        ques = " ".join(l[2:])
    try:
        print("recherche wikipedia")
        ans = (wikipedia.summary(question, sentences=1)).encode('ascii', 'ignore')
        ans = re.sub('([(].*?[)])', "", ans)
        print(ans)
        link = wikipedia.page(ques)
        ans = ans + '\n Pour plus d\'informations: '+link.url
        print('Reference: ', link.url)
        print("reponse")
    except :
        print("recherche wiki echouée")
        google_search(question)
    return ans


def reponse_finale(question):
    try:
        app_id = 'W837XL-LKW945H2AU'    # l'id de mon application
        if not app_id:
            print("id de notre application")
        client = wolframalpha.Client(app_id)
        res = client.query(question)  # wolram alpha repond a certaines questions what,when mais pas a who
        ans = str(next(res.results).text).replace('.', '.\n')

        if ans == 'None':
            print("ans is none")
            q_type = classifier_questions(question)
            if q_type == 'Definition' or q_type == 'Location':
                print("except-wiki")
                ans = wiki_search(question)
            if len(question.split()) <= 5:
                print("none-wiki")
                ans = wiki_search(question)
            else:
                print("none-google")
                ans = google_search(question)
                print("google answ: "),ans

        return ans

    except :
        try:
            print("Exception au premier demarage")
            q_type = classifier_questions(question)
            if q_type == 'Definition' or q_type == 'Location':
                print("except-wiki")
                ans = wiki_search(question)
            if len(question.split()) <= 5:
                print("except-wiki question < 5 words")
                ans = wiki_search(question)
            else:
                print("except-google")
                ans = google_search(question)
                print("google ans: "), ans

            return ans
        except:
            return "Oops! I don't know. Try something else"
