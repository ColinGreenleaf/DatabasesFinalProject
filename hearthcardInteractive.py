import sqlite3
import csv
import os


def menu():
    print("Please select an option:")
    print("1. Create a new card")
    print("2. Search for a card")
    print("3. Get card statistics")
    return input("\n>> ")


def main():
    print("Welcome to Hearthcard Interactive!")
    choice = menu()
    if choice == "1":
        createCard()


def createCard():
    con = sqlite3.connect("hearthcards.db")
    cur = con.cursor()

    # get list of mechanics
    mechanicsList = getMechanics()
    classList = ["neutral", "druid", "hunter", "mage", "paladin", "priest", "rogue", "shaman", "warlock", "warrior"]
    typeList = ["minion", "spell", "weapon"]
    rarityList = ["common", "rare", "epic", "legendary"]

    cardclass = input(
        "What class is the card for? (neutral, druid, hunter, mage, paladin, priest, rogue, shaman, warlock, warrior) ")
    cardtype = input("What type of card is it? (minion, spell, weapon) ")
    name = input("What is the name of the card? ")
    cost = input("What is its mana cost? ")
    rarity = input("What is its rarity? (common, rare, epic, legendary) ")
    if cardtype == "minion":
        attack = input("What is its attack? ")
        health = input("What is its health? ")
        tribe = input("What is its tribe? ")
        text = input("What is its text? ")
        durability = None
    elif cardtype == "spell":
        text = input("What is its text? ")
        attack = None
        health = None
        tribe = None
        durability = None
    elif cardtype == "weapon":
        attack = input("What is its attack? ")
        durability = input("What is its durability? ")
        text = input("What is its text? ")
        health = None
        tribe = None

    flavor = input("Finally, give it some flavor text! ")

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


main()

