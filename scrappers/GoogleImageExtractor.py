'''
This module scrapes image links given from google image search results.
Other implementations
- https://github.com/scirag/selenium-image-crawler/blob/master/crawler/GoogleCrawler.py
'''

# Authors: Jacob Armentrout <jarmentr@uci.edu>
#

# standard
from collections import defaultdict
from copy import deepcopy
import imghdr
import json
import os
import shutil
import sys
import time
import urllib

# vendors
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


class GoogleImageExtractor:
    '''Object to house the configurations and methods for collecting and saving image links.
    '''
    
    # out of the box configuration
    DEFAULT_CONFIG = {
        # google images search url
        'google_url': 'https://www.google.co.in/search?q={0}&source=lnms&tbm=isch',
        # request header
        'header': {'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"},
        # google search queries
        'queries': None,
        # firefox executable path
        'firefox_path': None,
        # max number of images per query
        'req_num': 200,
        # image save path
        'dl_path': 'google_search',
        # each dir has unique imgs amongst eachother or allow redundancy
        'unique_buckets': False,
        # overwrite any existing dirs
        'overwrite_dirs': False,
        # excessive print statements
        'debug': False,
    }
    
    def __init__(self, config):
        '''Configure the image extractor'''
        
        self.config = self.DEFAULT_CONFIG
        self.reconfigure(config)

    def reconfigure(self, config):
        '''Update configuration settings'''
        new_config = deepcopy(self.config)
        
        for setting, val in config.items():
            assert setting in self.DEFAULT_CONFIG
            new_config[setting] = val
        
        for setting, val in new_config.items():
            if val == None:
                raise Exception('Invalid reconfig: {0} is required to be set!'.format(setting))
        
        self.config = new_config

        # used to determine unique links
        # e.g. {links}
        self.links = set()

        # query buckets filled with links
        # e.g. {query_path: {links}}
        self.query_links = defaultdict(set)

        debug = self.config['debug']
        queries = self.config['queries']
        google_url = self.config['google_url']
        dl_path = self.config['dl_path']

        # build urls with the queries
        tokenized = [query.strip().replace(' ', '+') for query in queries]
        self.urls = [google_url.format(tokes) for tokes in tokenized]

        # build save paths with the queries
        underscored = [query.strip().replace(' ', '_') for query in queries]
        self.query_paths = [os.path.join(dl_path, path) for path in underscored]

        if debug:
            for setting, val in self.config.items():
                print('{0}: {1}'.format(setting, val))

    def exec_queries(self):
        '''Launch firefox driver and scrape images for each query'''
        debug = self.config['debug']
        firefox_path = self.config['firefox_path']
        
        if debug:
            print('creating firefox binary...')
        self.binary = FirefoxBinary(firefox_path)
        
        if debug:
            print('generating firefox browser...')
        self.driver = webdriver.Firefox(firefox_binary = self.binary)

        for url, q_path in zip(self.urls, self.query_paths):
            if debug:
                print('grabbing url: {0}'.format(url))
            self.driver.get(url)
            self.scroll_to_bottom()
            self.scrape_img_links(q_path)

        # clean up
        self.driver.quit()
        self.binary = None
        self.driver = None

    def scroll_to_bottom(self):
        '''Use selenium to scroll to the bottom of the page and continue to load results.'''
        assert self.driver
        
        debug = self.config['debug']
        scroll_script = 'window.scrollTo(0, document.body.scrollHeight);var h=document.body.scrollHeight;return h;' 

        height = self.driver.execute_script(scroll_script)
        cursor = 0
        while cursor < height:
            time.sleep(2)
            cursor = height
            height = self.driver.execute_script(scroll_script)
            try:
                if debug:
                    print('looking for "Show more results" button...')
                self.driver.find_element_by_id('smb').click()
            except:
                if debug:
                    print('button not found')
        

    def scrape_img_links(self, query_path):
        '''Scrape the DOM object for image results'''
        assert query_path not in self.query_links
        assert self.driver
        
        debug = self.config['debug']
        req_num = self.config['req_num']
        unique_buckets = self.config['unique_buckets']
        
        # get all image meta data tags
        metas = self.driver.find_elements_by_xpath('//div[@class="rg_meta"]')
        if debug:
            print('Total image metas found: ', len(metas))

        for meta in metas:
            meta_json = json.loads(meta.get_attribute('innerHTML'))
            img_url = meta_json['ou']
            
            if unique_buckets:        
                if img_url in self.links:
                    if debug:
                        print('found duplicate, removing from all query buckets')
                    for q_path in self.query_links:
                        if img_url in self.query_links[q_path]:
                            self.query_links[q_path].remove(img_url)
                            #break # max of 1 already exists
                else:
                    # link does not exist, add it
                    self.query_links[query_path].add(img_url)
            else:
                if img_url not in self.query_links[query_path]:
                    self.query_links[query_path].add(img_url)
                    
            # add link to master list
            self.links.add(img_url)
                
            # max link count
            if len(self.query_links[query_path]) >= req_num:
                if debug:
                    print('found max request count, exiting...')
                break
        
    def create_dir(self):
        '''Create the download directory for the images'''
        debug = self.config['debug']
        overwrite_dirs = self.config['overwrite_dirs']
        dl_path = self.config['dl_path']
        
        if overwrite_dirs:
            if os.path.exists(dl_path):
                if debug:
                    print('removing the directory {0}'.format(dl_path))
                shutil.rmtree(dl_path)
        else:
            assert not os.path.exists(dl_path)
            
        os.mkdir(dl_path)

    def save_img(self, path, url):
        '''Download a single image'''
        debug = self.config['debug']
        header = self.config['header']
        try:
            req = urllib.request.Request(url, None, header)
            raw_img = urllib.request.urlopen(url, timeout=5).read()
            with open(path, 'wb') as f:
                f.write(raw_img)
            
            ext = imghdr.what(path)
            if ext:
                shutil.move(path, path + '.' + ext)
                path += '.' + ext
            if debug:
                print('{0} at {1}'.format(path, url))
        except Exception as e:
            if debug:
                print('could not load {0}: {1}'.format(url, e))

    def save_as_buckets(self):
        '''Save images from their respective query dirs'''
        self.create_dir()
        img_num = 1
        for q_path in self.query_paths:
            os.mkdir(q_path)
            with open(os.path.join(q_path, 'links.txt'), 'w') as f:
                # for every link in that bucket
                for link in self.query_links[q_path]:
                    f.write('{0} {1}\n'.format(link, img_num))
                    save_path = os.path.join(q_path, str(img_num))
                    self.save_img(save_path, link)
                    img_num += 1
                
    def save_all(self):
        '''Save all links gathered to a single dir'''
        dl_path = self.config['dl_path']
        self.create_dir()
        with open(os.path.join(dl_path, 'links.txt'), 'w') as f:
            for i, link in enumerate(self.links):
                f.write('{0} {1}\n'.format(link, i))
                save_path = os.path.join(dl_path, str(i))
                self.save_img(save_path, link)

if __name__ == '__main__':
    queries = ['minecraft', 'minecraft gameplay']
    #queries = ['minecraft sheep', 'minecraft pig', 'minecraft cow', 'minecraft chicken', 'minecraft horse', 'minecraft wolf', 'minecraft ocelot', 'minecraft rabbit', 'minecraft llama', 'minecraft mushroom cow', 'minecraft zombie']
    config = {
        'firefox_path': '/home/jarmentr/bin/firefox-53',
        'queries': queries,
        'dl_path': 'google_search',
        'req_num': 100,
        'unique_buckets': True,
        'overwrite_dirs': True,
        'debug': True
    }
    extr = GoogleImageExtractor(config)
    start = time.time()
    extr.exec_queries()
    print('exec queries time: {0} seconds'.format(time.time() - start))
    start = time.time()
    extr.save_as_buckets()
    print('save as buckets time: {0} seconds'.format(time.time() - start))
