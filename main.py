from urllib.request import urlopen
from collections import Counter
from bs4 import BeautifulSoup
import pandas
import pandas as pd
import re
import matplotlib.pyplot as plt
import numpy as np
import unidecode

WIKI_URL = "https://en.wikipedia.org"
plt.rcdefaults()


def get_films_info():
    gal_gadot_wiki = WIKI_URL + "/wiki/Gal_Gadot"
    year = []
    title = []
    role = []
    director = []
    url_movies = []
    tmp_year = ''
    film_table = BeautifulSoup(urlopen(gal_gadot_wiki)).find('table', class_='wikitable sortable')
    for tr in film_table.findAll("tr"):
        cells = tr.findAll('td')
        if len(cells) == 5:
            tmp_year = cells[0].find(text=True).strip('\n')
            year.append(tmp_year)
            title.append(cells[1].find(text=True).strip('\n'))
            url_movies.append(WIKI_URL + cells[1].a.get("href"))
            role.append(cells[2].find(text=True).strip('\n'))
            director.append(cells[3].find(text=True).strip('\n'))
        elif len(cells) == 4:
            year.append(tmp_year)
            title.append(cells[0].find(text=True).strip('\n'))
            url_movies.append(WIKI_URL + cells[0].a.get("href"))
            role.append(cells[1].find(text=True).strip('\n'))
            director.append(cells[2].find(text=True).strip('\n'))
    return {
        'year': year,
        'title': title,
        'role': role,
        'director': director,
        'url_movies': url_movies
    }


def get_characters_pages(url_movies):
    name = []
    birth = []
    country = []
    awards = []
    characters_dict = {}
    characters_dict_with_page = {}
    for movie in url_movies:
        movie_page_html = BeautifulSoup(urlopen(movie))
        cast_list = movie_page_html.find("span", {"id": re.compile("cast.*|Cast.*")}).findNext('ul').findAll('li')
        if len(cast_list) == 1:
            separate_list = movie_page_html.find("span", {"id": re.compile("cast.*|Cast.*")}).findAllNext('ul')
            for separate in separate_list:
                if 'a' != separate.find('li').findNext().name:
                    break
                cast_list.append(separate.find('li'))
        if movie_page_html.find("span", {"id": "As_themselves"}):
            continue_list = movie_page_html.find("span", {"id": "As_themselves"}).findNext('ul').findAll('li')
            cast_list.extend(continue_list)
        for character in cast_list:
            if character.find('a'):
                character_url = character.find('a').get("href")
                character_name = unidecode.unidecode(character.find('a').get("title"))
                if "/wiki/" not in character_url:
                    array_name = character.find('a').get('title').split(" ")
                    character_name = array_name[0] + " " + array_name[1]
                    if character_name not in characters_dict:
                        characters_dict[character_name] = {
                            'count': 1,
                            'url': character.find('a').get("href")
                        }
                    else:
                        characters_dict[character_name]['count'] = characters_dict[character_name]['count'] + 1
                    name.append(character_name)
                    birth.append("NA")
                    country.append("NA")
                    awards.append("NA")
                    continue
                if "Gal Gadot" in character_name:
                    continue
                if character_name not in characters_dict:
                    characters_dict[character_name] = {
                        'count': 1,
                        'url': character.find('a').get("href")
                    }
                    characters_dict_with_page[character_name] = {
                        'count': 1,
                        'url': character.find('a').get("href")
                    }
                else:
                    characters_dict[character_name]['count'] = characters_dict[character_name]['count'] + 1
                    characters_dict_with_page[character_name]['count'] = characters_dict_with_page[character_name]['count'] + 1
            else:
                if "as" in character.get_text():
                    array_name = character.get_text().split(" ")
                    name_to_add = ""
                    for i in array_name:
                        if i != 'as':
                            name_to_add = name_to_add + i + " "
                        else:
                            name_to_add = name_to_add[:-1]
                            break
                    if name_to_add not in characters_dict:
                        characters_dict[name_to_add] = {
                            'count': 1,
                            'url': 'NA'
                        }
                    else:
                        characters_dict[name_to_add]['count'] = characters_dict[name_to_add]['count'] + 1
                    name.append(name_to_add)
                    birth.append("NA")
                    country.append("NA")
                    awards.append("NA")
    return {
        'name': name,
        'birth': birth,
        'country': country,
        'awards': awards,
        'characters_dict': characters_dict,
        'characters_dict_with_page': characters_dict_with_page
    }


def get_characters_info(characters_pages_info):
    name = characters_pages_info['name']
    birth = characters_pages_info['birth']
    country = characters_pages_info['country']
    awards = characters_pages_info['awards']
    characters_dict_with_page = characters_pages_info['characters_dict_with_page']
    for character_name in characters_dict_with_page.keys():
        url = urlopen(WIKI_URL + characters_dict_with_page[character_name]['url'])
        curr_soup = BeautifulSoup(url)
        biography_table = curr_soup.find('table', class_='infobox biography vcard')
        # need to check this issue
        if not biography_table:
            biography_table = curr_soup.find('table', class_='infobox vcard')
        # only one charachter
        if not biography_table:
            biography_table = curr_soup.find('table', class_='infobox vcard plainlist')
        curr_name = curr_soup.find('h1', class_='firstHeading').get_text()
        if '(' in curr_name:
            only_name = curr_name.split(" ")
            curr_name = ""
            for i in only_name:
                if '(' in i:
                    break
                curr_name = curr_name + i + " "
            curr_name = curr_name[:-1]
        # curr_name = biography_table.find('div', class_='fn').get_text()
        name.append(curr_name)
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
        birth.append(birth_year)
        # print(birth_year)

        if biography_table.find('div', class_='birthplace'):
            birth_country = biography_table.find('div', class_='birthplace').get_text()
            split = birth_country.split(', ')
            birth_country = split[len(split) - 1].replace(')', "")
            #in case of james franco
            if "U.S." in split[len(split) - 1]:
                birth_country = "U.S."
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
        country.append(birth_country)
        award_count = 0
        all_a_tags = curr_soup.findAll('a')
        list_url = None
        for curr_a in all_a_tags:
            list_title = str(curr_a.get('title'))
            if "List of awards" in list_title and curr_name in list_title:
                list_url = WIKI_URL + curr_a.get('href')
                break
        # list_url = curr_soup.findAll('div', class_='hatnote navigation-not-searchable')
        if list_url is not None:
            # list_url = "https://en.wikipedia.org" + list_url.find('a').get('href')
            url = urlopen(list_url)
            curr_soup = BeautifulSoup(url)
            awards_tables = curr_soup.findAll('table', class_="wikitable")
            award_count = 0
            for table in awards_tables:
                for row in table.findAll("tr"):
                    if row.find('td', class_="yes table-yes2"):
                        award_count = award_count + 1
            awards.append(award_count)
            continue
        else:
            awards_label = curr_soup.find("span", {"id": "Awards_and_nominations"})
            if not awards_label:
                awards.append('NA')
            else:
                award_count = 0
                awards_table = awards_label.findNext('table', class_='wikitable sortable')
                if not awards_table:
                    award_count = 0
                    awards_table = awards_label.findNext('table', class_='wikitable')
                if not awards_table:
                    awards.append('NA')
                    continue
                awards_table = awards_table.findAll('tr')
                for award in awards_table:
                    if award.find('td', class_="yes table-yes2"):
                        award_count = award_count + 1
                awards.append(award_count)
    return {
        'name': name,
        'birth': birth,
        'country': country,
        'awards': awards,
    }


films_info_dict = get_films_info()
df = pd.DataFrame(films_info_dict['year'], columns=['Year'])
df['Title'] = films_info_dict['title']
df['Role'] = films_info_dict['role']
df['Director'] = films_info_dict['director']

characters_pages_info = get_characters_pages(films_info_dict['url_movies'])
characters_info = get_characters_info(characters_pages_info)

df = pd.DataFrame(characters_info['name'], columns=['Name'])
df['Birth'] = characters_info['birth']
df['Country'] = characters_info['country']
df['Awards'] = characters_info['awards']
pandas.set_option('display.max_rows', df.shape[0] + 1)
print(df)

counters = []
for v in characters_pages_info['characters_dict'].values():
    counters.append(v['count'])
NumOfJointMovies = Counter(counters)
c = sorted(NumOfJointMovies.items())

objects = c
performance = [x[1] for x in c]
y_pos = np.arange(len(objects))
my_ids = [idx for idx, val in c]

plt.bar(y_pos, performance, align='center', alpha=0.5)
plt.xticks(y_pos, my_ids)
plt.xlabel('Number of Joint Movies')
plt.ylabel('Number Of Actors')
plt.title('Histogram of number of co-actors per number of joint movies')

plt.show()
