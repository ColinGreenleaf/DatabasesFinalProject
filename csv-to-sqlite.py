
import sqlite3
import csv

# connect to database
con = sqlite3.connect("hearthcards.db")
cur = con.cursor()

# drop tables if they already exist
cur.execute("DROP TABLE IF EXISTS cards")
cur.execute("DROP TABLE IF EXISTS dust_costs")
cur.execute("DROP TABLE IF EXISTS mechanics")
cur.execute("DROP TABLE IF EXISTS play_requirements")

# create tables
cur.execute("CREATE TABLE cards (card_id, player_class, type, name, card_set, text, cost, attack, health, rarity, collectible, flavor, race, hte, hteg, tat, fac, durability)")
cur.execute("CREATE TABLE dust_costs (card_id, action, cost)")
cur.execute("CREATE TABLE mechanics (card_id, mechanic)")
cur.execute("CREATE TABLE play_requirements (card_id, requirement, value)")

# open csv files
cardsFile = open('cards.csv', 'r', encoding='Windows-1252')
dustCostsFile = open('dust_costs.csv', 'r', encoding='Windows-1252')
mechanicsFile = open('mechanics.csv', 'r', encoding='Windows-1252')
playRequirementsFile = open('play_requirements.csv', 'r', encoding='Windows-1252')

# read csv files
cardsContents = csv.reader(cardsFile)
dustCostsContents = csv.reader(dustCostsFile)
mechanicsContents = csv.reader(mechanicsFile)
playRequirementsContents = csv.reader(playRequirementsFile)

# skip headers
cardsHeader = next(cardsContents)
dustCostsHeader = next(dustCostsContents)
mechanicsHeader = next(mechanicsContents)
playRequirementsHeader = next(playRequirementsContents)

# insert all data into tables
insertCards = "insert into cards(card_id, player_class, type, name, card_set, text, cost, attack, health, rarity, collectible, flavor, race, hte, hteg, tat, fac, durability) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
cur.executemany(insertCards, cardsContents)
insertDustCosts = '''insert into dust_costs(card_id, action, cost) values(?,?,?)'''
cur.executemany(insertDustCosts, dustCostsContents)
insertMechanics = '''insert into mechanics(card_id, mechanic) values(?,?)'''
cur.executemany(insertMechanics, mechanicsContents)
insertPlayRequirements = '''insert into play_requirements(card_id, requirement, value) values(?,?,?)'''
cur.executemany(insertPlayRequirements, playRequirementsContents)

# remove non-collectible cards and cards with no flavor text
removeNonCollectible = '''DELETE FROM cards WHERE collectible is not 'True' '''
removeNoFlavor = '''DELETE FROM cards WHERE flavor is '' '''

# remove non-collectible cards from dust_costs, mechanics, and play_requirements
removeNonCollectibleDustCosts = '''DELETE FROM dust_costs WHERE card_id NOT IN (SELECT card_id FROM cards)'''
removeNonCollectibleMechanics = '''DELETE FROM mechanics WHERE card_id NOT IN (SELECT card_id FROM cards)'''
removeNonCollectiblePlayRequirements = '''DELETE FROM play_requirements WHERE card_id NOT IN (SELECT card_id FROM cards)'''

# remove extraneous crafting costs
removeExtraneousCrafting = '''DELETE FROM dust_costs WHERE action is not 'CRAFTING_NORMAL' '''

# execute all removals
cur.execute(removeNonCollectible)
cur.execute(removeNoFlavor)
cur.execute(removeNonCollectibleDustCosts)
cur.execute(removeNonCollectibleMechanics)
cur.execute(removeNonCollectiblePlayRequirements)
cur.execute(removeExtraneousCrafting)

# Drop columns hte, hteg, tat, fac since they are not used
alterTableQuery = '''
CREATE TABLE new_cards AS
SELECT card_id, player_class, type, name, card_set, text, cost, attack, health, rarity, flavor, race, durability
FROM cards;
'''

# Execute the new table creation
cur.execute(alterTableQuery)

# Drop the old table
cur.execute("DROP TABLE cards")

# Rename the new table to the original table name
cur.execute("ALTER TABLE new_cards RENAME TO cards")

# commit changes and close files
con.commit()
con.close()

cardsFile.close()
dustCostsFile.close()
mechanicsFile.close()
playRequirementsFile.close()

