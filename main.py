from urllib.request import urlopen

import pandas
from bs4 import BeautifulSoup
import pandas as pd
import re

wiki = "https://en.wikipedia.org/wiki/Gal_Gadot"
page = urlopen(wiki)

soup = BeautifulSoup(page)
film_table = soup.find('table', class_='wikitable sortable')

Year = []
Title = []
Role = []
Director = []
tmp_year = ''
url_movies = []

for row in film_table.findAll("tr"):
    cells = row.findAll('td')
    if len(cells) == 5:
        tmp_year = cells[0].find(text=True).strip('\n')
        Year.append(tmp_year)
        Title.append(cells[1].find(text=True).strip('\n'))
        url_movies.append("https://en.wikipedia.org" + cells[1].a.get("href"))
        Role.append(cells[2].find(text=True).strip('\n'))
        Director.append(cells[3].find(text=True).strip('\n'))
    elif len(cells) == 4:
        Year.append(tmp_year)
        Title.append(cells[0].find(text=True).strip('\n'))
        url_movies.append("https://en.wikipedia.org" + cells[0].a.get("href"))
        Role.append(cells[1].find(text=True).strip('\n'))
        Director.append(cells[2].find(text=True).strip('\n'))

Name = []
Birth = []
Country = []
Awards = []
characters_url = []
characters_dict = {}

for movie in url_movies:
    url = urlopen(movie)
    curr_soup = BeautifulSoup(url)
    cast_list = curr_soup.find("span", {"id": re.compile("cast.*|Cast.*")}).findNext('ul').findAll('li')
    for character in cast_list:
        # if character.find('a').get("title") != "Gal Gadot":
        if character.find('a'):
            name = character.find('a').get("href")
            # characters_url.append("https://en.wikipedia.org" + name)
            if "/wiki/" not in name:
                # print(name)
                continue
            if "/wiki/Gal_Gadot" in name:
                continue
            if name not in characters_dict:
                characters_dict[name] = 1
            else:
                characters_dict[name] = characters_dict[name] + 1
for name in characters_dict.keys():
    url = urlopen("https://en.wikipedia.org" + name)
    curr_soup = BeautifulSoup(url)
    biography_table = curr_soup.find('table', class_='infobox biography vcard')
    # need to check this issue
    if not biography_table:
        biography_table = curr_soup.find('table', class_='infobox vcard')
    # only one charachter
    if not biography_table:
        biography_table = curr_soup.find('table', class_='infobox vcard plainlist')

    curr_name = curr_soup.find('h1', class_='firstHeading').get_text()
    # curr_name = biography_table.find('div', class_='fn').get_text()
    Name.append(curr_name)
    # print(curr_name)
    if biography_table.find('span', class_='bday'):
        birth_year = biography_table.find('span', class_='bday').get_text().split('-')[0]
    else:
        birth_year = 'NA'
        # need to ask what to do with this issue
        for born in biography_table.findAll('tr'):
            if "Born" in str(born):
                regex = "\d{4}"
                born = str(born).replace('"', ' ')
                match = str(re.findall(regex, born)).replace('[', '').replace(']', '').replace('\'', '')
                birth_year = match
                if len(birth_year) == 0:
                    birth_year = 'NA'
                print(curr_name)
    Birth.append(birth_year)
    # print(birth_year)

    if biography_table.find('div', class_='birthplace'):
        birth_country = biography_table.find('div', class_='birthplace').get_text()
        split = birth_country.split(', ')
        birth_country = split[len(split) - 1]
    else:
        birth_country = 'NA'
        # need to ask what to do with this issue
        for born in biography_table.findAll('tr'):
            if "Born" in str(born):
                tmp = str(born.find('td').get_text()).split(',')
                if not bool(re.search(r'\d', tmp[len(tmp) - 1])):
                    birth_country = tmp[len(tmp) - 1]
                else:
                    birth_country = 'NA'
    # print(birth_country)
    Country.append(birth_country)
    awards_label = curr_soup.find("span", {"id": "Awards_and_nominations"})
    if not awards_label:
        award_count = 'NA'
        Awards.append(award_count)
        # print(award_count)
        continue
    award_count = 0
    awards_table = awards_label.findNext('table', class_='wikitable sortable')
    if not awards_table:
        awards_table = awards_label.findNext('table', class_='wikitable')
    if not awards_table:
        list_url = "https://en.wikipedia.org" + awards_label.findNext('div',
                                                                      class_='hatnote navigation-not-searchable').find(
            'a').get('href')
        url = urlopen(list_url)
        curr_soup = BeautifulSoup(url)
        awards_tables = curr_soup.findAll('table', class_="wikitable")
        # if not awards_table:
        #     awards_tables = curr_soup.findAll('table', class_="wikitable sortable")
        for table in awards_tables:
            for row in table.findAll("tr"):
                if row.find('td', class_="yes table-yes2"):
                    award_count = award_count + 1
        # print(award_count)
        Awards.append(award_count)
        continue
        # bio_awards_table = curr_soup.find('table', class_='infobox')
        # if not bio_awards_table:
        #     award_count = 'NA'
        #     Awards.append(award_count)
        #     continue
        # won_awards = []
        # for row in bio_awards_table.findAll('tr'):
        #     all_won = row.findAll('td', class_="yes table-yes2")
        #     if not all_won:
        #         continue
        #     else:
        #         won_awards.append(all_won)
        # won_awards = won_awards[len(won_awards)-1]
        # award_count = won_awards[len(won_awards)-1].get_text()
        # Awards.append(award_count)
        # print(award_count)
        # continue
    if not awards_table:
        award_count = 'NA'
        continue
    awards_table = awards_table.findAll('tr')
    for award in awards_table:
        if award.find('td', class_="yes table-yes2"):
            award_count = award_count + 1
    Awards.append(award_count)
    # print(award_count)

# df = pd.DataFrame({'Vin Diesel': list('Name')})

df = pd.DataFrame(Name, columns=['Name'])
df['Birth'] = Birth
df['Country'] = Country
df['Awards'] = Awards
pandas.set_option('display.max_rows', df.shape[0] + 1)
print(df)
# print(df.groupby('Vin Diesel').count())


# df = pd.DataFrame(Year, columns=['Year'])
# df['Title'] = Title
# df['Role'] = Role
# df['Director'] = Director

# print(Year)
# print(Title)
# print(Role)
# print(Director)