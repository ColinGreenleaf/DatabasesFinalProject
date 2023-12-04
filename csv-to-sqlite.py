
import sqlite3
import csv

con = sqlite3.connect("hearthcards.db")

cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS cards")
cur.execute("DROP TABLE IF EXISTS dust_costs")
cur.execute("DROP TABLE IF EXISTS mechanics")
cur.execute("DROP TABLE IF EXISTS play_requirements")

cur.execute("CREATE TABLE cards (card_id, player_class, type, name, card_set, text, cost, attack, health, rarity, collectible, flavor, race, hte, hteg, tat, fac, durability)")
cur.execute("CREATE TABLE dust_costs (card_id, action, cost)")
cur.execute("CREATE TABLE mechanics (card_id, mechanic)")
cur.execute("CREATE TABLE play_requirements (card_id, requirement, value)")

cardsFile = open('cards.csv', 'r', encoding='Windows-1252')
dustCostsFile = open('dust_costs.csv', 'r', encoding='Windows-1252')
mechanicsFile = open('mechanics.csv', 'r', encoding='Windows-1252')
playRequirementsFile = open('play_requirements.csv', 'r', encoding='Windows-1252')


cardsContents = csv.reader(cardsFile)
dustCostsContents = csv.reader(dustCostsFile)
mechanicsContents = csv.reader(mechanicsFile)
playRequirementsContents = csv.reader(playRequirementsFile)




cardsHeader = next(cardsContents)
dustCostsHeader = next(dustCostsContents)
mechanicsHeader = next(mechanicsContents)
playRequirementsHeader = next(playRequirementsContents)

print("first row of cardsContents:")
print(next(cardsContents))


insertCards = "insert into cards(card_id, player_class, type, name, card_set, text, cost, attack, health, rarity, collectible, flavor, race, hte, hteg, tat, fac, durability) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
cur.executemany(insertCards, cardsContents)
insertDustCosts = '''insert into dust_costs(card_id, action, cost) values(?,?,?)'''
cur.executemany(insertDustCosts, dustCostsContents)
insertMechanics = '''insert into mechanics(card_id, mechanic) values(?,?)'''
cur.executemany(insertMechanics, mechanicsContents)
insertPlayRequirements = '''insert into play_requirements(card_id, requirement, value) values(?,?,?)'''
cur.executemany(insertPlayRequirements, playRequirementsContents)

removeNonCollectible = '''DELETE FROM cards WHERE collectible is not 'True' '''
removeNonCollectibleDustCosts = '''DELETE FROM dust_costs WHERE card_id NOT IN (SELECT card_id FROM cards)'''
removeNonCollectibleMechanics = '''DELETE FROM mechanics WHERE card_id NOT IN (SELECT card_id FROM cards)'''
removeNonCollectiblePlayRequirements = '''DELETE FROM play_requirements WHERE card_id NOT IN (SELECT card_id FROM cards)'''

cur.execute(removeNonCollectible)
cur.execute(removeNonCollectibleDustCosts)
cur.execute(removeNonCollectibleMechanics)
cur.execute(removeNonCollectiblePlayRequirements)

# drop columns  hte, hteg, tat, fac
dropHte = '''ALTER TABLE cards DROP COLUMN hte'''
dropHteg = '''ALTER TABLE cards DROP COLUMN hteg'''
dropTat = '''ALTER TABLE cards DROP COLUMN tat'''
dropFac = '''ALTER TABLE cards DROP COLUMN fac'''

cur.execute(dropHte)
cur.execute(dropHteg)
cur.execute(dropTat)
cur.execute(dropFac)


con.commit()

con.close()

cardsFile.close()
dustCostsFile.close()
mechanicsFile.close()
playRequirementsFile.close()

