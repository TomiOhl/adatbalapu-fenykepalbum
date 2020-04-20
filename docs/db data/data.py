import random


# *** USERS TABLE ***

# Generate full names

vezetekNevek = ['Nagy', 'Kovács', 'Tóth', 'Szabó', 'Horváth', 'Varga', 'Kiss', 'Molnár', 'Németh', 'Farkas', 'Balog', 'Papp', 'Takács', 'Juhász', 'Lakatos', 'Mészáros', 'Oláh', 'Simon', 'Rácz', 'Fekete']
keresztNevek = ['Bence', 'Hanna', 'Lajos', 'Júlia', 'Péter', 'Mária', 'Zoltán', 'Erika', 'Gergő', 'Adrienn', 'Tamás', 'Jázmin', 'László', 'Krisztina', 'József', 'Laura', 'Zsolt', 'Dóra', 'Balázs', 'Tünde']
fullNames = []

for vnev in vezetekNevek:
	for knev in keresztNevek:
		fullNames.append(vnev + " " + knev)

#print(fullNames)

# Generate email addresses and nicknames

emailAddresses = []
nickNames = []

for nev in fullNames:
	nev = nev.replace(' ', '.').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ő', 'o').replace('ö', 'o').replace('ú', 'u').replace('ű', 'u').replace('ü', 'u')
	emailAddresses.append(nev.lower() + '@gmail.com')
	nickNames.append(nev.replace('.', '_'))

#print(emailAddresses)
#print(nickNames)

# Generate passwords

passwords = []

for nev in fullNames:
	pwd = nev.replace(' ', '').lower().replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ő', 'o').replace('ö', 'o').replace('ú', 'u').replace('ű', 'u').replace('ü', 'u')
	passwords.append(pwd)

#print(passwords)

# Generate birthdays

birthdays = []

while len(birthdays) < 400:
	datum = str(random.randint(1960, 2000)) + "-" + str(random.randint(1, 12)) + "-" + str(random.randint(1, 28))
	if datum not in birthdays:
		birthdays.append(datum)

#print(birthdays)

# locations: randint. Városok száma: hu(177), sk(71), ro(44), rs(55), das macht 347 zusammen


# *** Countries table ***

country_continent = []
flags = []
countries_length = 0
with open('countries_and_continents.txt', 'r') as cclist:
	lines = cclist.readlines()
	for line in lines:
		if line.startswith('['):
			continent = (line.replace('[ ', '').replace(' ]', '').strip())
		else:
			countries_length += 1
			country_continent.append(f"'{line.strip()}', '{continent}'")
			flags.append(line.strip().lower().replace(' ', '').replace('-', '').replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ő', 'o').replace('ö', 'o').replace('ú', 'u').replace('ű', 'u').replace('ü', 'u')[:10])


# *** Settlements table ***

settlement_country = []
settlements_length = 0

# Hungary
with open('hu.csv') as hu:
	lines = hu.readlines()
	for line in lines:
		if not line.startswith('city'):
			settlements_length += 1
			line = line.split(',')[0]
			settlement_country.append(f"'{line.strip()}', 138")

# Slovakia
with open('sk.csv') as sk:
	lines = sk.readlines()
	for line in lines:
		if not line.startswith('city'):
			settlements_length += 1
			line = line.split(',')[0]
			settlement_country.append(f"'{line.strip()}', 157")

# Serbia
with open('rs.csv') as rs:
	lines = rs.readlines()
	for line in lines:
		if not line.startswith('city'):
			settlements_length += 1
			line = line.split(',')[0]
			settlement_country.append(f"'{line.strip()}', 155")

# Romania
with open('ro.csv') as ro:
	lines = ro.readlines()
	for line in lines:
		if not line.startswith('city'):
			settlements_length += 1
			line = line.split(',')[0]
			settlement_country.append(f"'{line.strip()}', 149")


# *** Generate "INSERT INTOs" ***

insertIntoUsers = []
insertIntoCountries = []
insertIntoSettlements = []

for i in range(400):
	insertIntoUsers.append("INSERT INTO Users VALUES ('" + nickNames[i] + "','" + emailAddresses[i] + "','" + passwords[i] + "','" + fullNames[i] + "'," + str(random.randint(0, settlements_length-1)) + ",TO_DATE('" + birthdays[i] + "', 'YYYY-MM-DD'));\n")

for i in range(countries_length):
	insertIntoCountries.append(f"INSERT INTO Countries VALUES ({str(i)}, {country_continent[i]}, '{flags[i]}');\n")

for i in range(settlements_length):
	insertIntoSettlements.append(f"INSERT INTO Settlements VALUES ({str(i)}, {settlement_country[i]});\n")

with open("InsertIntoUsers.sql", "w") as t:
	for i in insertIntoUsers:
		t.write(i)
	print("User inserts generated.")

with open("InsertIntoCountries.sql", "w") as t:
	for i in insertIntoCountries:
		t.write(i)
	print("Country inserts generated.")

with open("InsertIntoSettlements.sql", "w") as t:
	for i in insertIntoSettlements:
		t.write(i)
	print("Settlement inserts generated.")
