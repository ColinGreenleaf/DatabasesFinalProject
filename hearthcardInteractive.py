import sqlite3
import csv
import os
import constants as c

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
        searchSingleCard()
    elif plurality == "multiple":
        searchMultipleCards()

def searchSingleCard():
    name = input("What is the name of the card? (case sensitive)\n>> ")
    # name = "Argent Lance"
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
    pass

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
    print("placeholder")


main()
