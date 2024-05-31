#!/usr/bin/env python
import requests, json
import bs4
from bs4 import BeautifulSoup, Tag
import gc
import csv
import time
import random
import os,sys, logging,pwd
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-recursive-argument
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/#the-string-argument
#   Since Beautiful Soup 4.4.0. a parameter called string does the work that text used to do in the previous versions.
#   example soup.find_all("td", string="Elsie")

# Wifi 9310130138 parmod ji security DTU AHU rack key

# pip install html5lib
# source /Users/kapil/Downloads/UnivCrawlerPython/UnivCrawlerPython/venv/bin/activate
# git config --global user.name "kapsharma1977"
# git config --global user.email kapsharma1977@gmail.com
# git config --list
# git remote -v
# git init
# git push origin main or git push -f origin main
# The CHE ranking system only applies to German universities. 
# The Center for Higher Education Development in Germany (CHE) releases both its 'Excellence Rankings' and 'Research Rankings' each year
# If you can affect your environment, you can use PYTHONOPTIMIZE=1
# find_all return Resultset which is kind of list(sublist) for soup
# fetching HTML: HTTPSConnectionPool(host='studiengaenge.zeit.de', port=443)
# Hauptunterrichtssprache: Englisch

# ps aux --sort -rss | grep python
# nohup python /home/kapilsharma/www/germanuniversities/university.py > error.log &


# https://www.hochschulkompass.de/home.html
# 'UX Design & Management', 'Hochschule Fresenius']

LOWER_BOUND_RAND = 1
UPPER_BOUND_RAND = 3
TEXT_SEPARATOR = '|'
TEXT_SECTION_SEPARATOR = '||'
RANK_LOWERBOUND = 0
RANK_UPPERBOUND = 1000
UNIV_DIR = 'univdir'
UNIVCORS_SAVE_TO_FILE_AND_REMOVE_FROM_LIST = True
#UNIVLIST = [] # List all University in CHE seedurl
CHE = {'seedurl' : 'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true&page='
           ,'MAX_PAGES' : 20
           ,'seedurlforcourse' : 'https://studiengaenge.zeit.de/studienangebote?hsid='
           ,'MAX_COURSE_PAGES' : 20}
ENABLE_PRINTS = False
ENABLE_SLEEP = True
def fetch_html(url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Error while fetching HTML: {e}")
            #print(f"Error while fetching HTML: {e}")
            return None

class wikiGermany:
    def __init__(self):
        self.wikiurl = 'https://en.wikipedia.org'
        #self.url = "https://en.wikipedia.org/wiki/List_of_universities_in_Germany"
        self.seedurl = self.wikiurl + "/wiki/List_of_universities_in_Germany"
        self.universities_names = []
        self.universities = [] # list of dict {'Name' : univ_name,'Type': univ_type,'url': univ_url}
        # field names
        self.fields = ['Name','Type','url']
        # name of csv file
        self.csvfilename = "WikiGermanUniversities.csv"
        self.htmlfilename = "WikiGermanUniversities.html"
        #self.html = self.fetch_html(self.seedurl)
        #self.find_universities_in_germany()
        self.find_universities_names_only_in_germany()
        self.find_universities_in_germany()
        self.output_csv()
        self.output_html()

    def fetch_html(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error while fetching HTML: {e}")
            return None

    def find_universities_names_only_in_germany(self):
        html = self.fetch_html(self.seedurl)

        if html:
            soup = BeautifulSoup(html, "html.parser")
            for h3 in soup.find_all('h3'):
                for span in h3.find_all('span', {'id' : ['A–D', 'E–H','I–N','O–Z']}):
                    #print(span.text)
                    ul = h3.find_next_sibling('ul')
                    #print(ul)
                    for il in ul.find_all('li'):
                        self.universities_names.append(il.a.get('title'))
                    del ul
            del html
            gc.collect()
            return self.universities_names

    def find_universities_in_germany(self):
        html = self.fetch_html(self.seedurl)

        if not html:
            return []
        soup = BeautifulSoup(html, "html.parser")
        ######################################################################
        # allul = soup.find_all(lambda tag: tag.name == 'ul' and not tag.attrs)
        # for ul in allul:
        #     for il in ul.find_all(lambda tag: tag.name == 'li' and not tag.attrs):
        #         if il.a is not None:
        #             universities.append(il.a.get('title'))
        #             #print(type(il)) # <class 'bs4.element.Tag'>
        #             #print(il.name)
        #             #print(il.attrs)
        #             print(il.string)
        #         else:
        #             pass
        #     print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
        ##################################################################
        for h3 in soup.find_all('h3'):
            for span in h3.find_all('span', {'id' : ['A–D', 'E–H','I–N','O–Z']}):
            #for span in h3.find_all('span', {'id' : ['A–D']}):
                print(span.text)
                ul = h3.find_next_sibling('ul')
                #print(ul)
                for index, il in enumerate(ul.find_all('li'),1):
                    print(f"{index}.{il.a['title']} . {self.wikiurl + il.a['href']}")
                    individual_university_wiki_data = self.individual_university_wiki_page_fetch_url(il.a.get('title'),self.wikiurl + il.a['href'])
                    self.universities.append(individual_university_wiki_data)
                    #universities.append(il.a.get('title'))
                #del individual_university_wiki_page
                #del ul
        del html
        del soup
        gc.collect()

        # for h3 in soup.find_all('h3'):
        #     for i,span in enumerate(h3.find_all('span', {'id' : ['A–D', 'E–H','I–N','O–Z']})):
        #         print('span {} == > {}'.format(i,span.text))
        return self.universities
    def individual_university_wiki_page_fetch_url(self,nameuniv, iuwp_url):
        univ_name = nameuniv
        univ_type = None
        univ_url = iuwp_url
        
        # Fetch Wiki Page 
        individual_university_wiki_page_html = self.fetch_html(iuwp_url)
        # if Wiki Page is not found
        if not individual_university_wiki_page_html:
            return {'Name': univ_name
                    ,'Type': univ_type
                    ,'url': univ_url
                    }
        soup = BeautifulSoup(individual_university_wiki_page_html, "html.parser")
        table = soup.find("table",{'class' : 'infobox vcard'})
        
        # if no table is found
        if not table:
            return {'Name': nameuniv
                    ,'Type': univ_type
                    ,'url': univ_url
                    }
        else:
            #print(table)
            caption = table.find('caption')
            #print(caption.text)
            if caption:
                if caption.text:
                    univ_name = caption.text
            rows = table.find_all('tr')
            #print(rows)
            for row in rows:
                #print(row)
                th = row.find('th')
                if th:
                    #print(th)
                    #print(th.text)
                    if th.text == 'Type':
                        td = row.find('td')
                        if td:
                            #print(th.text + ' ' + td.text)
                            univ_type = td.text
                    if th.text == 'Website':
                        td = row.find('td')
                        if td:
                            #print(th.text + ' ' + td.a['href'])
                            univ_url = td.a['href']
            #print(univ_name + ',' + univ_type + ',' + univ_url)
            #return univ_name + ',' + univ_type + ',' + univ_url
            del individual_university_wiki_page_html
            del soup
            gc.collect()
            return {'Name': univ_name
                    ,'Type': univ_type
                    ,'url': univ_url
                    }
    
    def output_csv(self):
        # writing to csv file
        with open(self.csvfilename, 'w+') as csvfile:
            # creating a csv dict writer object
            writer = csv.DictWriter(csvfile, fieldnames = self.fields)
            # writing headers (field names)
            writer.writeheader()
            # writing data rows
            #print(self.universities)
            writer.writerows(self.universities)
    
    def output_html(self):
        with open(self.htmlfilename, 'w+') as f:
            f.writelines('<!DOCTYPE html>\n')
            f.writelines('<html>\n')
            f.writelines('\t<head>\n')
            f.writelines('\t\t<title>Total German Universities</title>\n')
            f.writelines('\t\t<meta charset="utf-8">\n')
            f.writelines('\t\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            f.writelines('\t\t<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">\n')
            # f.writelines('\t\t<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>\n')
            # f.writelines('\t\t<link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/dataTables.bootstrap4.min.css">\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/dataTables.bootstrap4.min.js"></script>\n')
            f.writelines('\t</head>\n')
            f.writelines('<body>\n')
            f.writelines('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>\n')
            f.writelines('<div class="container-fluid">\n')
            f.writelines('<H1>' + 'Total German Universities ' + str(len(self.universities_names))  + '</H1>\n')
            f.writelines('<br>\n')
            f.writelines('<table class="table table-striped table-sm">\n') #table-condensed
            f.writelines('\t<tr>\n')
            f.writelines('\t\t<th>Serial Number</th>\n')
            f.writelines('\t\t<th>German Universities Names</th>\n')
            f.writelines('\t</tr>\n')
            for index, name in enumerate(self.universities_names, 1):
                f.writelines('\t<tr>\n')
                f.writelines('\t\t<td>' + str(index) + '</td>\n')
                f.writelines('\t\t<td>' + name + '</td>\n')
                f.writelines('\t</tr>\n')
            f.writelines('</table>\n')
            f.writelines('<br>\n')
            f.writelines('<H1>' + 'Total German Universities Links and Type' + str(len(self.universities_names))  + '</H1>\n')
            # f.writelines('<table class="table table-hover table-condensed" id="sortTable">\n')
            f.writelines('<table class="table table-hover table-sm">\n')
            f.writelines('\t<thead>\n')
            f.writelines('\t<tr>\n')
            f.writelines('\t\t<th>Serial Number</th>\n')
            f.writelines('\t\t<th>Type</th>\n')
            f.writelines('\t\t<th>German Universities Names With Links</th>\n')
            f.writelines('\t</tr>\n')
            f.writelines('\t</thead>\n')
            f.writelines('\t<tbody>\n')
            for index, name in enumerate(self.universities, 0):
                f.writelines('\t<tr>\n')
                f.writelines('\t\t<td>' + str(index + 1) + '</td>\n')
                if name['Type']:
                    f.writelines('\t\t<td>' + name['Type'] + '</td>\n')
                else:
                    f.writelines('\t\t<td>' + ' ' + '</td>\n')
                if name['Name']:
                    if name['url']:
                        f.writelines('\t\t<td>' + '<a href = \'' + name['url'] + '\'>' + name['Name'] + '</a>' + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + name['Name'] + '</td>\n')
                else:
                    if name['url']:
                        f.writelines('\t\t<td>' + '<a href = \'' + name['url'] + '\'>' + name['url'] + '</a>' + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                f.writelines('\t</tr>\n')
            f.writelines('\t</tbody>\n')
            f.writelines('</table>\n')
            f.writelines('</div>\n')
            # f.writelines('<script>\n')
            # f.writelines('\t$(\'#sortTable\').DataTable();\n')
            # f.writelines('</script>\n')
            f.writelines('</body>\n')
            f.writelines('</html>')

class Course:
    # index is dict key as primary key for indexing
    # index = rank + course name
    def __init__(self, perticuler_course_page_che_url:str=None, name:str=None, url:str=None, minidetails:str=None, Hauptunterrichtssprache:str=None, address:str=None, details_url:str=None, email:str= None, university:str= None, facts:str= None, QA=[], detail:str= None, overview:str= None, Wintersemester=[], Sommersemester=[]):
        self.course = {'name' : name, 'url' : url, 'minidetails' : minidetails, 'Hauptunterrichtssprache' : Hauptunterrichtssprache # main language of instruction/Hauptunterrichtssprache:Deutsch
                       , 'details' : {'facts' : facts, 'university' : university, 'overview' : overview, 'address' : address ,'url' : details_url, 'email' : email, 'QA' : QA, 'detail' : detail  # #QA = [{'Question' : None, 'Answer' : None}]
                            , 'session' : {'Wintersemester' : Wintersemester, 'Sommersemester' : Sommersemester}
                            }
                       }
        
        if perticuler_course_page_che_url:
            self.course_details_from_course_page_of_particular_university_on_che_site(perticuler_course_page_che_url)
    
    def setCourse(self,new_course):
        if new_course:
            self.course = new_course
            return self
    def course_details_from_course_page_of_particular_university_on_che_site(self,perticuler_course_page_che_url:str):
        # {'Abschluss' : 'Master of Science', 'Sachgebiet(e)': 'Umweltwissenschaft','Hauptunterrichtssprache' : 'Deutsch', 'Studienform(en)' : 'Vollzeitstudium', 'Standort(e)' : 'Karlsruhe'}
        # {'Degree' : 'Master of Arts', 'Subject(s)': 'Intercultural studies','Standard period of study' : '4 semesters', 'Main language of instruction' : 'German', 'Form(s) of study': 'Full-time study'}
        # University location, Further information / services => Hochschulstandort, Weitere Informationen / Services
        # Without admission restriction, With local admission restrictions, International students from countries that are not members of the EU:
        # time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        # course_details('https://studiengaenge.zeit.de/studiengang/w65647/data-science-4')
        #course_details = dict()
        if ENABLE_SLEEP:
            time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        html = fetch_html(perticuler_course_page_che_url)
        if not html:
            return None
        soup = BeautifulSoup(html,"html.parser")
        
        ######################### Course name #######################
        h1 = soup.find('h1',attrs={ 'itemprop' : lambda itpr: itpr is not None and 'name' in itpr})
        if h1:
            self.course['name'] = h1.get_text('',strip=True)
        else:
            self.course['name'] = 'No Name Found'
            #h1.contents
        
        ######################### Course CHE url #######################
        self.course['url'] = perticuler_course_page_che_url

        ###################### Course facts ##################
        # h1.find_next().get_text(TEXT_SEPARATOR,strip=True)
        next_div_after_h1 = h1.find_next()
        self.course['details']['facts'] = next_div_after_h1.get_text(TEXT_SEPARATOR,strip=True)
        self.course['details']['university'] = next_div_after_h1.find(itemprop="provider").get_text(TEXT_SEPARATOR,strip=True)
        # print(f"Facts : {self.course['details']['facts']}")
        # print(f"University : {self.course['details']['university']}")
        # input('facts')
        
        ###################### Course reiter-uebersicht(overview) ##################
        # itemprop="description"
        #self.course['details']['overview'] = soup.find('ul',itemprop="description").get_text(TEXT_SEPARATOR,strip=True)
        ul_pageelement = soup.find('ul',itemprop="description")
        for li in ul_pageelement.find_all('li'):
            #str_split = li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[0].strip() + ':' + li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[1].strip()
            try:
                if 'li' in li.name:
                    if self.course['details']['overview'] is not None:
                        self.course['details']['overview'] = self.course['details']['overview'] + '|' + li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[0].strip() + ':' + li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[1].strip()
                    else:
                        self.course['details']['overview'] = li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[0].strip() + ':' + li.get_text(TEXT_SEPARATOR,strip=True).rsplit(':')[1].strip()
            except:
                pass
            
        ########################## University Address and url  #######################
        # class="std-region std-region--s std-region[xl]--l std-region--white std-region--roundedSmall std-region[xl]--roundedMedium std-region--bordered"
        Kontakt = soup.find('div',attrs={'class' : lambda cl: cl is not None and 'std-region' in cl and 'std-region--s' in cl and 'std-region[xl]--l' in cl
                                        and 'std-region--white' in cl and 'std-region--roundedSmall' in cl and 'std-region[xl]--roundedMedium' in cl and 'std-region--bordered' in cl})
        if Kontakt and type(Kontakt) is not bs4.element.NavigableString:
            self.course['details']['address'] = Kontakt.get_text(TEXT_SEPARATOR,strip=True)
            #### url in <a> Tag
            a_resultset = Kontakt.find_all('a')
            for a in a_resultset:
                if a:
                    if 'mailto' in a['href']:
                        if self.course['details']['email']:
                            self.course['details']['email'] = self.course['details']['email'] + '|' + a['href'].rsplit(':')[1]
                        else: 
                            self.course['details']['email'] = a['href'].rsplit(':')[1]
                        #print(course_emails)
                    if 'http' in a['href']:
                        self.course['details']['url'] = a['href']
                        #print(course_url)

        # print(self.course['details']['email'])
        # print(self.course['details']['url'])
        # print(self.course['details']['address'])
        # input('Address')
        
        ############################ Hauptunterrichtssprache / main language of instruction
        # find language in minidetails and overview
        languageinminidetail = None
        languageinoverview = None
        if 'Deutsch' in self.course['minidetails']:
            languageinminidetail = True
        if 'Deutsch' in self.course['details']['overview']:
            languageinoverview = True
        if languageinminidetail or languageinoverview:
            self.course['Hauptunterrichtssprache'] = 'Deutsch'
            return self.course


        #######################################  Details Tab  
        # id="reiter-details"
        #for details_tab_div_resultset in soup.find_all('div',attrs={'id' : lambda di : di is not None and 'reiter-details' in di }):
        details_tab_div_resultset = soup.find('div',id = 'reiter-details')
        #print(type(details_tab_div_resultset))
        detail = None
        for item_resultset in details_tab_div_resultset:
            if item_resultset and type(item_resultset) is not bs4.element.NavigableString:
                tmp = item_resultset.get_text(TEXT_SEPARATOR,strip=True)
                if tmp:
                    if detail:
                        detail = detail + TEXT_SECTION_SEPARATOR + tmp
                    else:
                        detail = tmp
                #print(f"{ir} {item_resultset.get_text(TEXT_SEPARATOR,strip=True)}")
        self.course['details']['detail'] = detail


        ########################## When can I apply? (for Master's only)  #######################
        # WINTERSEMESTER  => WINTER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        # SOMMERSEMESTER  => SUMMER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        #(for Master's only) International students from countries that are not members of the EU
        # when_can_I_apply = {'WINTER SEMESTER' : {'winter': '','Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}
        #                     ,'SUMMER SEMESTER' : {'summer' : '', 'Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}}
        when_can_I_apply = {'Wintersemester' : [], 'Sommersemester' : []}
        Wintersemester = []; Sommersemester = []
        ########################################## Qustion and Answer
        # temprop="mainEntity"
        #QA = {'Question' : None, 'Answer' : None}
        allqa = []
        for mainEntity_div_resultset in soup.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'mainEntity' in itpr
                                                             , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Question' in cl
                                                             }):
            Qtext = None
            Atext = None
            for div_rs_item in mainEntity_div_resultset: # div_rs_item contains one Q and A (two entary)
                if type(div_rs_item) is not bs4.element.NavigableString:
                    if 'name' in div_rs_item['itemprop']:
                        Qtext = div_rs_item.get_text(TEXT_SEPARATOR,strip=True)
                        #print(Qtext)
                    if 'acceptedAnswer' in div_rs_item['itemprop']:
                        Atext = div_rs_item.get_text(TEXT_SEPARATOR,strip=True)
                        #print(Atext)
            allqa.append({'Question' : Qtext, 'Answer' : Atext})
            if 'Wann kann ich mich bewerben?' in Qtext:
                Wintersemester = []; Sommersemester = []
                sem = None; 
                flag_Furthercourses_of_study = None; 
                flag_Without_admission_restriction = None; 
                flag_International_students_from_countries_that_are_not_members_of_the_EU = None; flag_International_students_from_countries_that_are_not_members_of_the_EU_index = -1
                # Without admission restriction / Ohne Zulassungsbeschränkung
                # International students from countries that are not members of the EU: / International Studierende aus Staaten, die nicht Mitglied der EU sind
                if Atext is not None:
                    ans_list = Atext.rsplit('|')
                    for i, Answer in enumerate(ans_list,0):
                        #print(f"{i}.{Answer}")
                        try:
                            if 'Wintersemester' in Answer:
                                sem = 'Wintersemester'
                                flag_Furthercourses_of_study = None
                                flag_Without_admission_restriction = None
                                flag_International_students_from_countries_that_are_not_members_of_the_EU = None
                                #print(f"{i}.{ans_list[i+1]}{ans_list[i+2]}") # Lecture period: / Vorlesungszeit:01.10.2023 - 31.03.2024
                                #when_can_I_apply['Wintersemester'].append({ans_list[i+1]:ans_list[i+2]})
                                Wintersemester.append({ans_list[i+1]:ans_list[i+2]})
                            if 'Sommersemester' in Answer:
                                sem = 'Sommersemester'
                                flag_Furthercourses_of_study = None
                                flag_Without_admission_restriction = None
                                flag_International_students_from_countries_that_are_not_members_of_the_EU = None
                                #print(f"{i}.{ans_list[i+1]}{ans_list[i+2]}") # Lecture period: / Vorlesungszeit:01.10.2023 - 31.03.2024
                                #when_can_I_apply['Sommersemester'].append({ans_list[i+1]:ans_list[i+2]})
                                Sommersemester.append({ans_list[i+1]:ans_list[i+2]})
                            if 'Weiterführende Studiengänge' in Answer:
                                flag_Furthercourses_of_study = True
                            if flag_Furthercourses_of_study:
                                if 'Ohne Zulassungsbeschränkung' in Answer:
                                    flag_Without_admission_restriction = True
                                if 'International Studierende aus Staaten, die nicht Mitglied der EU sind' in Answer:
                                    flag_International_students_from_countries_that_are_not_members_of_the_EU = True
                                    flag_International_students_from_countries_that_are_not_members_of_the_EU_index = i
                            
                            if sem and sem == 'Wintersemester':
                                # Further courses of study / Weiterführende Studiengänge
                                if flag_Furthercourses_of_study and flag_Without_admission_restriction and flag_International_students_from_countries_that_are_not_members_of_the_EU :
                                    #print(f"\t\t\t\t\t{flag_International_students_from_countries_that_are_not_members_of_the_EU_index}.{ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]}{ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]}")
                                    #when_can_I_apply['Wintersemester'].append({ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]:ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]})
                                    Wintersemester.append({ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]:ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]})
                                    sem = None
                                    flag_Furthercourses_of_study = None
                                    flag_Without_admission_restriction = None
                                    flag_International_students_from_countries_that_are_not_members_of_the_EU = None
                                    flag_International_students_from_countries_that_are_not_members_of_the_EU_index = -1
                            if sem and sem == 'Sommersemester':
                                # Further courses of study / Weiterführende Studiengänge
                                if flag_Furthercourses_of_study and flag_Without_admission_restriction and flag_International_students_from_countries_that_are_not_members_of_the_EU :
                                    #print(f"\t\t\t\t\t{flag_International_students_from_countries_that_are_not_members_of_the_EU_index}.{ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]}{ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]}")
                                    #when_can_I_apply['Sommersemester'].append({ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]:ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]})
                                    Sommersemester.append({ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index]:ans_list[flag_International_students_from_countries_that_are_not_members_of_the_EU_index+1]})
                                    sem = None
                                    flag_Furthercourses_of_study = None
                                    flag_Without_admission_restriction = None
                                    flag_International_students_from_countries_that_are_not_members_of_the_EU = None
                        except:
                            pass
                self.course['details']['session']['Wintersemester'] = Wintersemester
                self.course['details']['session']['Sommersemester'] = Sommersemester
    
                #input('Wann kann ich mich bewerben?')
            # print(f"'Question' : {Qtext}")
            # Atext = Atext.replace('\n',' ')
            # print(f"'Answer' : {Atext}")
            # input('QA')
        #print(when_can_I_apply)
        self.course['details']['QA'] = allqa
        #######################################  deadlines and dates for your application
        
        
        
            #print(self.course['details']['detail'])
            #input('details_tab_div_resultset')
        # print('Course Details............')
        # print(perticuler_course_page_che_url)
        # print(course_details)
        # print('\n')  
        #print(self.course)  
        #input('print self.course')        
        return self.course
    def fienamewithfolder(self, id_rank:int):
        if not os.path.isdir(UNIV_DIR):
            os.mkdir(UNIV_DIR)
        if self.course['name'] and id_rank > 0:
            return UNIV_DIR + '/' + str(id_rank) + '-' + self.course['name'].replace(' ','_') + '.json'
        else:
            None
    def savecourse(self, id_rank:int):
        filename = self.fienamewithfolder(id_rank=id_rank)
        try:
            if filename:
                with open(filename,'w') as fp:
                    json.dump(self.course, fp)
        except:
            pass
    def loadcourse(self, id_rank:int):
        filename = self.fienamewithfolder(id_rank=id_rank)
        try:
            if filename:
                with open(filename,'r') as fp:
                    self.course = json.load(fp)
        except:
            pass
    def printcourse(self,t:str):
        print(f"{t}Course Name  : {self.course['name']} CHE Url : {self.course['url']} University Url : {self.course['details']['url']}")
        print(f"{t}Hauptunterrichtssprache  : {self.course['Hauptunterrichtssprache']}")
        print(f"{t}Minidetails  : {self.course['minidetails']}")
        print(f"{t}Course Facts : {self.course['details']['facts']}")
        print(f"{t}University   : {self.course['details']['university']}")
        print(f"{t}Overview     : {self.course['details']['overview']}")
        print(f"{t}Address      : {self.course['details']['address']}")
        if self.course['details']['email']:
            print(f"{t}Email        : {self.course['details']['email']}")
        print(f"{t}Wintersemester: {self.course['details']['session']['Wintersemester']}")
        print(f"{t}Sommersemester: {self.course['details']['session']['Sommersemester']}")
        # for aq in self.course['details']['QA']: # #QA = [{'Question' : None, 'Answer' : None}]
        #     if 'Wann kann ich mich bewerben?' in aq['Question']:
        #         print(aq['Answer'])
        print('\n')

class University:
    UNIVLIST = [] # list of all universities for CHE site
    htmlfilename = UNIV_DIR + '/' + 'CHEUniversities.html'
    def __init__(self, from_a_tag_of_div_std_profileListItemWrapper=None, id:int=0, people:str=None, location:str=None, keystrengths:str=None, name:str=None, cheurl:str=None):
        self.cheuniversity = { 'id' : id  # id is CHE Rank
                          ,'people' : people
                          , 'location' : location
                          , 'keystrengths' : keystrengths
                          , 'name' : name
                          , 'cheurl' : cheurl
                          }
        if from_a_tag_of_div_std_profileListItemWrapper and id==0:
            self.extractUniversity(from_a_tag_of_div_std_profileListItemWrapper)
    def extractUniversity(self,from_a_tag_of_div_std_profileListItemWrapper):
        try:
            # ############################################# CHE url    #######################
            if str(from_a_tag_of_div_std_profileListItemWrapper['href']):
                self.cheuniversity['cheurl'] = from_a_tag_of_div_std_profileListItemWrapper['href']
            else:
                self.cheuniversity['cheurl'] = None
            #self.cheuniversity['cheurl'] = str(from_a_tag_of_div_std_profileListItemWrapper['href'])
            #print(a['href'])
            
            ################################################## Name   ########################
            self.cheuniversity['name'] = str(from_a_tag_of_div_std_profileListItemWrapper.find('div',attrs={'class' : lambda cl: cl is not None and 'std-headline std-headline--h6 std-headline--autoHyphens' in cl}).get_text(TEXT_SEPARATOR,strip=True))
            #print(a.find('div',attrs={'class' : lambda cl: cl is not None and 'std-headline std-headline--h6 std-headline--autoHyphens' in cl}).get_text(TEXT_SEPARATOR,strip=True)) # find all <div> child)
            
            ################################################## Rank   #########################
            for che_rank in from_a_tag_of_div_std_profileListItemWrapper['href'].rsplit('/'):
                #print(che_rank)
                if che_rank.isnumeric():
                    self.cheuniversity['id'] = int(che_rank)
                    #print(che_rank)
            if not self.cheuniversity['id']:
                self.cheuniversity['id'] = 0
            #print(a)
            
            ################################## Mini details about University #######################
            for metaItems in from_a_tag_of_div_std_profileListItemWrapper.find_all(attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__metaItems' in cl}):
                for metaItem in metaItems.find_all(attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__metaItem' in cl}):
                    for use in metaItem.find_all('use'):
                        # Number of Students/people
                        if '#people' in str(use['xlink:href']):
                            if self.cheuniversity['people']:
                                self.cheuniversity['people'] = str(self.cheuniversity['people']) + '|' + metaItem.get_text(TEXT_SEPARATOR,strip=True)
                            else:
                                self.cheuniversity['people'] = metaItem.get_text(TEXT_SEPARATOR,strip=True)
                            #print(metaItem.get_text(TEXT_SEPARATOR,strip=True))
                        # Location of University
                        if '#location' in str(use['xlink:href']):
                            if self.cheuniversity['location']:
                                self.cheuniversity['location'] = self.cheuniversity['location'] + '|' + metaItem.get_text(TEXT_SEPARATOR,strip=True)
                            else:
                                self.cheuniversity['location'] = metaItem.get_text(TEXT_SEPARATOR,strip=True)
                            #print(metaItem.get_text(TEXT_SEPARATOR,strip=True))
                    # University key Strengths
                    for use in metaItem.find_all('span'): # University Strength
                        if self.cheuniversity['keystrengths']:
                            self.cheuniversity['keystrengths'] = self.cheuniversity['keystrengths'] + '|' + metaItem.get_text(TEXT_SEPARATOR,strip=True)
                        else:
                            self.cheuniversity['keystrengths'] = metaItem.get_text(TEXT_SEPARATOR,strip=True)
                        #print(metaItem.get_text(TEXT_SEPARATOR,strip=True))
        except:
            pass
    def setUniversity(self,cheuniversity):
        if cheuniversity:
            self.cheuniversity = cheuniversity
        return self
    def __resetcheuniversity__(self):
        self.cheuniversity['id'] = 0
        self.cheuniversity['people'] = None
        self.cheuniversity['location'] = None
        self.cheuniversity['keystrengths'] = None
        self.cheuniversity['name'] = None
        self.cheuniversity['cheurl'] = None
    def getCHEurl(self):
        if self.cheuniversity['cheurl']:
            return self.cheuniversity['cheurl']
        else:
            None
    def getCHErank(self):
        if int(self.cheuniversity['id']) > 0 :
            return int(self.cheuniversity['id'])
        else:
            int(0)
    def printUniversity(self):
        print('***********************************************************************')
        print(f"University Name     : {self.cheuniversity['name']}")
        print(f"\tRecord id         : {self.cheuniversity['id']}")
        print(f"\tCHE url           : {self.cheuniversity['cheurl']}")
        print(f"\tPeople            : {self.cheuniversity['people']}")
        print(f"\tLocation          : {self.cheuniversity['location']}")
        print(f"\tKey Strengths     : {self.cheuniversity['keystrengths']}")
    @classmethod
    def fienamewithfolder(cls):
        if not os.path.isdir(UNIV_DIR):
            os.mkdir(UNIV_DIR)
        else:
            return UNIV_DIR + '/' + 'cheuniversities' + ".json"
    @classmethod
    def saveuniversities(cls):
        # check universities list or not
        if len(cls.UNIVLIST) > 0:
            with open(cls.fienamewithfolder(),'w') as fp:
                json.dump(cls.UNIVLIST, fp) # {'id': id_rank, 'university' : uc['university'], 'courses' : uc['courses']}
    @classmethod
    def loaduniversities(cls):
        # check university with courses is in list or not
        if len(cls.UNIVLIST) <= 0:
            with open(cls.fienamewithfolder(),'r') as fp:
                cls.UNIVLIST = json.load(fp)
            if len(cls.UNIVLIST) > 0:
                return True
            else:
                return False
    @classmethod
    def find_universities_che_pages_url(cls): # store in class variable University.UNIVLIST.append(self.cheuniversity)
        page_counter = 1
        while(page_counter < CHE['MAX_PAGES']):# HTML Pages having Universities / Colleges
            if ENABLE_PRINTS:
                print(CHE['seedurl'] + str(page_counter))
            if page_counter != 1 and ENABLE_SLEEP:
                time.sleep(random.randint(LOWER_BOUND_RAND, UPPER_BOUND_RAND))
            html = fetch_html(CHE['seedurl'] + str(page_counter)) # A Page with <a> tags lnks of Universities / Colleges
            if not html:
                pass # return []
            soup = BeautifulSoup(html, "html.parser")
            try :
                div_std_profileList = soup.find('div', attrs={'class' : lambda cl: cl is not None and  cl == 'std-profileList'})
                # print(div_std_profileList)
                # input('std-profileList')
                
                ############################## loop for all University in <a>. div_std_profileListItemWrapper is a pageelement for one university among set div_std_profileList
                for div_std_profileListItemWrapper in div_std_profileList.find_all('div', attrs={'class' : lambda cl: cl is not None and 'std-profileListItemWrapper' in cl}):
                    #print(div_std_profileListItemWrapper)
                    #input('div_std_profileListItemWrapper')
                    try:
                        a = div_std_profileListItemWrapper.find('a',attrs={'href' : lambda tg: tg is not None and 'https://studiengaenge.zeit.de' in tg
                                                        , 'class' : lambda cl: cl is not None and 'std-region--clickable' in cl and 'std-profileListItem' in cl
                                                        , 'data-wt-click' : lambda dct: dct is not None})
                        #
                        u = University(from_a_tag_of_div_std_profileListItemWrapper=a)
                        if u.getCHErank() != 0:
                            cls.UNIVLIST.append(u.cheuniversity)
                            if ENABLE_PRINTS:
                                u.printUniversity()
                    except :
                        pass
            except :
                pass
                #print('No Resultset found in soup')
            page_counter = page_counter + 1
            del html
            del soup
            gc.collect()
    @classmethod
    def output_html(cls):
        if len(cls.UNIVLIST) <= 0:
            return None
        with open(cls.htmlfilename, 'w') as f:
            f.writelines('<!DOCTYPE html>\n')
            f.writelines('<html>\n')
            f.writelines('\t<head>\n')
            f.writelines('\t\t<title>Total German CHE Universities</title>\n')
            f.writelines('\t\t<meta charset="utf-8">\n')
            f.writelines('\t\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            f.writelines('\t\t<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">\n')
            # f.writelines('\t\t<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>\n')
            # f.writelines('\t\t<link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/dataTables.bootstrap4.min.css">\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/dataTables.bootstrap4.min.js"></script>\n')
            f.writelines('\t</head>\n')
            f.writelines('<body>\n')
            f.writelines('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>\n')
            f.writelines('<div class="container-fluid">\n')
            f.writelines('<H1>' + 'Total German Universities(CHE) ' + str(len(cls.UNIVLIST))  + '</H1>\n')
            f.writelines('<br>\n')
            f.writelines('<table class="table table-striped table-sm">\n') #table-condensed
            f.writelines('\t<tr>\n')
            f.writelines('\t\t<th>Serial Number</th>\n')
            f.writelines('\t\t<th>CHE Rank</th>\n')
            f.writelines('\t\t<th>German CHE Universities Names</th>\n')
            f.writelines('\t\t<th>location</th>\n')
            f.writelines('\t\t<th>Other Info</th>\n')
            f.writelines('\t</tr>\n')
            for index, univ in enumerate(cls.UNIVLIST, 1):
                if univ['name'] and univ['id'] != 0:
                    f.writelines('\t<tr>\n')
                    f.writelines('\t\t<td>' + str(index) + '</td>\n')
                    f.writelines('\t\t<td>' + str(univ['id']) + '</td>\n')
                    f.writelines('\t\t<td>' + '<a href="' + univ['cheurl'] + '">' + univ['name'] + '</a>' + '</td>\n')
                    if univ['location']:
                        f.writelines('\t\t<td>' + univ['location'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if univ['keystrengths']:
                        f.writelines('\t\t<td>' + univ['keystrengths'] + "," + univ['people'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    f.writelines('\t</tr>\n')
            f.writelines('</table>\n')
            f.writelines('</div>\n')
            # f.writelines('<script>\n')
            # f.writelines('\t$(\'#sortTable\').DataTable();\n')
            # f.writelines('</script>\n')
            f.writelines('</body>\n')
            f.writelines('</html>')
class UniversityCourses:
    # id is dict key as primary key for indexing
    # id = rank + course name
    def __init__(self, rank=0) -> None:
        #self.univcourses = {'rank' : rank, 'courses' : courses}
        if rank < int(RANK_LOWERBOUND) or rank > int(RANK_UPPERBOUND):
            rank = 0
        self.unicors = [] # {'id' : 0, 'university' : None, 'courses' : []}

        self.univlist = [] # list of university member cheuniversity dict 
    
    def setUniversityCourses(self, new_unicors):
        if new_unicors:
            self.unicors = new_unicors
    def Universityinlist(self, id_rank:int):
        for uc in self.unicors:
            if int(uc['id']) == id_rank:
                return uc
        else:
            return None
    def find_universities_che_pages_url(self): #step 1
        # if not University.loaduniversities():
        #     University.find_universities_che_pages_url()
        #     University.saveuniversities()
        # for univ in University.UNIVLIST:
        #     u = University().setUniversity(univ)
        page_counter = 1
        while(page_counter < CHE['MAX_PAGES']):# HTML Pages having Universities / Colleges
            if ENABLE_PRINTS:
                print(CHE['seedurl'] + str(page_counter))
            if ENABLE_SLEEP:
                time.sleep(random.randint(LOWER_BOUND_RAND, UPPER_BOUND_RAND))
            html = fetch_html(CHE['seedurl'] + str(page_counter)) # A Page with <a> tags lnks of Universities / Colleges
            if not html:
                pass # return []
            soup = BeautifulSoup(html, "html.parser")
            try :
                div_std_profileList = soup.find('div', attrs={'class' : lambda cl: cl is not None and  cl == 'std-profileList'})
                # print(div_std_profileList)
                # input('std-profileList')
                
                ############################## loop for all University in <a>. div_std_profileListItemWrapper is a pageelement for one university among set div_std_profileList
                for div_std_profileListItemWrapper in div_std_profileList.find_all('div', attrs={'class' : lambda cl: cl is not None and 'std-profileListItemWrapper' in cl}):
                    #print(div_std_profileListItemWrapper)
                    #input('div_std_profileListItemWrapper')
                    try:
                        a = div_std_profileListItemWrapper.find('a',attrs={'href' : lambda tg: tg is not None and 'https://studiengaenge.zeit.de' in tg
                                                        , 'class' : lambda cl: cl is not None and 'std-region--clickable' in cl and 'std-profileListItem' in cl
                                                        , 'data-wt-click' : lambda dct: dct is not None})
                        u = University(from_a_tag_of_div_std_profileListItemWrapper=a) # Step 2 Find University from website page
                        # u.extractUniversity(a)
                        if ENABLE_PRINTS:
                            u.printUniversity()
                        self.univlist.append(u.cheuniversity)
                        ############# Check University in Local filesystem
                        ## if found on local file system then load it form there else find university coureses from remote site and save to local file system
                        ## to force system to find university coureses from remote site and save to local file system "delete files from local system"
                        # if not self.loaduniversitycourses(u.getCHErank()): 
                        #     self.find_courses_from_university_page_on_che_site(partial_seed_url_of_university_page_on_che_site=CHE['seedurlforcourse'],university=u,course_Master_Bachelor_All='master')
                        #     self.saveuniversitycourses(id_rank=u.getCHErank())
                        #input('saveuniversitycourses')
                        #print(self.unicors)
                        
                    except :
                        pass
            except :
                pass
                #print('No Resultset found in soup')
            page_counter = page_counter + 1
            del html
            del soup
            gc.collect()
    def univlist_fienamewithfolder(cls):
        if not os.path.isdir(UNIV_DIR):
            os.mkdir(UNIV_DIR)
        else:
            return UNIV_DIR + '/' + 'cheuniversities' + '.json'
    def univlist_saveuniversities(self):
        # check universities list or not
        if len(self.univlist) > 0:
            with open(self.univlist_fienamewithfolder(),'w') as fp:
                json.dump(self.univlist, fp) # {'id': id_rank, 'university' : uc['university'], 'courses' : uc['courses']}
    def univlist_loaduniversities(self):
        # check university with courses is in list or not
        if len(self.univlist) <= 0:
            filenamewithpath = str(self.univlist_fienamewithfolder())
            if os.path.isfile(filenamewithpath):
                with open(filenamewithpath,'r') as fp:
                    self.univlist = json.load(fp)
            if len(self.univlist) > 0:
                return True
            else:
                return False
    
    ## to force system to find university coureses from remote site and save to local file system "delete files from local system"
    def find_universities_che_pages_url_old(self): #step 1
        # if not University.loaduniversities():
        #     University.find_universities_che_pages_url()
        #     University.saveuniversities()
        # for univ in University.UNIVLIST:
        #     u = University().setUniversity(univ)
        page_counter = 1
        while(page_counter < CHE['MAX_PAGES']):# HTML Pages having Universities / Colleges
            if ENABLE_PRINTS:
                print(CHE['seedurl'] + str(page_counter))
            if ENABLE_SLEEP:
                time.sleep(random.randint(LOWER_BOUND_RAND, UPPER_BOUND_RAND))
            html = fetch_html(CHE['seedurl'] + str(page_counter)) # A Page with <a> tags lnks of Universities / Colleges
            if not html:
                pass # return []
            soup = BeautifulSoup(html, "html.parser")
            try :
                div_std_profileList = soup.find('div', attrs={'class' : lambda cl: cl is not None and  cl == 'std-profileList'})
                # print(div_std_profileList)
                # input('std-profileList')
                
                ############################## loop for all University in <a>. div_std_profileListItemWrapper is a pageelement for one university among set div_std_profileList
                for div_std_profileListItemWrapper in div_std_profileList.find_all('div', attrs={'class' : lambda cl: cl is not None and 'std-profileListItemWrapper' in cl}):
                    #print(div_std_profileListItemWrapper)
                    #input('div_std_profileListItemWrapper')
                    try:
                        a = div_std_profileListItemWrapper.find('a',attrs={'href' : lambda tg: tg is not None and 'https://studiengaenge.zeit.de' in tg
                                                        , 'class' : lambda cl: cl is not None and 'std-region--clickable' in cl and 'std-profileListItem' in cl
                                                        , 'data-wt-click' : lambda dct: dct is not None})
                        u = University(from_a_tag_of_div_std_profileListItemWrapper=a) # Step 2 Find University from website page
                        # u.extractUniversity(a)
                        if ENABLE_PRINTS:
                            u.printUniversity()
                        ############# Check University in Local filesystem
                        ## if found on local file system then load it form there else find university coureses from remote site and save to local file system
                        ## to force system to find university coureses from remote site and save to local file system "delete files from local system"
                        if not self.loaduniversitycourses(u.getCHErank()): 
                            self.find_courses_from_university_page_on_che_site(partial_seed_url_of_university_page_on_che_site=CHE['seedurlforcourse'],university=u,course_Master_Bachelor_All='master')
                            self.saveuniversitycourses(id_rank=u.getCHErank())
                        #input('saveuniversitycourses')
                        #print(self.unicors)
                        
                    except :
                        pass
            except :
                pass
                #print('No Resultset found in soup')
            page_counter = page_counter + 1
            del html
            del soup
            gc.collect()
    def find_courses_from_university_page_on_che_site(self, partial_seed_url_of_university_page_on_che_site:str, university:University, course_Master_Bachelor_All:str):
        # find_courses_from_university_page_on_che_site(self, 'https://studiengaenge.zeit.de/studienangebote?hsid=', 100, 'Master')
        che_rank = university.getCHErank()
        unicor = {'id' : che_rank, 'university' : university.cheuniversity, 'courses' : []}
        #courses = []
        page = 1
        while True: ###### Loop for pages  ###########
            # University Pages(page = 1, 2.. n) containing coureses
            #url = 'https://studiengaenge.zeit.de/studienangebote?hsid=' + str(che_rank) + '&page=' + str(page)
            url = partial_seed_url_of_university_page_on_che_site + str(che_rank) + '&page=' + str(page)
            if page != 1 and ENABLE_SLEEP:
                time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
            html = fetch_html(url)
            if not html:
                break # No further course pages to look for
            if page > CHE['MAX_COURSE_PAGES']:
                break
            if ENABLE_PRINTS:
                if page == 1:
                    print(url)
                else:
                    print('\n')
                    print(url)
            
            soup = BeautifulSoup(html,"html.parser")
            
            ###### Loop for all courses on perticuler page  ###########
            for course_promo_on_page in soup.find_all('div',attrs={'class' : lambda cl: cl is not None and 'std-profileListItemWrapper' in cl}):
                course_minidetails = ''
                course_name = None
                for promo in course_promo_on_page:
                    if promo and type(promo) is not bs4.element.NavigableString:
                        if promo.name == 'a':
                            courses_university = promo.find('div', attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__subname' in cl}).get_text(TEXT_SEPARATOR,strip=True)
                            course_minidetails = promo.get_text(TEXT_SEPARATOR,strip=True)
                            course_name = promo.find('div', attrs={'class' : lambda cl: cl is not None and 'std-headline' in cl}).get_text(TEXT_SEPARATOR,strip=True) #promo.get_text(TEXT_SEPARATOR,strip=True).rsplit(TEXT_SEPARATOR)[0]
                            #print(promo.name)
                            #print(f"{course_url} {promo.get_text(TEXT_SEPARATOR,strip=True)}")
                            #print(course_name)
                            #print(course_minidetails)
                            if 'master' in course_Master_Bachelor_All:
                                if 'Master' in course_minidetails:
                                    #print(f"{course_url} {course_minidetails}")
                                    #course_tmp = Course()
                                    course_tmp = Course(perticuler_course_page_che_url=promo['href'],name=course_name,url=url,minidetails=course_minidetails)
                                    unicor['courses'].append(course_tmp.course)
                                    # if course_tmp.course['Hauptunterrichtssprache'] is None:
                                    #     unicor['courses'].append(course_tmp.course)
                                    # else:
                                    #     if 'Deutsch' not in course_tmp.course['Hauptunterrichtssprache']:
                                    #         course_id = course_tmp.course['name'].replace(' ','_')
                                    #         unicor['courses'].append(course_tmp.course)
                                    if ENABLE_PRINTS:
                                        course_tmp.printcourse('\t')
                                    #courses.append(course_tmp.course)
                                    #course_tmp.printcourse('\t')
                            else:
                                if course_Master_Bachelor_All == 'All':
                                    pass
                                if course_Master_Bachelor_All == 'Bachelor':
                                    pass
                                    # if 'Bachelor' in course_minidetails:
                                    #     pass
                        #print(promo)
                        #input('promo')
            page = page + 1
            #input('sleep')
        self.unicors.append(unicor)
        gc.collect()
    def fetch_universities_coureses(self):
    #### Find Universities using class Uiversity
        if not self.univlist_loaduniversities():
            self.find_universities_che_pages_url()
            self.univlist_saveuniversities()
            self.output_html()
        #input('univlist_saveuniversities')
        ### for university univ find courses all courses 
        for univ in self.univlist:
            u = University().setUniversity(univ)
            if ENABLE_PRINTS:
                u.printUniversity()
            ## find courses all courses for unversity
            id_rank = u.getCHErank()
            if id_rank is not None:
                if self.loaduniversitycourses(int(id_rank)) is None:
                    self.find_courses_from_university_page_on_che_site(partial_seed_url_of_university_page_on_che_site=CHE['seedurlforcourse'],university=u,course_Master_Bachelor_All='master')
                    self.saveuniversitycourses(id_rank=id_rank)
    def fienamewithfolder(self, id_rank:int):
        if not os.path.isdir(UNIV_DIR):
            os.mkdir(UNIV_DIR)
        if id_rank < int(RANK_LOWERBOUND) or id_rank > int(RANK_UPPERBOUND):
            return None
        else:
            return UNIV_DIR + '/' + str(id_rank) + '_university' + ".json"
    def saveuniversitycourses(self, id_rank:int):
        # check university with courses is in list or not
        for uc in self.unicors:
            if int(uc['id']) == id_rank:
                with open(self.fienamewithfolder(id_rank),'w') as fp:
                    json.dump(uc, fp) # {'id': id_rank, 'university' : uc['university'], 'courses' : uc['courses']}
                if UNIVCORS_SAVE_TO_FILE_AND_REMOVE_FROM_LIST:
                    self.unicors.remove(uc)
    def deleteuniversitycourses(self, id_rank:int):
        # check university with courses is in list or not
        for uc in self.unicors:
            if int(uc['id']) == id_rank:
                self.unicors.remove(uc) # {'id': id_rank, 'university' : uc['university'], 'courses' : uc['courses']}
    def loaduniversitycourses(self, id_rank:int):
        # check university with courses is in list or not
        isUniversityinlist = self.Universityinlist(id_rank=id_rank)
        if isUniversityinlist:
            return isUniversityinlist # already in list do not load return
        else:
            # check file do exist
            if os.path.isfile(self.fienamewithfolder(id_rank)):
                uc_file = None
                with open(self.fienamewithfolder(id_rank),'r') as fp:
                    uc_file = json.load(fp)
                if uc_file:
                    self.unicors.append(uc_file)
                    return uc_file
                else:
                    return None
            else:
                return None
    def output_html(self):
        if len(self.univlist) <= 0:
            return None
        filename = self.univlist_fienamewithfolder().rsplit('.')[0] + '.html'
        with open(filename, 'w') as f:
            f.writelines('<!DOCTYPE html>\n')
            f.writelines('<html>\n')
            f.writelines('\t<head>\n')
            f.writelines('\t\t<title>Total German CHE Universities</title>\n')
            f.writelines('\t\t<meta charset="utf-8">\n')
            f.writelines('\t\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            f.writelines('\t\t<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">\n')
            # f.writelines('\t\t<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>\n')
            # f.writelines('\t\t<link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/dataTables.bootstrap4.min.css">\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>\n')
            # f.writelines('\t\t<script src="https://cdn.datatables.net/1.10.22/js/dataTables.bootstrap4.min.js"></script>\n')
            f.writelines('\t</head>\n')
            f.writelines('<body>\n')
            f.writelines('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>\n')
            f.writelines('<div class="container-fluid">\n')
            f.writelines('<H1>' + 'Total German Universities(CHE) ' + str(len(self.univlist))  + '</H1>\n')
            f.writelines('<br>\n')
            f.writelines('<table class="table table-striped table-sm">\n') #table-condensed
            f.writelines('\t<tr>\n')
            f.writelines('\t\t<th>Serial Number</th>\n')
            f.writelines('\t\t<th>CHE Rank</th>\n')
            f.writelines('\t\t<th>German CHE Universities Names</th>\n')
            f.writelines('\t\t<th>location</th>\n')
            f.writelines('\t\t<th>Other Info</th>\n')
            f.writelines('\t</tr>\n')
            for index, univ in enumerate(self.univlist, 1):
                if univ['name'] and univ['id'] != 0:
                    f.writelines('\t<tr>\n')
                    f.writelines('\t\t<td>' + str(index) + '</td>\n')
                    f.writelines('\t\t<td>' + str(univ['id']) + '</td>\n')
                    f.writelines('\t\t<td>' + '<a href="' + univ['cheurl'] + '">' + univ['name'] + '</a>' + '</td>\n')
                    if univ['location']:
                        f.writelines('\t\t<td>' + univ['location'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if univ['keystrengths']:
                        f.writelines('\t\t<td>' + univ['keystrengths'] + "," + univ['people'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    f.writelines('\t</tr>\n')
            f.writelines('</table>\n')
            f.writelines('</div>\n')
            # f.writelines('<script>\n')
            # f.writelines('\t$(\'#sortTable\').DataTable();\n')
            # f.writelines('</script>\n')
            f.writelines('</body>\n')
            f.writelines('</html>')
    def printresults(self):
        for uc in self.unicors:
            print('****************************************************************\n')
            print(f"{'University Rank : '}{uc['id']}")
            University().setUniversity(uc['university']).printUniversity()
            print(f"Total Number of Master's Courses : {len(uc['courses'])}")
            for c in uc['courses']:
                Course().setCourse(c).printcourse('\t')
        gc.collect()
            #sinput('printmodule')
    



class CHERanking():
    def __init__(self):
        # find_universities_che_pages_url
        #       |
        #       |__university_details
        #                   |
        #                   |__course_of_study
        #                           |
        #                           |__Course Deitales
        #'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true'#'https://studiengaenge.zeit.de/ranking'
        ########## Seed url for all University CHE ranking list
        self.seedurl = 'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true&page=' # + '1'
        #self.seedurl = 'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true&page=1'
        #self.seedurl = 'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true&page=2'
        # ... up to 'https://studiengaenge.zeit.de/hochschulen?college-in-che-ranking=true&page=20'
        ############# Individual University Course Page on CHE ranking site 
        self.course_che_url = 'https://studiengaenge.zeit.de/studienangebote?hsid=' # + str(che_rank) + '&page=' + str(page)
        self.showmore = 'Alle Hochschulen anzeigen' # In German
        
        #https://studiengaenge.zeit.de/hochschule/267/hochschule-fuer-musik-franz-liszt-weimar
        self.MAX_COURSE_PAGES = 25
        self.seedurl_1_to_20 = []
        
        ################## Pages of CHE Ranking Site Containing Universities (url) 
        url_count_1_to_20 = 1
        while(url_count_1_to_20 <= 1):
            self.seedurl_1_to_20.append(self.seedurl + str(url_count_1_to_20))
            url_count_1_to_20 = url_count_1_to_20 + 1
        ##########################################

        ################### 

        ##################

        self.universities_che_pages_url = [] # list of dict {'cherank' : '', 'cheurl' : '', 'name' : ''}
        self.universities_names = [] # list of dict {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_url}
        self.universities = [] # list of dict {'cherank' : che_rank, 'cheurl' : che_url, 'name' : univ_name, 'url': univ_url}
        self.htmlfilename = "CHEGermanUniversities.html"
        print('Seed Urls ...............................')
        print(self.seedurl_1_to_20)
        self.find_universities_che_pages_url_1()
        # print('CHE Rank, CHE Pages Urls ...............................')
        # for index, che_page_url in enumerate(self.universities_che_pages_url,0):
        #     print(f"{index} -Rank- {che_page_url['cherank']} -CHEurl-  {che_page_url['cheurl']}")
        #     self.universities_names.append(self.university_details(self.universities_che_pages_url[index]))
        # print('CHE Rank, University Name, University Url ...............................')
        # for index, univ in enumerate(self.universities_names,0):
        #     print(f"{index} . {univ}")
        
        #self.university_details({'cherank': 100, 'cheurl':'https://studiengaenge.zeit.de/hochschule/100/fernuniversitaet-in-hagen'})
        # for tmp in self.course_of_study(101,'Master'):
        #     print(tmp)
        #univ_courses = self.course_of_study({'cherank' : 100, 'name' : 'FernUniversität in Hagen', 'url' : 'www.fernuni-hagen.de'},'Master')
        #self.universities.append(self.course_of_study_1({'cherank' : 137, 'name' : 'Pädagogische Hochschule Karlsruhe', 'url' : 'www.ph-karlsruhe.de'},'Master')) # {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_url, 'courses' : courses}
        

        self.universities.append(self.university_courses_pages_1(self.universities_che_pages_url[0],'Master'))
        for univ in self.universities:
            print(f"{univ['name']},{univ['cherank']},{univ['url']}")
            for i, course in enumerate(univ['courses'],0): #dict course {'href' : a[''href], 'details' : []} # details # {'Abschluss' : 'Master of Science', 'Sachgebiet(e)': 'Umweltwissenschaft','Hauptunterrichtssprache' : 'Deutsch', 'Studienform(en)' : 'Vollzeitstudium', 'Standort(e)' : 'Karlsruhe'}
                print(f"{i}.{univ['cherank']}.{course['details']['Abschluss']},{course['details']['Sachgebiet(e)']},{course['details']['Regelstudienzeit']},{course['details']['Hauptunterrichtssprache']},{course['details']['Studienform(en)']},{course['details']['Standort(e)']}")
                #print(f"{i}.{course['details']['address']},{course['details']['url']}")
        # self.output_html()
        
        #print(self.course_of_study({'cherank' : 137, 'name' : 'Pädagogische Hochschule Karlsruhe', 'url' : 'www.ph-karlsruhe.de'},'Master'))
        # for univ in enumerate(self.universities_names,0):
        #     self.course_of_study(univ,'Master')
        
        

    # collecet all che university pages url
    # self.universities_che_pages_url.append{'cherank' : '', 'cheurl' : ''}
    def find_universities_che_pages_url(self): 
        for url in self.seedurl_1_to_20: # HTML Pages having Universities / Colleges
            html = fetch_html(url) # A Page with <a> tags lnks of Universities / Colleges
            if not html:
                pass # return []
            soup = BeautifulSoup(html, "html.parser")
            try :
                a_tag_resultset = soup.find_all('a',{'href' : lambda tg: tg is not None and 'https://studiengaenge.zeit.de' in tg
                                                     , 'class' : lambda cl: cl is not None and 'std-region--clickable' in cl and 'std-profileListItem' in cl
                                                     , 'data-wt-click' : lambda dct: dct is not None})
                #a_tag_resultset = soup.find_all('a',{'href' : lambda tg: '/hochschule' in tg, 'class' : lambda cl: 'std-region--clickable' in cl})
                #print(f'{a_tag_resultset}')
                for atagresultset in a_tag_resultset:
                    for che_rank in atagresultset['href'].rsplit('/'):
                        #print(che_rank)
                        if che_rank.isnumeric():
                            self.universities_che_pages_url.append({'cherank' : che_rank, 'cheurl' : atagresultset['href']})
                            #print(f"{che_rank} . {atagresultset['href']}")
                    #self.universities_che_pages_url.append(atagresultset['href']) # collecet all che university pages url
                #for index, hrefs in enumerate(a_tag_resultset, 1):
                #    print(f"{index} . {atagresultset['href']}")
                del a_tag_resultset
            except :
                print('No Resultset found in soup')
            del html
            del soup
            gc.collect()
            time.sleep(random.randint(LOWER_BOUND_RAND, UPPER_BOUND_RAND))

            #with open('body.txt', 'w+') as f:
                #f.writelines(str(soup.body.find_all('a',{'class' : 'std-region--clickable'})))
                #f.writelines(str(soup.body.find_all('a',{'class' : ['td-profileListItem', 'std-region std-region--s', 'std-region--white', 'std-region--roundedMedium', 'std-region--bordered', 'std-region--clickable']})))
    
    
    # collecet all che university pages url
    # self.universities_che_pages_url.append{'cherank' : '', 'cheurl' : ''}
    def find_universities_che_pages_url_1(self): 
        #{'cherank' : '', 'cheurl' : '', 'name' : ''}
        univ_name = None
        for url in self.seedurl_1_to_20: # HTML Pages having Universities / Colleges
            html = fetch_html(url) # A Page with <a> tags lnks of Universities / Colleges
            if not html:
                pass # return []
            soup = BeautifulSoup(html, "html.parser")
            try :
                for atagresultset in soup.find_all('div', attrs={'class' : lambda cl: cl is not None and 'std-profileListItemWrapper' in cl}):
                    for div_univname in atagresultset.find_all('div',attrs={'class' : lambda cl: cl is not None and 'std-headline std-headline--h6 std-headline--autoHyphens' in cl
                                                     }): # find all <div> child
                        #print(f"${div_univname.get_text().strip()}$")
                        univ_name = div_univname.get_text().strip()
                    for a_url in atagresultset.find_all('a',attrs={'href' : lambda tg: tg is not None and 'https://studiengaenge.zeit.de' in tg
                                                     , 'class' : lambda cl: cl is not None and 'std-region--clickable' in cl and 'std-profileListItem' in cl
                                                     , 'data-wt-click' : lambda dct: dct is not None}): # first <a> child 
                        #print(a_url)
                        for che_rank in a_url['href'].rsplit('/'):
                            #print(che_rank)
                            if che_rank.isnumeric():
                                #print({'cherank' : che_rank, 'cheurl' : a_url['href'], 'name' : univ_name})
                                
                                self.universities_che_pages_url.append({'cherank' : che_rank, 'cheurl' : a_url['href'], 'name' : univ_name})
                                ##return
                                #print(f"{che_rank} . {atagresultset['href']}")
                    #self.universities_che_pages_url.append(atagresultset['href']) # collecet all che university pages url
                #for index, hrefs in enumerate(a_tag_resultset, 1):
                #    print(f"{index} . {atagresultset['href']}")
            except :
                print('No Resultset found in soup')
            del html
            del soup
            gc.collect()
            time.sleep(random.randint(LOWER_BOUND_RAND, UPPER_BOUND_RAND))

            #with open('body.txt', 'w+') as f:
                #f.writelines(str(soup.body.find_all('a',{'class' : 'std-region--clickable'})))
                #f.writelines(str(soup.body.find_all('a',{'class' : ['td-profileListItem', 'std-region std-region--s', 'std-region--white', 'std-region--roundedMedium', 'std-region--bordered', 'std-region--clickable']})))
    
    
    
    
    # Collect Uni
    def university_details(self, dict_univ_che_page_url): # dict_univ_che_page_url is dict {'cherank' : che_rank, 'cheurl' : che_url}
        cherank = dict_univ_che_page_url['cherank']
        univ_name = ''
        univ_url = ''
        html = fetch_html(dict_univ_che_page_url['cheurl'])
        if not html:
            return []
        soup = BeautifulSoup(html,"html.parser")
        
        ############ University Name ####################
        for a in soup.find_all('a',attrs={'itemprop' : lambda itp: itp is not None and "item" in itp
                                          , 'class' : lambda cl: cl is not None and 'std-breadcrumb__link' in cl
                                          , 'href' : lambda hf: not hf}): #class="std-breadcrumb__link"
            univ_name = univ_name + a.get_text().strip()
            print(univ_name)
            #print(a.get_text().strip())
        # for span in soup.find_all('span',itemprop = lambda itp: itp is not None and "name" in itp):
        #     print(span)
            #print(span.get_text())
        
        ############# University url ####################
        for a in soup.find_all('a',attrs={'data-wt-click' : lambda dwc: dwc is not None and 'zur_hochschulwebsite' in dwc
                                          , 'class' : lambda cl: cl is not None and 'td-button' in cl and 'std-button--highlight' in cl}):
            #print(a)
            #print(a['data-wt-click'])
            for url in a['data-wt-click'].split():
                print(url)
                index = url.find('www.',0)
                if index != -1:
                    univ_url = univ_url + url.replace(',','').replace('\'','')
                    print(url.replace(',','').replace('\'',''))
            
        return {'cherank' : cherank, 'name' : univ_name, 'url' : univ_url}
        
    def university_courses_pages(self, dict_univ_name, course_Master_Bachelor_All): # dict dict_univ_name {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_url}
        #course = {} #list of dict {'href' : a[''href], 'details' : []}
        ############# Course of Study ####################
        #https://studiengaenge.zeit.de/studienangebote?hsid= + str(che_rank)
        #<a class="std-button std-button--primary" href="https://studiengaenge.zeit.de/studienangebote?hsid=137&amp;page=2">Weitere 20 Laden</a>
        # Max pages to fectch / scan
        che_rank = dict_univ_name['cherank']
        univ_name = dict_univ_name['name']
        univ_url = dict_univ_name['url']
        
        courses = []

        page = 1
        while True:
            # University Pages(page = 1, 2.. n) containing coureses
            #url = 'https://studiengaenge.zeit.de/studienangebote?hsid=' + str(che_rank) + '&page=' + str(page)
            url = self.course_che_url + str(che_rank) + '&page=' + str(page)
            html = fetch_html(url)
            print(url)
            if not html:
                break #return []
            if page > self.MAX_COURSE_PAGES:
                break
            soup = BeautifulSoup(html,"html.parser")
            ###<a _ngcontent-ng-c3618484436="" class="std-profileListItem std-region std-region--s std-region--white std-region--roundedMedium std-region--bordered std-region--clickable" href="/studiengang/w43140/interkulturelle-bildung-migration-und-mehrsprachigkeit"><div _ngcontent-ng-c3618484436="" class="std-profileListItem__content"><div _ngcontent-ng-c3618484436="" class="std-profileListItem__contentTitle std-postfix std-postfix--gutters"><div _ngcontent-ng-c3618484436="" class="std-postfix__fluid"><div _ngcontent-ng-c3618484436="" class="std-profileListItem__metaItems std-row std-row--s std-row[xl]--xs"><!----><!----></div><div _ngcontent-ng-c3618484436="" class="std-headline std-headline--h6 std-headline--autoHyphens">Intercultural education, migration and multilingualism</div><div _ngcontent-ng-c3618484436="" class="std-profileListItem__subname">Karlsruhe University of Education</div></div><div _ngcontent-ng-c3618484436="" class="std-postfix__fixed"><div _ngcontent-ng-c3618484436="" class="std-profileListItem__favouriteToggle"><std-course-favourite-toggle _ngcontent-ng-c3618484436="" wtidentifier="courselist" _nghost-ng-c2471638470=""><button _ngcontent-ng-c2471638470="" type="button" class="std-clickable std-clickable--touchy"><svg _ngcontent-ng-c2471638470="" class="std-postfix__icon std-icon" data-size="undefined"><use xlink:href="#std_icons_heart-empty"></use></svg></button></std-course-favourite-toggle></div></div><!----></div><div _ngcontent-ng-c3618484436="" class="std-profileListItem__contentMeta"><!----><div _ngcontent-ng-c3618484436="" class="std-profileListItem__metaItems"><div _ngcontent-ng-c3618484436="" class="std-profileListItem__metaItem"><div _ngcontent-ng-c3618484436="" class="std-badge std-badge--blue std-badge--inverted">Master</div></div><div _ngcontent-ng-c3618484436="" class="std-profileListItem__metaItem"><div _ngcontent-ng-c3618484436="" class="std-badge std-badge--transparent"><svg _ngcontent-ng-c3618484436="" stdIcon="dot" class="std-badge__icon std-icon std-icon--small" data-size="undefined"><use xlink:href="#std_icons_dot"></use></svg>4 semesters</div></div><!----><!----><!----></div></div></div><!----></a>
            # for a in soup.find_all('a',attrs={'data-wt-click' : lambda dwc: dwc is not None and '\'studiengang_ansehen\'' in dwc
            #                                   , 'class' : lambda cl: cl is not None and 'std-profileListItem' in cl and 'std-region--clickable' in cl}):
            #     ##print(a['data-wt-click'])
            #     ##print(a['href'])
            #     print(a.get_text().replace('\n','').split())
            # perticuler course page link
            for index,a in enumerate(soup.find_all('a',attrs={'data-wt-click' : lambda dwc: dwc is not None and '\'studiengang_ansehen\'' in dwc
                                            , 'class' : lambda cl: cl is not None and 'std-profileListItem' in cl and 'std-region--clickable' in cl}),1):
                ##print(a['data-wt-click'])
                ##print(a['href'])
                course = {} #dict course {'href' : a[''href], 'details' : []}
                course_text = a.get_text().replace('\n','').split()
                if course_Master_Bachelor_All == 'All':
                    print(f"{index} .{course_text}")
                if course_Master_Bachelor_All == 'Bachelor':
                    if 'Bachelor' in course_text:
                        print(f"{index} .{course_text}")
                if course_Master_Bachelor_All == 'Master':
                    if 'Master' in course_text:
                        course['href'] = a['href']
                        course['details'] = self.course_of_study_details(a['href'])
                        #print(a.get_text().split('\n'))
                        #course.append(a['href'])
                        # if 'href' not in course:
                        #     course['href'] = a['href']

                        #i = 1
                        # for text_with_spaces in a.get_text().split('\n'):
                        #     text = text_with_spaces.strip()
                        #     if text:
                        #         course.append(text.strip())
                        #         #print(f"$\t{i} * {text.strip()}") #.strip()
                        #         #i = i  + 1
                        # #print(f"{index} . {courses}")
                        # #print(f"{index} . {a['href']}")
                        courses.append(course)
                del course
            page = page + 1
            time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        #return dict()
        return {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_url, 'courses' : courses}
        ##### Check for Weitere/More button ##############
        # page = 2
        # while True:
        #     weitere_more_button_flag = False
        #     for a in soup.find_all('a',attrs={'class' : lambda cl: cl is not None and 'std-button' in cl and 'std-button--primary' in cl}):
        #         print(a['href'])
        #         if a['href'] == 'https://studiengaenge.zeit.de/studienangebote?hsid=' + str(che_rank) + '&page=' + str(page):
        #             print(a['href'])
        #             print(a.get_text().replace('\n','').split())
        #             weitere_more_button_flag = True
        #     if weitere_more_button_flag:
        #         html = fetch_html('https://studiengaenge.zeit.de/studienangebote?hsid=' + str(che_rank)) + '&page=' + str(page)
        #         if not html:
        #             print('no html found')
        #             break #return []
        #         del soup
        #         soup = BeautifulSoup(html,"html.parser")
        #         page = page + 1
        #         print(f'page = {page}')
                
        #     else:
        #         print('weiere')
        #         break

    # {'cherank' : '', 'cheurl' : '', 'name' : ''}
    def university_courses_pages_1(self, university_che_page_url, course_Master_Bachelor_All): # dict dict_univ_name {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_url}
        
        che_rank = university_che_page_url['cherank']
        univ_name = university_che_page_url['name']
        univ_cheurl = university_che_page_url['cheurl']
        
        courses = []

        page = 1
        while True:
            # University Pages(page = 1, 2.. n) containing coureses
            #url = 'https://studiengaenge.zeit.de/studienangebote?hsid=' + str(che_rank) + '&page=' + str(page)
            url = self.course_che_url + str(che_rank) + '&page=' + str(page)
            html = fetch_html(url)
            print(url)
            if not html:
                break #return []
            if page > self.MAX_COURSE_PAGES:
                break
            soup = BeautifulSoup(html,"html.parser")

            for a in soup.find_all('a',attrs={'data-wt-click' : lambda dwc: dwc is not None and '\'studiengang_ansehen\'' in dwc
                                            , 'class' : lambda cl: cl is not None and 'std-profileListItem' in cl and 'std-region--clickable' in cl}):
                ##print(a['data-wt-click'])
                ##print(a['href'])
                course = {'minidetails' : []} #dict course {'name' : ,'href' : a[''href], 'minidetails' : []}
                ############# Course Name  ############
                for course_name_div in a.find_all('div',attrs={'class' : lambda cl: cl is not None and 'std-headline--h6 std-headline--autoHyphens' in cl}):
                    course['name'] = course_name_div.get_text().strip()
                    #print(course_name_div.get_text().strip())
                ############# University Name  ############
                # for univ_name_div in a.find_all('div',attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__subname' in cl}):
                #     univ_name = univ_name_div.get_text().strip()
                #     print(univ_name_div.get_text().strip())
                ############# Content Meta 'minidetails' ############
                for contentMeta in a.find_all(attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__contentMeta' in cl}):
                    course['minidetails'] = []
                    for metaItems in contentMeta.find_all(attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__metaItems' in cl}):
                        for metaItem in metaItems.find_all(attrs={'class' : lambda cl: cl is not None and 'std-profileListItem__metaItem' in cl}):
                            course['minidetails'].append(metaItem.get_text().strip())
                            # for use in metaItem.find_all('use'):
                            #     for key in str(use['xlink:href']).rsplit('#'):
                            #         if '/' not in key:
                            #             #print(f"{key}.{metaItem.get_text().strip()}")
                            #             if key in meta_Items.keys():
                            #                 meta_Items[key].append(metaItem.get_text().strip())
                            #             else:
                            #                 meta_Items[key] = [metaItem.get_text().strip()]        
                    #print(course['minidetails'])
                if course_Master_Bachelor_All == 'Master':
                    if 'Master' in course['minidetails']:
                        course['href'] = a['href']
                        #course['details'] = self.course_of_study_details(a['href'])
                        course['details'] = self.course_of_study_details(a['href'])
                        courses.append(course)
                        #print(course)
                if course_Master_Bachelor_All == 'All':
                    print(f"{course}")
                if course_Master_Bachelor_All == 'Bachelor':
                    if 'Bachelor' in course['minidetails']:
                        print(f"{course}")
                del course
            page = page + 1
            gc.collect()
            time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        #return dict()
        return {'cherank' : che_rank, 'name' : univ_name, 'url' : univ_cheurl, 'courses' : courses}

    def course_of_study_details(self,perticuler_course_page_che_url):
        # {'Abschluss' : 'Master of Science', 'Sachgebiet(e)': 'Umweltwissenschaft','Hauptunterrichtssprache' : 'Deutsch', 'Studienform(en)' : 'Vollzeitstudium', 'Standort(e)' : 'Karlsruhe'}
        # {'Degree' : 'Master of Arts', 'Subject(s)': 'Intercultural studies','Standard period of study' : '4 semesters', 'Main language of instruction' : 'German', 'Form(s) of study': 'Full-time study'}
        # University location, Further information / services => Hochschulstandort, Weitere Informationen / Services
        # Without admission restriction, With local admission restrictions, International students from countries that are not members of the EU:
        time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        course_details = dict()
        html = fetch_html(perticuler_course_page_che_url)
        
        if not html:
            return dict()
        soup = BeautifulSoup(html,"html.parser")
        ########################## Course Deitales  #######################
            #class="std-list std-list--bulletedS std-list--highlight"
        for ul in soup.find_all('ul',attrs={'itemprop' : lambda itpr: itpr is not None and 'description' in itpr
                                                             , 'class' : lambda cl: cl is not None and 'std-list' in cl and 'std-list--bulletedS' in cl and 'std-list--highlight' in cl}):
            #print(ul)
            for li in ul.find_all('li'):
                keyvalue = li.get_text().strip().rsplit(':')
                course_details[keyvalue[0].strip()] = keyvalue[1].replace('\n','').strip()
            
        ########################## University Address  #######################
        #<div class="std-headline std-headline--h7 std-row std-row--xs std-row[xl]--s">Hochschulstandort</div>
        address = []
        for div in soup.find_all('div'):
            if 'Hochschulstandort' == div.get_text().strip():
                for line in div.find_next_sibling('div').get_text().rsplit('\n'):
                    if line:
                        #print(f"${line.strip()}$")
                        address.append(line.strip())
        if len(address) != 0:
            course_details['address'] = address
        ########################## University url  #######################
        # <div class="std-headline std-headline--h7 std-row std-row--xs std-row[xl]--s">Weitere Informationen / Services:</div>
        for div in soup.find_all('div'):
            div_text = div.get_text().strip()
            if 'Weitere Informationen / Services:' == div_text:
                for url in div.find_next_siblings():
                    if url.a:
                        course_details['url'] = url.a['href']
                        #print(f"${url.a['href']}$")
        ########################## When can I apply? (for Master's only)  #######################
        # WINTERSEMESTER  => WINTER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        # SOMMERSEMESTER  => SUMMER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        #(for Master's only) International students from countries that are not members of the EU
        # when_can_I_apply = {'WINTER SEMESTER' : {'winter': '','Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}
        #                     ,'SUMMER SEMESTER' : {'summer' : '', 'Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}}
        when_can_I_apply = {'Wintersemester' : [], 'Sommersemester' : []}
        for mainEntity in soup.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'mainEntity' in itpr
                                                             , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Question' in cl}
                                                             ):
            for question in mainEntity.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'name' in itpr}):
                #print(question.get_text().strip())
                # Find Question 'Wann kann ich mich bewerben?' => 'When can I apply?'
                if 'Wann kann ich mich bewerben?' in question.get_text().strip():
                    print(question.get_text().strip())
                    # if Question is found then find answere
                    for ans in mainEntity.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'acceptedAnswer' in itpr
                                                             , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Answer' in cl}):
                        if isinstance(ans, Tag):
                            win_sum_key = None
                            for child in ans.descendants:
                                if isinstance(child, Tag):
                                    if child.name == 'div':
                                        if 'Wintersemester' in child.get_text().strip():
                                            print(child)
                                            win_sum_key = 'Wintersemester'

                                        if 'Sommersemester' in child.get_text().strip():
                                            print(child)
                                            win_sum_key = 'Sommersemester'
                                    if child.name == 'dl':
                                        #whencanIapply = dict()
                                        dt_key = None
                                        dd_value = None
                                        for dt_dd in child.descendants:
                                            if isinstance(dt_dd, Tag):
                                                if dt_dd.name == 'dt':
                                                    dt_key = dt_dd.get_text().strip()
                                                if dt_dd.name == 'dd':
                                                    dd_value = dt_dd.get_text().strip()
                                        if dt_key and dd_value:
                                            when_can_I_apply[win_sum_key].append({dt_key:dd_value})  #[dt_key] = dd_value
        course_details['sessions'] = when_can_I_apply
                                                        
                                        
                            # print(when_can_I_apply)
                            # input("jhfahgbakfhgabkfjbajkbaj")
    
        # print('Course Details............')
        # print(perticuler_course_page_che_url)
        # print(course_details)
        # print('\n')            
        return course_details
    
    def course_of_study_details_testing(self,perticuler_course_page_che_url):
        # {'Abschluss' : 'Master of Science', 'Sachgebiet(e)': 'Umweltwissenschaft','Hauptunterrichtssprache' : 'Deutsch', 'Studienform(en)' : 'Vollzeitstudium', 'Standort(e)' : 'Karlsruhe'}
        # {'Degree' : 'Master of Arts', 'Subject(s)': 'Intercultural studies','Standard period of study' : '4 semesters', 'Main language of instruction' : 'German', 'Form(s) of study': 'Full-time study'}
        # University location, Further information / services => Hochschulstandort, Weitere Informationen / Services
        # Without admission restriction, With local admission restrictions, International students from countries that are not members of the EU:
        
        # course_details = {}
        
        time.sleep(random.randint(LOWER_BOUND_RAND,UPPER_BOUND_RAND))
        course_details = dict()
        html = fetch_html(perticuler_course_page_che_url)
        
        if not html:
            return dict()
        soup = BeautifulSoup(html,"html.parser")
        ########################## Course Deitales  #######################
            #class="std-list std-list--bulletedS std-list--highlight"
        for ul in soup.find_all('ul',attrs={'itemprop' : lambda itpr: itpr is not None and 'description' in itpr
                                                             , 'class' : lambda cl: cl is not None and 'std-list' in cl and 'std-list--bulletedS' in cl and 'std-list--highlight' in cl}):
            #print(ul)
            for li in ul.find_all('li'):
                keyvalue = li.get_text().strip().rsplit(':')
                course_details[keyvalue[0].strip()] = keyvalue[1].replace('\n','').strip()
            
        ########################## University Address  #######################
        #<div class="std-headline std-headline--h7 std-row std-row--xs std-row[xl]--s">Hochschulstandort</div>
        address = []
        for div in soup.find_all('div'):
            if 'Hochschulstandort' == div.get_text().strip():
                for line in div.find_next_sibling('div').get_text().rsplit('\n'):
                    if line:
                        #print(f"${line.strip()}$")
                        address.append(line.strip())
        if len(address) != 0:
            course_details['address'] = address
        ########################## University url  #######################
        # <div class="std-headline std-headline--h7 std-row std-row--xs std-row[xl]--s">Weitere Informationen / Services:</div>
        for div in soup.find_all('div'):
            div_text = div.get_text().strip()
            if 'Weitere Informationen / Services:' == div_text:
                for url in div.find_next_siblings():
                    if url.a:
                        course_details['url'] = url.a['href']
                        #print(f"${url.a['href']}$")
        ########################## When can I apply? (for Master's only)  #######################
        # WINTERSEMESTER  => WINTER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        # SOMMERSEMESTER  => SUMMER SEMESTER
        #   Vorlesungszeit  => Lecture period
        #       Weiterführende Studiengänge => Further courses of study
        #           Ohne Zulassungsbeschränkung => Without admission restriction
        #               International Studierende aus Staaten, die nicht Mitglied der EU sind => International students from countries that are not members of the EU
        #(for Master's only) International students from countries that are not members of the EU
        # when_can_I_apply = {'WINTER SEMESTER' : {'winter': '','Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}
        #                     ,'SUMMER SEMESTER' : {'summer' : '', 'Lecture period' : '', 'International students from countries that are not members of the EU' : '', 'conditions' : 'Further courses of study and Without admission restriction'}}
        when_can_I_apply = {'Wintersemester' : [], 'Sommersemester' : []}
        for mainEntity in soup.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'mainEntity' in itpr
                                                             , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Question' in cl}
                                                             ):
            for question in mainEntity.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'name' in itpr}):
                #print(question.get_text().strip())
                # Find Question 'Wann kann ich mich bewerben?' => 'When can I apply?'
                if 'Wann kann ich mich bewerben?' in question.get_text().strip():
                    print(question.get_text().strip())
                    # if Question is found then find answere
                    ans_count = 0 
                    for ans in mainEntity.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'acceptedAnswer' in itpr
                                                             , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Answer' in cl}):
                        if isinstance(ans, Tag):
                            ans_count = ans_count + 1
                            print(f"{'Ans Count = '}{ans_count}")
                            child_count = 0
                            win_sum_key = None
                            for child in ans.descendants:
                                if isinstance(child, Tag):
                                    child_count = child_count + 1
                                    print(f"{'Child Count = '}{child_count}")
                                    if child.name == 'div':
                                        if 'Wintersemester' in child.get_text().strip():
                                            print(child)
                                            win_sum_key = 'Wintersemester'

                                        if 'Sommersemester' in child.get_text().strip():
                                            print(child)
                                            win_sum_key = 'Sommersemester'
                                    if child.name == 'dl':
                                        #whencanIapply = dict()
                                        dt_key = None
                                        dd_value = None
                                        for dt_dd in child.descendants:
                                            if isinstance(dt_dd, Tag):
                                                if dt_dd.name == 'dt':
                                                    dt_key = dt_dd.get_text().strip()
                                                if dt_dd.name == 'dd':
                                                    dd_value = dt_dd.get_text().strip()
                                        if dt_key and dd_value:
                                            when_can_I_apply[win_sum_key].append({dt_key:dd_value})  #[dt_key] = dd_value
                                                        
                                                    
                                        
                                        # print(f"{index}.{len(child)}.{child.name}")
                                        # print(child.getText('^',strip=True).rsplit('^'))
                                        # for tmp in child.getText('^',strip=False).rsplit('^'):
                                        #     if 'Wintersemester' in tmp or 'WINTERSEMESTER' in tmp:
                                        #         when_can_I_apply['WINTER SEMESTER']['winter'] = True
                                        #     if 'Wintersemester' in tmp or 'WINTERSEMESTER' in tmp:
                                        #         when_can_I_apply['WINTER SEMESTER']['winter'] = True
                                        # if 'Wintersemester' in child.get_text().strip():
                                        #     print(f"{index}.{len(child)}.{child.name}")
                                        #     print(f"{child}")
                            print(when_can_I_apply)
                            input("jhfahgbakfhgabkfjbajkbaj")
                    #for ans in mainEntity.find_all():
                        # if isinstance(ans, Tag):
                        #     if 'class' in ans.attrs and 'acceptedAnswer' in ans.attrs['class']:
                            
                            # for index, child in enumerate(ans.descendants,1):
                            #     print(f"{index}.{child}")
                            #     v = input('Wintersemester>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
                                # if 'Wintersemester' in child.get_text().strip():
                                #     print(f"{index}.{child.get_text().strip()}")
                                #     input('Wintersemester')
                                
                            #print(ans.get_text())
                                
                    # for index,ans in enumerate(mainEntity.find_all('div',attrs={'itemprop' : lambda itpr: itpr is not None and 'acceptedAnswer' in itpr
                    #                                          , 'itemtype' : lambda cl: cl is not None and 'https://schema.org/Answer' in cl}),1):
                    #     print(f"{index}.{ans}")
                    ############################################
                    # for index,sib_div in enumerate(question.next_siblings,1):
                    #     if isinstance(sib_div, Tag):
                    #         if 'class' in sib_div.attrs and 'acceptedAnswer' in sib_div.attrs['class']:
                    #             print(f"{index}.{sib_div}")
                    #####################################################
                    
                    # ans = question.find_next_siblings("div")
                    # for index,an in enumerate(ans,1):
                    #     print(f"{index}.{type(an)}")
                    #     # if 'WINTERSEMESTER'in ans.get_text():
                        #     print(ans.find_next_sibling('dd'))
                    input('$$$$$$$$$$$$$')
        print('Course Details............')
        print(perticuler_course_page_che_url)
        print(course_details)
        print('\n')            
        input('@@@@@@@@@@@@@@@')
        return course_details

    def output_html(self):
        with open(self.htmlfilename, 'w+') as f:
            f.writelines('<!DOCTYPE html>\n')
            f.writelines('<html>\n')
            f.writelines('\t<head>\n')
            f.writelines('\t\t<title>Total German Universities</title>\n')
            f.writelines('\t\t<meta charset="utf-8">\n')
            f.writelines('\t\t<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            #f.writelines('\t\t<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-rbsA2VBKQhggwzxH7pPCaAqO46MgnOM80zW1RWuH61DGLwZJEdK2Kadq2F9CUG65" crossorigin="anonymous">\n')
            ############# Scripts ############
            f.writelines('\t\t<script src="https://code.jquery.com/jquery-3.7.0.js"></script>\n')
            f.writelines('\t\t<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>\n')
            f.writelines('\t\t<script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>\n')
            f.writelines('\t\t<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/5.3.0/css/bootstrap.min.css">\n')
            f.writelines('\t\t<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">\n')
            f.writelines('\t\t<script>')
            f.writelines('\t\t\t$(document).ready(function() {')
            f.writelines('\t\t\t\t$("#GermanUniversities").DataTable();')
            f.writelines('\t\t\t});')
            f.writelines('\t\t</script>')
            ############# Scripts ############
            f.writelines('\t</head>\n')
            f.writelines('<body>\n')
            #f.writelines('<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-kenU1KFdBIe4zVF0s0G1M5b4hcpxyD9F7jL+jjXkk+Q2h455rYXK/7HAuoJl+0I4" crossorigin="anonymous"></script>\n')
            f.writelines('<div class="container-fluid">\n')
            f.writelines('<H1>' + 'Total German Universities ' + str(len(self.universities_names))  + '</H1>\n')
            f.writelines('<br>\n')
            f.writelines('<table id="GermanUniversities" class="table table-striped table-sm">\n') #table-condensed
            f.writelines('\t<thead>\n')
            f.writelines('\t<tr>\n')
            f.writelines('\t\t<th>Serial Number</th>\n')
            f.writelines('\t\t<th>Abschluss</th>\n')
            f.writelines('\t\t<th>Sachgebiet(e)</th>\n')
            f.writelines('\t\t<th>Regelstudienzeit</th>\n')
            f.writelines('\t\t<th>Hauptunterrichtssprache</th>\n')
            f.writelines('\t\t<th>Studienform(en)</th>\n')
            f.writelines('\t\t<th>Standort(e)</th>\n')
            f.writelines('\t\t<th>CHE Rank</th>\n')
            f.writelines('\t\t<th>University Name</th>\n')
            f.writelines('\t</tr>\n')
            f.writelines('\t</thead>\n')
            f.writelines('\t<tbody>\n')
            for u, univ in enumerate(self.universities):
                for i, course in enumerate(univ['courses'],0):
                    f.writelines('\t<tr>\n')
                    f.writelines('\t\t<td>' + str(i + 1) + '</td>\n')
                    if course['details']['Abschluss']:
                        f.writelines('\t\t<td>' + course['details']['Abschluss'] + '</td>\n') # course['details']['Abschluss']},{course['details']['Sachgebiet(e)']},{course['details']['Regelstudienzeit']},{course['details']['Hauptunterrichtssprache']},{course['details']['Studienform(en)']},{course['details']['Standort(e)']}
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if course['details']['Sachgebiet(e)']:
                        f.writelines('\t\t<td>' + course['details']['Sachgebiet(e)'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if course['details']['Regelstudienzeit']:
                        f.writelines('\t\t<td>' + course['details']['Regelstudienzeit'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if course['details']['Hauptunterrichtssprache']:
                        f.writelines('\t\t<td>' + course['details']['Hauptunterrichtssprache'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if course['details']['Studienform(en)']:
                        f.writelines('\t\t<td>' + course['details']['Studienform(en)'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if course['details']['Standort(e)']:
                        f.writelines('\t\t<td>' + course['details']['Standort(e)'] + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    
                    if str(univ['cherank']):
                        f.writelines('\t\t<td>' + '<a href=\'' + str(course['href']) + '\'>' + str(univ['cherank']) + '</a>' + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    if univ['name']:
                        f.writelines('\t\t<td>' + '<a href=\'' + univ['url'] + '\'>' + univ['name'] + '</a>' + '</td>\n')
                    else:
                        f.writelines('\t\t<td>' + ' ' + '</td>\n')
                    f.writelines('\t</tr>\n')
                    f.writelines('\t</tbody>\n')
            f.writelines('</table>\n')
            f.writelines('<br>\n')
            f.writelines('<H1>' + 'Total German Universities Links and Type' + str(len(self.universities_names))  + '</H1>\n')
            # f.writelines('<table class="table table-hover table-condensed" id="sortTable">\n')
            # f.writelines('<table class="table table-hover table-sm">\n')
            # f.writelines('\t<thead>\n')
            # f.writelines('\t<tr>\n')
            # f.writelines('\t\t<th>Serial Number</th>\n')
            # f.writelines('\t\t<th>Type</th>\n')
            # f.writelines('\t\t<th>German Universities Names With Links</th>\n')
            # f.writelines('\t</tr>\n')
            # f.writelines('\t</thead>\n')
            # f.writelines('\t<tbody>\n')
            # for index, name in enumerate(self.universities, 0):
            #     f.writelines('\t<tr>\n')
            #     f.writelines('\t\t<td>' + str(index + 1) + '</td>\n')
            #     if name['Type']:
            #         f.writelines('\t\t<td>' + name['Type'] + '</td>\n')
            #     else:
            #         f.writelines('\t\t<td>' + ' ' + '</td>\n')
            #     if name['Name']:
            #         if name['url']:
            #             f.writelines('\t\t<td>' + '<a href = \'' + name['url'] + '\'>' + name['Name'] + '</a>' + '</td>\n')
            #         else:
            #             f.writelines('\t\t<td>' + name['Name'] + '</td>\n')
            #     else:
            #         if name['url']:
            #             f.writelines('\t\t<td>' + '<a href = \'' + name['url'] + '\'>' + name['url'] + '</a>' + '</td>\n')
            #         else:
            #             f.writelines('\t\t<td>' + ' ' + '</td>\n')
            #     f.writelines('\t</tr>\n')
            # f.writelines('\t</tbody>\n')
            # f.writelines('</table>\n')
            f.writelines('</div>\n')
            # f.writelines('<script>\n')
            # f.writelines('\t$(\'#sortTable\').DataTable();\n')
            # f.writelines('</script>\n')
            f.writelines('</body>\n')
            f.writelines('</html>')

if __name__ == "__main__":
    logging.basicConfig(filename='university.log', encoding='utf-8', level=logging.INFO)
    #wg = wikiGermany()
    #che = CHERanking()

    uc = UniversityCourses()
    uc.fetch_universities_coureses()
    
    # if not University.loaduniversities():
    #     University.find_universities_che_pages_url()
    #     University.saveuniversities()
    #     University.output_html()
    #uucc = UniversityCourses()
    #uucc.find_universities_che_pages_url()
    
    #univs = University()
    #univs.find_universities_che_pages_url()

    #uc = UniversityCourses(partial_seed_url_of_university_page_on_che_site='https://studiengaenge.zeit.de/studienangebote?hsid=',rank=100,course_Master_Bachelor_All='master')
    #uc = UniversityCourses(partial_seed_url_of_university_page_on_che_site=None,rank=100,course_Master_Bachelor_All='master')
    
    #uc.saveuniversitycourses()
    #uc.find_courses_from_university_page_on_che_site('https://studiengaenge.zeit.de/studienangebote?hsid=', 100, 'Master')
    #uc.printresults()
    
    # germany_universities = wg.find_universities_names_only_in_germany()
    # germany_universities = wg.find_universities_in_germany()
    # if germany_universities:
    #     wg.output_html()
    #     print("List of universities in Germany:")
    #     for index, university in enumerate(germany_universities, 1):
    #         print(f"{index}. {university}")
    # else:
    #     print("No universities found in Germany.")
