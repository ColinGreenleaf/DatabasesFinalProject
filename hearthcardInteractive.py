# %%
import sqlite3
import constants as c
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def main():
    print("Welcome to Hearthcard Interactive!")
    navigate()

def options():
    print("Please select an option:")
    print("1. Create a new card")
    print("2. Search for a card")
    print("3. Get card statistics")
    return input("\n>> ")


def navigate():
    choice = options()
    if choice == "1":
        createCard()
    elif choice == "2":
        searchCard()
    elif choice == "3":
        cardStats()



def searchCard():
    plurality = input("Would you like to search for a single card or multiple cards? (single, multiple)\n>> ")
    if plurality == "single":
        name = input("What is the name of the card? (case sensitive)\n>> ")
        searchSingleCard(name)
    elif plurality == "multiple":
        searchMultipleCards()

def searchSingleCard(name):
    card = getCard(name)
    if card is not None:
        # get the card's values
        card_id = card[0]
        cardclass = card[1]
        cardtype = card[2]
        name = card[3]
        set = card[4]
        text = card[5]
        cost = card[6]
        attack = card[7]
        health = card[8]
        rarity = card[9]
        flavor = card[10]
        tribe = card[11]
        durability = card[12]

        text = text.replace("<b>", "")
        text = text.replace("</b>", "")

        if cardtype == "MINION":
            renderMinion(cost, name, text, attack, health, tribe)
        elif cardtype == "SPELL":
            renderSpell(cost, name, text)
        elif cardtype == "WEAPON":
            renderWeapon(cost, name, text, attack, durability)

        print("\n")
        print("a", rarity.capitalize(), cardclass.capitalize(), cardtype.capitalize(),
              'from', c.longSetNames[set])

        print("Cost to craft:", getDustCost(rarity), "dust")
        print("Flavor text:", flavor)

        selectChoice = input("What would you like to do with this card? (delete, edit, exit)\n>> ")

        if selectChoice == "delete":
            deleteCard(card_id)
        elif selectChoice == "edit":
            editCard(card_id, cardtype)
        elif selectChoice == "exit":
            navigate()

def searchMultipleCards():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()

    fields = ["cost", "attack", "health", "rarity", "class", "type", "tribe", "durability", "set", "mechanics"]
    print("what field would you like to search by?")
    print(fields)
    choice = input(">> ")
    if choice not in fields:
        print("That is not a valid field!")
        return
    if choice in ["attack", "health", "cost", "durability"]:
        print("you've chosen an integer field. what operator would you like to use? (<, >, =, <=, >=)")
        operator = input(">> ")
        if operator not in ["<", ">", "=", "<=", ">="]:
            print("That is not a valid operator!")
            return
        value = int(input("What value would you like to search against?\n>> "))
        #wrap value in quotes so sqlite can compare it to a string
        value = "'" + str(value) + "'"
        #only show those with values of 10 if the operand is >, >=, or of val is 10 itslef
        if operator in [">", ">=", "="] or value == "'10'":
            execString = "SELECT name FROM cards WHERE type != 'SPELL' AND " + choice + " " + operator + " " + str(value) + " ORDER BY " + choice + " ASC"
        else:
            execString = "SELECT name FROM cards WHERE type != 'SPELL' AND " + choice + " < '10' AND " + choice + " " + operator + " " + value + " ORDER BY " + choice + " ASC"
    elif choice == "mechanics":
        mechanicChoice = input("Would you like to search for a keyword of a play requirement?\n>> ")
        if mechanicChoice == "keyword":
            value = input("What keyword would you like to search for?\n>> ")
            value = value.upper().replace(" ", "_")
            execString = "SELECT name FROM cards JOIN mechanics ON cards.card_id = mechanics.card_id WHERE mechanic = '" + value + "'"
        elif mechanicChoice == "play requirement":
            value = input("What play requirement would you like to search for?\n>> ")
            value = value.upper().replace(" ", "_")
            value = "REQ_" + value
            execString = "SELECT name FROM cards JOIN play_requirements ON cards.card_id = play_requirements.card_id WHERE play_requirement = '" + value + "'"

    else:
        value = input("What value from your chosen field would you like the results to have?\n>> ")
        if choice in ["rarity", "class", "type", "tribe", "set"]:
            value = value.upper()

        execString = "SELECT * FROM cards WHERE " + choice + " = '" + value + "'"

    cards = cur.execute(execString)
    cards = cards.fetchall()
    con.close()
    if len(cards) == 0:
        print("No cards found!")
        return

    #print card names 10 at a time, and prompt the user to see the next 10
    i = 0
    renderNext = True
    while renderNext:
        j = i+9
        # if there are less than 10 cards left, print them all
        if j + 1 >= len(cards):
            for v in range(i, len(cards)):
                print(cards[v][0])
            renderNext = False
            break
        for v in range(i, j):
            print(cards[v][0])
        if renderNext:
            choice = input("type n to see the next 10 cards, or type the name of a card to view it.\n>> ")
            if choice != "n":
                renderNext = False
                searchSingleCard(choice)

    navigate()

def deleteCard(card_id):
    delete = "DELETE FROM cards WHERE card_id = '" + card_id + "'"
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()
    cur.execute(delete)
    con.commit()
    con.close()
    print("Card deleted successfully!")

def editCard(card_id, cardtype):
    print("What would you like to edit?")
    print("General Attributes: cost, name, rarity, flavor, class, type, text")
    print("Minion-Specific Attributes: attack, health, tribe")
    print("Weapon-Specific Attributes: attack, durability")



    attribute = input(">> ")
    attribute = attribute.lower()
    if cardtype != "MINION" and attribute in ["health", "tribe"]:
        print("This is not a minion!")
        return
    if cardtype != "WEAPON" and attribute == "durability":
        print("This is not a weapon!")
        return

    if attribute == "class":
        attribute = "player_class"
    print("What would you like to change it to?")
    value = input(">> ")
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()
    execString = "UPDATE cards SET " + attribute + " = '" + value + "' WHERE card_id = '" + card_id + "'"
    cur.execute(execString)
    con.commit()
    con.close()
    print("Card edited successfully!")


def createCard():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()

    # get list of mechanics
    mechanicsList = getMechanics()
    classList = ["neutral", "druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"]
    typeList = ["minion", "spell", "weapon"]
    rarityList = ["common", "rare", "epic", "legendary"]

    cardclass = input(
        "What class is the card for? (neutral, druid, hunter, mage, paladin, priest, rogue, shaman, warlock, warrior)\n>> ")
    cardtype = input("What type of card is it? (minion, spell, weapon)\n>> ")
    name = input("What is the name of the card?\n>> ")
    cost = input("What is its mana cost?\n>> ")
    rarity = input("What is its rarity? (common, rare, epic, legendary)\n>> ")
    if cardtype.casefold() == "minion".casefold():
        attack = input("What is its attack?\n>> ")
        health = input("What is its health?\n>> ")
        tribe = input("What is its tribe?\n>> ")
        text = input("What is its text?\n>> ")
        durability = None
    elif cardtype.casefold() == "spell".casefold():
        text = input("What is its text?\n>> ")
        attack = None
        health = None
        tribe = None
        durability = None
    elif cardtype.casefold() == "weapon".casefold():
        attack = input("What is its attack?\n>> ")
        durability = input("What is its durability?\n>> ")
        text = input("What is its text?\n>> ")
        health = None
        tribe = None

    flavor = input("Finally, give it some flavor text!\n>> ")

    id = getNextAvailableID()

    card = [id, cardclass, cardtype, name, "CUSTOM", text, cost, attack, health, rarity, flavor, tribe, durability]
    cur.execute("INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", card)

    # if there are any mechanics in the text, add them to the card_mechanics table
    for mechanic in mechanicsList:
        if mechanic.casefold() in text.casefold():
            cur.execute("INSERT INTO card_mechanics VALUES (?,?)", (id, mechanic.upper().replace(" ", "_")))

    # add the dust cost to the dust_costs table
    dustCostData = [id, "CRAFTING_NORMAL", getDustCost(rarity)]
    cur.execute("INSERT INTO dust_costs VALUES (?,?,?)", dustCostData)

    # TODO: add play requirements to the play_requirements table

    print("Card created successfully!")

    con.commit()
    con.close()


def getMechanics():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()
    mechanics = cur.execute("SELECT DISTINCT mechanic FROM mechanics")
    # get list of mechanics
    mechanicsList = []
    for mechanic in mechanics:
        mechanicsList.append(mechanic[0])
    # replace underscores with spaces
    for i in range(len(mechanicsList)):
        mechanicsList[i] = mechanicsList[i].replace("_", " ")
    return mechanicsList


def getNextAvailableID():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()
    # get the current largest ID from the custom cards in the cards table
    maxID = cur.execute("SELECT MAX(card_id) FROM cards where card_id like 'CU_%'")
    # pull out the value of the maxID
    maxID = maxID.fetchone()[0]
    # if there are no cards in the database, return 1
    if maxID is None:
        return "CU_001"
    # get the last 3 digits of the maxID and convert to an int
    intID = int(maxID[-3:])
    # encode the new id number as a string with three digits and combine it with the prefix
    newID = "CU_" + str(intID + 1).zfill(3)

    return newID


def getDustCost(rarity):
    if rarity == "common":
        return 40
    elif rarity == "rare":
        return 100
    elif rarity == "epic":
        return 400
    elif rarity == "legendary":
        return 1600
    else:
        return 0


def getCard(name):
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()
    card = cur.execute("SELECT * FROM cards WHERE name = ?", (name,))
    card = card.fetchone()
    con.close()
    if card is not None:
        return card
    else:
        return None


def renderLine(text):
    return "|" + text.center(c.cardwidth, " ") + "|"


def renderMinion(cost, name, text, attack, health, tribe):
    text_lines = []
    # split card text into lines by splitting at the first space after every 20 characters
    while len(text) > 0:
        if len(text) > 22:
            text_lines.append(text[:22])
            text = text[22:]
        else:
            text_lines.append(text)
            text = ""

    print("________________________________")
    print("| " + cost + " |    /           \\         |")
    print("|___|   |             |        |")
    print("|       |             |        |")
    print("|       |             |        |")
    print("|________\\___________/_________|")
    print(renderLine(name))
    print("|______________________________|")
    print(renderLine(""))
    for line in text_lines:
        print(renderLine(line))
    print("|______________________________|")
    print("| " + attack + " |" + tribe.center(22, " ") + "| " + health + " |")
    print("|___|______________________|___|")


def renderSpell(cost, name, text):
    text_lines = []
    # split card text into lines by splitting at the first space after every 20 characters
    while len(text) > 0:
        if len(text) > 22:
            text_lines.append(text[:22])
            text = text[22:]
        else:
            text_lines.append(text)
            text = ""

    print("________________________________")
    print("| " + cost + " |                          |")
    print("|___|                          |")
    print("|                              |")
    print("|                              |")
    print("|______________________________|")
    print(renderLine(name))
    print("|______________________________|")
    print(renderLine(""))
    for line in text_lines:
        print(renderLine(line))
    print("|______________________________|")
    print("|______________________________|")


def renderWeapon(cost, name, text, attack, durability):
    text_lines = []
    # split card text into lines by splitting at the first space after every 20 characters
    while len(text) > 0:
        if len(text) > 22:
            text_lines.append(text[:22])
            text = text[22:]
        else:
            text_lines.append(text)
            text = ""

    print("________________________________")
    print("| " + cost + " |    _____________         |")
    print("|___|   /             \\        |")
    print("|      |               |       |")
    print("|       \\_____________/        |")
    print("|______________________________|")
    print(renderLine(name))
    print("|______________________________|")
    print(renderLine(""))
    for line in text_lines:
        print(renderLine(line))
    print("|______________________________|")
    print("| " + attack + " |" + "".center(22, " ") + "| " + durability + " |")
    print("|___|______________________|\\_/|")

def cardStats():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()

    # list of numerical fields
    yAxisTwo = ["cost", "attack", "health", "durability"]

    # list of all fields
    xAxis = ["cost", "attack", "health", "rarity", "type", "race", "durability", "card_set"]
    # list of numerical fields
    xAxisTwo = ["cost", "attack", "health", "durability"]

    # one variable plots count of cards by field
    # two variable plots fieldX vs fieldY and count by density via color gradient
    numberAxis = input("Would you like to visualize one or two variables?  \n>> ")

    if numberAxis == "two":


        print("what field would you like to make the Y axis?")
        print(yAxisTwo)
        choiceY = input(">> ")

        print("what field would you like to make the X axis?")
        print(xAxisTwo)
        choiceX = input(">> ")


        if choiceY not in yAxisTwo or choiceX not in xAxisTwo:
            print("That is not a valid field!")
            return
        else:
            #execString = "SELECT avg("+choiceX+") as '"+choiceX+"', "+choiceY+", count("+choiceY+") as 'count' FROM cards WHERE "+choiceX+" is not '' and "+choiceY+" is not ''"
            execString = "SELECT "+choiceX+", "+choiceY+" FROM cards WHERE "+choiceX+" is not '' and "+choiceY+" is not ''"

        cards = cur.execute(execString)
        cards = cards.fetchall()
        con.close()
        if len(cards) == 0:
            print("No cards found!")
            return

        df = pd.DataFrame(cards)

        df.columns = [choiceX,choiceY]

        # data in .db file is stored as strings, convert to int for proper visualization
        df = df.astype({choiceX:'int'})
        df = df.astype({choiceY:'int'})



        x = df[choiceX]
        y = df[choiceY]


        fig, ax = plt.subplots(figsize=(9, 6))

        hexbin = ax.hexbin( x= x, y= y, gridsize = 20,
                                cmap = 'Greens' 
                        )                
        ax.set_xlabel(choiceX)
        ax.set_ylabel(choiceY)
        cb = fig.colorbar(hexbin, ax=ax, label='Count of Cards')
        ax.set_title('Hexbin chart, third variable as count of cards', size = 14)

        plt.show()



    elif numberAxis == "one":
        print("what field would you like to make the X axis?")
        print(xAxis)
        choiceX = input(">> ")


        if choiceX not in xAxis:
            print("That is not a valid field!")
            return
        else:
            execString = "SELECT "+choiceX+" FROM cards WHERE "+choiceX+" is not ''"
        
        cards = cur.execute(execString)
        cards = cards.fetchall()
        con.close()
        if len(cards) == 0:
            print("No cards found!")
            return

        df = pd.DataFrame(cards)
        df.columns = [choiceX]


        if choiceX in xAxisTwo:
            df = df.astype({choiceX:'int'})
        
        df[choiceX].value_counts().plot(kind='bar')
        plt.ylabel("Count", labelpad=14)
        plt.title("Count of Cards by Field", y=1.02)
        plt.show()







    navigate()


main()

# %%
