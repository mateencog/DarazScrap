#!/usr/bin/python

from selenium import webdriver
import time
import re
import requests
from bs4 import BeautifulSoup
import os
import shutil
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
from multiprocessing import Process
import json
from random import random
from requests.adapters import HTTPAdapter, Retry

def webpage(link):
    driver.get(link)
    return driver.page_source

def download_parallel(args):
    cpus = cpu_count()
    #print(args)
    results = ThreadPool(cpus - 1).imap_unordered(downloader, args)
	
def downloader(args):
    #try:
    verified_url, filenames, aisle, path, s = args[0], args[1], args[2], args[3], args[4]
    with open(aisle + '/' + path + '/'+ filenames, 'wb') as f:
        response = s.get(verified_url)
        f.write(response.content)
    #except Exception as e:
     #       print('Exception in download_parallel():', e)
          
def souper(html):
    soup = BeautifulSoup(html, 'html.parser')
    img_tags = soup.find_all('img')

    urls = [img['src'] for img in img_tags]
    print('found ', len(urls), 'urls')
    return urls, soup

def sieve(urls, aisle, page, database, image_dupe):
    verified_urls = []
    filenames = []
    for url in urls:
        result = re.search(r'/([\w_-]+[.](jpg|png))$', url)
    
        if not result:
            #print("regex wont match: {}".format(url))
            #with open(aisle + '/_regex_unmatch_' + aisle + '.txt', 'a') as bm:
            #    bm.write('\n')
            #    bm.write(url+ ' ' + str(aisle) + ' ' + str(page))
            continue
            
        filename = result.group(1)
        if filename in database:
            with open(aisle + '/images_page_'+ str(page) + '/_duplicates_' + aisle + '_images_page_'+ str(page) + '.txt', 'a') as be:
                image_dupe = image_dupe + 1
                # print('ignored, already downloaded: ', url)
                be.write('\n')
                be.write(url)
            continue
            
        if 'http' not in url:
            url = '{}{}'.format('https:', url)
            
        if "live-21.slatic" in url or "static" in url:
            #print(url)
            with open(aisle +  '/images_page_'+ str(page) + '/_urls_' + aisle + '_images_page_'+ str(page) + '.txt', 'a') as bn:
                bn.write('\n')
                bn.write(url)
            with open(aisle + '/images_page_'+ str(page) + '/_filenames_' + aisle + '_images_page_'+ str(page) + '.txt', 'a') as bo:
                bo.write('\n')
                bo.write(filename)
            database.add(filename)
            verified_urls.append(url)
            filenames.append(filename)
                    # print(url)
            # print('ignored, not a product: ', url)
        else:
            with open(aisle + '/images_page_' + str(page) + '/_ignored_' + aisle + '_images_page_'+ str(page) + '.txt', 'a') as be:
                be.write('\n')
                be.write(url+ ' ' + str(aisle) + ' ' + str(page))
        
    return database, verified_urls, filenames, image_dupe

#########website_name

s = requests.Session()
retries = Retry(total=5,
                backoff_factor=0.1,
                status_forcelist=[ 500, 502, 503, 504, 104 ])
s.mount('http://', HTTPAdapter(max_retries=retries))

my_file = open("aisle23.txt", "r").read().split("\n")
# driver = webdriver.Firefox()
driver = webdriver.Firefox()
aisle_dir = os.listdir()
#print(my_file)

#########Continuing_download

for i, j in enumerate(my_file):
    if j not in aisle_dir:
        if i == 0:
            print('starting fresh for the current aisle list')
            page_current = 1
            database = set()
            break
        print('continuation from ', my_file[i - 1])
        continuation = True
        try:
            progress_path = my_file[i - 1] + '/download.progress'
            #print(progress_path)
            progress = open(progress_path, "r+")
            page_current = int(progress.readlines()[0]) - 1
            if page_current == 0:
                page_current = 1
            my_file = my_file[ i - 1 : ]
            print('continuation from page ', page_current)
            database = set()
        except:
            database = set()
            page_current = 1
            #print(page_current)
            shutil.rmtree(my_file[i - 1])
            my_file = my_file[ i - 1 : ]
        break

for aisle in my_file:
    
    image_dupe = 0
    print('now parsing aisle ', aisle)
    website_kaboom = 'https://www.daraz.pk/' + aisle + '/?'

    #########Figuring out the total pages
	
    html = webpage('https://www.daraz.pk/' + aisle + '/?' + 'page=1')
    num = html.rfind('?page=') + 6
    if num == 5:
        print('could not find any pages')
		# meta_capture = False
		# page_num = 2
        print('skipping meta for ', aisle)
        time.sleep(random() + random() + 2)
        with open('aisle_ignored.txt', 'a') as bn:
            bn.write('\n')
            bn.write(aisle)
        if not os.path.isdir(aisle):
            os.makedirs(aisle)
        urls, soup = souper(html)
        page = 1
        database, verified_urls, filenames, image_dupe = sieve(urls, aisle, page, database, image_dupe)
        aisles = [aisle] * len(verified_urls)
        path = 'images_page_' + str(page)
        if not os.path.isdir(aisle + '/' + path):
            os.makedirs(aisle + '/' + path)
        paths = [path] * len(verified_urls)
        inputs = zip(verified_urls, filenames, aisles , paths)
        download_parallel(inputs)
        file_dict = aisle + '/images_page_' + str(page) + '/page_' + str(page) + '.soup'
        with open(file_dict, 'a') as bosa:
            bosa.write(html)
        print('total cache hit ', image_dupe)
        print('images downloaded for ', aisle, ' ', len(database))
            
        continue
    for i in range(0, 4):
        if html[num+i] == '"':
            break
    page_num = int(html[int(num):int(num)+i])
    print('total pages for ', aisle, page_num)
    meta_capture = True

    if not os.path.isdir(aisle):
        os.makedirs(aisle)

    #########crawling the pages in range

    for page in range(page_current, page_num + 1):
        
        path = 'images_page_' + str(page)

        if not os.path.isdir(aisle + '/' + path):
            os.makedirs(aisle + '/' + path)
        else:

            shutil.rmtree(aisle + '/' + path)
            #os.rmdir(aisle + '/' + path)
            os.makedirs(aisle + '/' + path)

        print('page ', page )
        website = website_kaboom + 'page=' + str(page)

    #########Driver Code

        try:
            html = webpage(website)
        except:
            print('error in browser', aisle)

    #########Extra Sneaky
    
        # driver.minimize_window()
        time.sleep(random() + random() + random() + 2)

    #########Extractor Code

        urls, soup = souper(html)
            
    #########Checker Code
        database, verified_urls, filenames, image_dupe = sieve(urls, aisle, page, database, image_dupe)
    
    #########Stealing metadata
        soup_str = str(soup)
        if "punish" in soup_str:
        	print('got caught, winding up!')
        	exit()
  #      try:
        if meta_capture == True:
            ind = soup_str.find("listItems")
            cut1 = soup_str[ind: len(soup_str)]
            ind2 = cut1.find(',"breadcrumb":[')
            cut2 = cut1[11 : ind2]
            dicts = json.loads(cut2)
            file_dict = aisle + '/images_page_' + str(page) + '/page_' + str(page) + '.json'
            with open(file_dict, 'w') as f:
                json.dump(dicts, f, indent=2)
  #      except Exception as e:
  #          print('error in meta-stealer', e)

    #########Actual stealing
        aisles = [aisle] * len(verified_urls)
        paths = [path] * len(verified_urls)
        inputs = zip(verified_urls, filenames, aisles , paths, s)
        download_parallel(inputs)
        file_dict = aisle + '/images_page_' + str(page) + '/page_' + str(page) + '.soup'
        with open(file_dict, 'a') as bos:
            bos.write(html)
        progress_file = aisle + '/download.progress'
        with open(progress_file, 'w+') as prog:
            prog.write(str(page))

        if page == page_num:
            print('total cache hit ', image_dupe)
            print('images downloaded for ', aisle, ' ', len(database))
