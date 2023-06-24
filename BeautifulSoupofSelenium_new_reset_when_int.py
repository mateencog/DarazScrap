#!/usr/bin/python
import urllib
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
import sys
import json
import pickle
from random import random



def webpage(link):
    driver.get(link)
    return driver.page_source

def download_parallel(args):
    cpus = cpu_count()
    #print(args)
    results = ThreadPool(cpus - 1).imap_unordered(downloader, args)
    #print(results)
	
def downloader(args):
    try:
        verified_url, filenames, aisle, path = args[0], args[1], args[2], args[3]
        with open(aisle + '/' + path + '/'+ filenames, 'wb') as f:
            response = requests.get(verified_url)
            f.write(response.content)
    except Exception as e:
            print('Exception in download_parallel():', e)
            
#########victim_website

my_file = open("aisle23.txt", "r").read().split("\n")
driver = webdriver.Firefox()
# driver = webdriver.Chrome()
aisle_dir = os.listdir()

#########Continuing_download

for i, j in enumerate(my_file):
    if j not in aisle_dir:
        if i == 0:
            print('starting fresh for the current aisle list')
            break
        print('continuation from ', my_file[i - 1])
        continuation = True
        shutil.rmtree(my_file[i - 1])
        my_file = my_file[ i - 1 : ]
        break

for aisle in my_file:
    
    image_dupe = 0
    database = set()
    print('now parsing aisle ', aisle)
    website_kaboom = 'https://www.daraz.pk/' + aisle + '/?'

    #########Total pages
    try:
        html = webpage('https://www.daraz.pk/' + aisle + '/?' + 'page=1')
        num = html.rfind('?page=') + 6
        for i in range(0,4):
            if html[num+i] == '"':
                break
        page_num = int(html[int(num):int(num)+i])
        print('total pages for ', aisle, page_num)
    except:
        page_num = 2
        print('error in pagination, continuation', aisle)
        
    if not os.path.isdir(aisle):
        os.makedirs(aisle)

    #########Crawling

    for i in range(1, page_num + 1):
    	
        verified_urls = []
        filenames = []
        
        path = 'images_page_' + str(i)

        if not os.path.isdir(aisle + '/' + path):
            os.makedirs(aisle + '/' + path)

        print('page ', i )
        website = website_kaboom + 'page=' + str(i)

    #########Driver Code

        try:
            html = webpage(website)
        except:
            print('error in browser', aisle)

    #########Extra Sneaky
    
        # driver.minimize_window()
        time.sleep(random() + random() + 2)

    #########Extractor Code
        try:
            soup = BeautifulSoup(html, 'html.parser')
            img_tags = soup.find_all('img')

            urls = [img['src'] for img in img_tags]
            print('found ', len(urls), 'urls')
        except:
            print('error in extractor', aisle)
            
    #########Checker Code

        for url in urls:
            result = re.search(r'/([\w_-]+[.](jpg|png))$', url)

            if not result:
                #print("regex wont match: {}".format(url))
                with open(aisle + '/_regex_unmatch_' + aisle + '.txt', 'a') as bm:
                    bm.write('\n')
                    bm.write(url+ ' ' + str(aisle) + ' ' + str(page_num))
                continue
                
            filename = result.group(1)

            if "static" not in url:
                # print('ignored, not a product: ', url)
                with open(aisle + '/_ignored_' + aisle + '.txt', 'a') as be:
                    be.write('\n')
                    be.write(url+ ' ' + str(aisle) + ' ' + str(i))
                continue

            if 'http' not in url:
                url = '{}{}'.format('https:', url)

            if filename in database:
                with open(aisle + '/_duplicates_' + aisle + '.txt', 'a') as be:
                    image_dupe = image_dupe + 1
                    # print('ignored, already downloaded: ', url)
                    be.write('\n')
                    be.write(url + ' ' + str(aisle) + ' ' + str(i))
                continue
            
            with open(aisle + '/_urls_' + aisle + '.txt', 'a') as bn:
                bn.write('\n')
                bn.write(url)

            with open(aisle + '/_filename_' + aisle + '.txt', 'a') as bo:
                bo.write('\n')
                bo.write(filename)
                
            database.add(filename)
            verified_urls.append(url)
            filenames.append(filename)
    
    #########Stealing metadata
        soup_str = str(soup)
        if "punish" in soup_str:
        	print('got caught, winding up!')
        	exit()
        ind = soup_str.find("listItems")
        cut1 = soup_str[ind: len(soup_str)]
        ind2 = cut1.find(',"breadcrumb":[')
        cut2 = cut1[11 : ind2]
        dicts = json.loads(cut2)
        file_dict = aisle + '/images_page_' + str(i) + '/page_' + str(i) + '.json'
        with open(file_dict, 'w') as f:
        	json.dump(dicts, f, indent=2)

    #########Actual stealing
        aisles = [aisle] * len(verified_urls)
        paths = [path] * len(verified_urls)
        inputs = zip(verified_urls, filenames, aisles , paths)
        download_parallel(inputs)

        if i == page_num:
            print('total cache hit ', image_dupe)
            print('images downloaded for ', aisle, ' ', len(database))
