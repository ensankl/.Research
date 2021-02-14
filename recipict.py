import os
import re
import json
import requests
from ibm_watson import VisualRecognitionV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from box import Box
from googletrans import Translator
import imagePreprocessing


class recipicture():
    def __init__(self, file_name, threshold):
        self.authenticator = IAMAuthenticator('ylE7ZMEpzSAAjVlnpUZP1hgyVizaR_XFgxUgcTslGasm')
        self.visual_recognition = VisualRecognitionV3(
            version='2018-03-19',
            authenticator=self.authenticator
        )
        self.visual_recognition.set_service_url(
            'https://api.us-south.visual-recognition.watson.cloud.ibm.com'
            )
        print('\nInitializing variable and constant.\n')
        self.pict_path = file_name
        self.json_path = os.path.splitext(self.pict_path)[0]+'.json'
        self.recipe_path = os.path.splitext(self.pict_path)[0]+'_recipe.json'
        self.images_file = None
        self.classes = None
        self.json_file = None
        self.json_data = None
        self.boxed_json = None
        self.sorted_json = None
        self.j = None
        self.threshold = threshold
        self.jp_list = []
        self.recipe = None
        self.name_list = []
        self.url = "https://katsuo.herokuapp.com/api?item="

    def classing_image(self):
        if os.path.exists(self.json_path):
            print("File already exists.")
            print("Reusing json file.\n")
        else:
            with open(self.pict_path, 'rb') as self.images_file:
                self.classes = self.visual_recognition.classify(
                    images_file=self.images_file,
                    classifier_ids=["food"]).get_result()
            with open(self.json_path, 'w') as self.json_file:
                json.dump(self.classes, self.json_file, indent=2)

    def en2ja(self, phrase):
        tr = Translator(service_urls=['translate.googleapis.com'])
        while True:
            try:
                text = tr.translate(phrase, dest="ja").text
                return text
            except Exception:
                tr = Translator(service_urls=['translate.googleapis.com'])

    def filter_score(self):
        with open(self.json_path, 'r') as self.json_data:
            self.boxed_json = Box(json.load(self.json_data))
            self.sorted_json = sorted(self.boxed_json.images[0].classifiers[0].
                                      classes, key=lambda x: x['score'], reverse=True)
            for j in self.sorted_json:
                if j.score >= self.threshold:
                    self.jp_list.append(self.en2ja(j.__getattr__('class')))
            i = 0
            for l in self.jp_list:
                l = re.sub('料理', '', l)
                print('IndexNum {}:{}'.format(i, l))
                self.jp_list[i] = l
                i += 1


    def get_recipe_list(self, item):
        '''
        item *String object*
        '''
        if item:
            url = 'https://katsuo.herokuapp.com/api?item='+item
            get_url_info = requests.get(url)
            # print(get_url_info)
            # print(get_url_info.headers['Content-Type'])
            jsonData = get_url_info.text.replace('\\u3000', ' ')
            self.j = json.loads(jsonData.replace('\"', '"'))
            # print(self.j[0])
            # show candidate
            r_i1 = r'"recipe": "[^"]+"'
            try:
                for r_list in self.j:
                    r1 = re.search(r_i1, r_list)
                    s = r1.group()
                    self.name_list.append(s)
                i = 0
                e = self.j[0]
                print('\nPrinting candidate below.\n')
                for l in self.name_list:
                    print('IndexNum {}: {}'.format(i, l.replace('"recipe": ', '')))
                    i += 1
            except (AttributeError, IndexError):
                print('Not matching.')
                print('Bad word to search.\n')
                print('Please input manually.\n')
                print('Sorry for the inconvenience.')
                exit()
        if not item:
            print('Item is empty.')
            print('No inputs.')


    def get_ingredients_list(self, index):
        r_str = r'(?<="ingredients": \[)(.*)'
        i_str = r'(.*)(?=\])'
        s_str = r'FoodGroup: [0-9]+, FoodNumber: [a-zA-Z0-9]+, RefNum: [0-9]+, '
        moji = self.j[index]
        mo1 = re.search(r_str, moji)
        mo2 = re.search(i_str, mo1.group())
        self.recipe = re.sub('"', '', mo2.group())
        self.recipe = self.recipe.replace('}, {', '\n\n')
        self.recipe = self.recipe.replace('{', '')
        self.recipe = self.recipe.replace('}', '')
        self.recipe = re.sub(s_str, '', self.recipe)
        print()
        print(self.recipe)



if __name__ == "__main__":
    directory = r'C:/Users/jinto/Documents/.Research/data'
    name = '/tomato.jpg'
    thsh = 0.5
    print('THRESHOLD IS {}'.format(thsh))
    man = int(input('AUTO DETECT = 0\nUSE MANUALLY = 1\n'))
# initialize
    if not man:
        cropped = imagePreprocessing.imagePreprocessing(directory+name)
        food = recipicture(cropped, threshold=thsh)
    if man:
        food = recipicture(directory+name, threshold=thsh)
# detecting mode
# auto mode
    if not man:
        print('****************************')
        print('RUNNING AS AUTO DETECT MODE.')
        print('****************************\n')
# class image and make json file
        food.classing_image()
        food.filter_score()
# select ingredients
        index_pict = int(input('\nSelect which is shown in picture.\n'))
        food.get_recipe_list(food.jp_list[index_pict])
# select recipe
        index_recipe = int(input('\nSelect which you wanna make.\n'))
        food.get_ingredients_list(index_recipe)
# manual mode
    if man:
        print('***********************')
        print('RUNNING AS MANUAL MODE.')
        print('***********************\n')
# input ingredients from keyboard
        index_man = input('\nWrite ingredients what you have in Japanese.\n')
        print('\n')
        food.get_recipe_list(index_man)
# select recipe
        index_r = int(input('\nSelect which you wanna make.\n'))
        print('\n')
        food.get_ingredients_list(index_r)
