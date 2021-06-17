import aqgFunction


# Main Function
def main():
    # Create AQG object
    aqg = aqgFunction.AutomaticQuestionGenerator()

    inputText = "Barça conceded a capital defeat on Saturday night against Real Madrid. A result which complicates the affairs of the Blaugrana in the title race and which generates a lot of frustration. Pique exacerbated by arbitration decisions was annoyed. The additional time of four minutes deemed insufficient and the penalty not awarded for an alleged foul by Mendy on Braithwaite has angered the Blaugrana."

    questionList = aqg.aqgParse(inputText)
    aqg.display(questionList)


    return 0


def generer(entree):

    aqg = aqgFunction.AutomaticQuestionGenerator()

    questionList = aqg.aqgParse(entree)

    return aqg.resultat(questionList)


# Call Main Function
if __name__ == "__main__":
    inputText = "Barça conceded a capital defeat on Saturday night against Real Madrid. A result which complicates the affairs of the Blaugrana in the title race and which generates a lot of frustration. Pique exacerbated by arbitration decisions was annoyed. The additional time of four minutes deemed insufficient and the penalty not awarded for an alleged foul by Mendy on Braithwaite has angered the Blaugrana."

    r = generer(inputText)
    print(r)

