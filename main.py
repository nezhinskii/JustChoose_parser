from ast import keyword
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from firebase_admin import storage
import get_recipe
import json
import requests
import re
from urllib.request import urlopen

BASE_URL = 'https://1000.menu'

def recipes_page_process(URL):
    soup = get_recipe.get_html(URL)
    for recipe in soup.find_all('div', class_ = 'cn-item'):
        print(BASE_URL + recipe.findNext('a').get('href'))
        load_recipe(BASE_URL + recipe.findNext('a').get('href'), ['salad', 'second_course'])

def load_recipe(URL, categories_list):
    soup = get_recipe.get_html(URL)
    match = re.search('(?<=\/)\d+(?=-)', URL)
    if match: 
        id = match[0]
    else:
        print('INVALID URL')
        return 
    recipe_dict = get_recipe.get_recipe_dict(soup)
    for category in categories_list:
        recipe_dict[category] = True
    ingredients = get_recipe.get_ingredients(soup)
    instructions = get_recipe.get_instructions(soup)
    if len(instructions) == 0:
        print('INVALID INSTRUCTIONS' + recipe_dict['name'])
        return
    hints = get_recipe.get_hints(soup)
    get_recipe.add_keywords(recipe_dict)

    recipe_doc = db.collection('recipes').document(id)
    if recipe_doc.get().exists:
        print('SUCH ID ALREADY EXIST')
        return
    recipe_doc.set(recipe_dict)

    recipe_ingredients = recipe_doc.collection('recipe_ingredients').document().set(ingredients)
    recipe_instructions = recipe_doc.collection('recipe_instructions').document().set(instructions)
    recipe_hints = recipe_doc.collection('recipe_hints').document().set(hints)
    default_ingredients = ['соль', 'перец_горошком', 'лавровый_лист', 'вода', 'морская_соль', 'сода', 'уксус', 'растительное_масло', 'масло']
    for value in ingredients.values():
        id = value['name'].lower().replace(' ', '_')
        if not id in default_ingredients:
            doc = db.collection('ingredients').document(id)
            if not doc.get().exists:
                keywords = []
                for word in id.split('_'):
                    for i in range(1, len(word)):
                        keywords.append(word[:i + 1].lower())
                doc.set({
                    'keywords': keywords
                })
            doc.update({
                'in_recipes':firestore.ArrayUnion([recipe_doc.id])
            })
    print('SUCCES ' + recipe_dict['name'])
    # print(ingredients)
    # print(json.dumps(instructions, indent=4, ensure_ascii=False))
    # print(json.dumps(hints, indent=4, ensure_ascii=False))
    # print(json.dumps(recipe_dict, indent=4, ensure_ascii=False))

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'storageBucket':'justchoose-2171b.appspot.com'
})
db = firestore.client()

# recipes_page_process('https://1000.menu/catalog/salaty?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog%5B47%5D=47&arr_catalog_sub%5B47%5D%5B851%5D=851&arr_catalog_sub%5B47%5D%5B7709%5D=7709&arr_catalog_sub%5B47%5D%5B864%5D=864&arr_catalog_sub%5B47%5D%5B870%5D=870&arr_catalog_sub%5B47%5D%5B6468%5D=6468&arr_catalog_sub%5B47%5D%5B865%5D=865&arr_catalog_sub%5B47%5D%5B859%5D=859&arr_catalog_sub%5B47%5D%5B858%5D=858&arr_catalog_sub%5B47%5D%5B856%5D=856&arr_catalog_sub%5B47%5D%5B8185%5D=8185&arr_catalog_sub%5B47%5D%5B8950%5D=8950&arr_catalog_sub%5B47%5D%5B7913%5D=7913&arr_catalog_sub%5B47%5D%5B867%5D=867&arr_catalog_sub%5B47%5D%5B9054%5D=9054&arr_catalog_sub%5B47%5D%5B872%5D=872&arr_catalog_sub%5B47%5D%5B7472%5D=7472&arr_catalog_sub%5B47%5D%5B8304%5D=8304&arr_catalog_sub%5B47%5D%5B6841%5D=6841&arr_catalog_sub%5B47%5D%5B8829%5D=8829&arr_catalog_sub%5B47%5D%5B8447%5D=8447&arr_catalog_sub%5B47%5D%5B8846%5D=8846&arr_catalog_sub%5B47%5D%5B8962%5D=8962&arr_catalog_sub%5B47%5D%5B8168%5D=8168&arr_catalog_sub%5B47%5D%5B9193%5D=9193&arr_catalog_sub%5B47%5D%5B9048%5D=9048&arr_catalog_sub%5B47%5D%5B9434%5D=9434&arr_catalog_sub%5B47%5D%5B7255%5D=7255&arr_catalog_sub%5B47%5D%5B8965%5D=8965&arr_catalog_sub%5B47%5D%5B6580%5D=6580&arr_catalog_sub%5B47%5D%5B8990%5D=8990&arr_catalog_sub%5B47%5D%5B862%5D=862&arr_catalog_sub%5B47%5D%5B871%5D=871&arr_catalog_sub%5B47%5D%5B9021%5D=9021&arr_catalog_sub%5B47%5D%5B7963%5D=7963&arr_catalog_sub%5B47%5D%5B7977%5D=7977&arr_catalog_sub%5B47%5D%5B6600%5D=6600&arr_catalog_sub%5B47%5D%5B6175%5D=6175&arr_catalog_sub%5B47%5D%5B8545%5D=8545&arr_catalog_sub%5B47%5D%5B1000%5D=1000&arr_catalog_sub%5B47%5D%5B9012%5D=9012&arr_catalog_sub%5B47%5D%5B6773%5D=6773&arr_catalog_sub%5B47%5D%5B869%5D=869&arr_catalog_sub%5B47%5D%5B6202%5D=6202&arr_catalog_sub%5B47%5D%5B6195%5D=6195&arr_catalog_sub%5B47%5D%5B6204%5D=6204&arr_catalog_sub%5B47%5D%5B6203%5D=6203&arr_catalog_sub%5B47%5D%5B8939%5D=8939&arr_catalog_sub%5B47%5D%5B7344%5D=7344')

# поиск по салатам https://1000.menu/catalog/salaty?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog%5B47%5D=47&arr_catalog_sub%5B47%5D%5B851%5D=851&arr_catalog_sub%5B47%5D%5B7709%5D=7709&arr_catalog_sub%5B47%5D%5B864%5D=864&arr_catalog_sub%5B47%5D%5B870%5D=870&arr_catalog_sub%5B47%5D%5B6468%5D=6468&arr_catalog_sub%5B47%5D%5B865%5D=865&arr_catalog_sub%5B47%5D%5B859%5D=859&arr_catalog_sub%5B47%5D%5B858%5D=858&arr_catalog_sub%5B47%5D%5B856%5D=856&arr_catalog_sub%5B47%5D%5B8185%5D=8185&arr_catalog_sub%5B47%5D%5B8950%5D=8950&arr_catalog_sub%5B47%5D%5B7913%5D=7913&arr_catalog_sub%5B47%5D%5B867%5D=867&arr_catalog_sub%5B47%5D%5B9054%5D=9054&arr_catalog_sub%5B47%5D%5B872%5D=872&arr_catalog_sub%5B47%5D%5B7472%5D=7472&arr_catalog_sub%5B47%5D%5B8304%5D=8304&arr_catalog_sub%5B47%5D%5B6841%5D=6841&arr_catalog_sub%5B47%5D%5B8829%5D=8829&arr_catalog_sub%5B47%5D%5B8447%5D=8447&arr_catalog_sub%5B47%5D%5B8846%5D=8846&arr_catalog_sub%5B47%5D%5B8962%5D=8962&arr_catalog_sub%5B47%5D%5B8168%5D=8168&arr_catalog_sub%5B47%5D%5B9193%5D=9193&arr_catalog_sub%5B47%5D%5B9048%5D=9048&arr_catalog_sub%5B47%5D%5B9434%5D=9434&arr_catalog_sub%5B47%5D%5B7255%5D=7255&arr_catalog_sub%5B47%5D%5B8965%5D=8965&arr_catalog_sub%5B47%5D%5B6580%5D=6580&arr_catalog_sub%5B47%5D%5B8990%5D=8990&arr_catalog_sub%5B47%5D%5B862%5D=862&arr_catalog_sub%5B47%5D%5B871%5D=871&arr_catalog_sub%5B47%5D%5B9021%5D=9021&arr_catalog_sub%5B47%5D%5B7963%5D=7963&arr_catalog_sub%5B47%5D%5B7977%5D=7977&arr_catalog_sub%5B47%5D%5B6600%5D=6600&arr_catalog_sub%5B47%5D%5B6175%5D=6175&arr_catalog_sub%5B47%5D%5B8545%5D=8545&arr_catalog_sub%5B47%5D%5B1000%5D=1000&arr_catalog_sub%5B47%5D%5B9012%5D=9012&arr_catalog_sub%5B47%5D%5B6773%5D=6773&arr_catalog_sub%5B47%5D%5B869%5D=869&arr_catalog_sub%5B47%5D%5B6202%5D=6202&arr_catalog_sub%5B47%5D%5B6195%5D=6195&arr_catalog_sub%5B47%5D%5B6204%5D=6204&arr_catalog_sub%5B47%5D%5B6203%5D=6203&arr_catalog_sub%5B47%5D%5B8939%5D=8939&arr_catalog_sub%5B47%5D%5B7344%5D=7344
# пока добавил только первую страницу рецептов
# набор категорий для салатов - salad second_course