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

def recipes_page_process(URL, page_number, categories_list, first_n_recipes = 180):
    soup = get_recipe.get_html(URL)
    recipes_added = 0
    i = page_number
    while i != 1:
        btn = soup.find('button', string = 'Показать еще результаты поиска...')
        if btn is None:
            print('PAGE IS NOT EXIST ' + page_number)
            return
        soup = get_recipe.get_html(BASE_URL + btn.get('onclick').split('\'')[1])
        i-=1
    for recipe in soup.find_all('div', class_ = 'cn-item')[:first_n_recipes]:
        print(BASE_URL + recipe.findNext('a').get('href'))
        if load_recipe(BASE_URL + recipe.findNext('a').get('href'), categories_list):
            recipes_added+=1
        print(recipes_added)
    print('RECIPES ADDED ' + str(recipes_added))

# def change_category(URL):
#     match = re.search('(?<=\/)\d+(?=-)', URL)
#     if match: 
#         id = match[0]
#     else:
#         print('INVALID URL')
#         return 
#     doc = db.collection('recipes').document(id)
#     if doc.get().exists:
#         doc.update({
#             'seafood': firestore.DELETE_FIELD,
#         })
#         print(id + ' category changed')

def load_recipe(URL, categories_list):
    soup = get_recipe.get_html(URL)
    match = re.search('(?<=\/)\d+(?=-)', URL)
    if match: 
        id = match[0]
    else:
        print('INVALID URL')
        return False
    recipe_dict = get_recipe.get_recipe_dict(soup)
    for category in categories_list:
        recipe_dict[category] = True
    ingredients = get_recipe.get_ingredients(soup)
    instructions = get_recipe.get_instructions(soup)
    if len(instructions) == 0:
        print('INVALID INSTRUCTIONS ' + recipe_dict['name'])
        return False
    hints = get_recipe.get_hints(soup)
    get_recipe.add_keywords(recipe_dict)

    recipe_doc = db.collection('recipes').document(id)
    if recipe_doc.get().exists:
        print('SUCH ID ALREADY EXIST')
        return False
    recipe_doc.set(recipe_dict)

    recipe_doc.collection('recipe_ingredients').document().set(ingredients)
    recipe_doc.collection('recipe_instructions').document().set(instructions)
    recipe_doc.collection('recipe_hints').document().set(hints)
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
    return True
    # print(ingredients)
    # print(json.dumps(instructions, indent=4, ensure_ascii=False))
    # print(json.dumps(hints, indent=4, ensure_ascii=False))
    # print(json.dumps(recipe_dict, indent=4, ensure_ascii=False))

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'storageBucket':'justchoose-2171b.appspot.com'
})
db = firestore.client()

# recipes_page_process('https://1000.menu/catalog/bezalkogolnje-napitki?arr_catalog_sub%5B6500%5D%5B16%5D=16', 1, 
# ['drinks'])

# ПЕРВОЕ БЛЮДО
    # КЛАССИКА
    # ссылка https://1000.menu/cooking/search?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B9055%5D=9055&arr_catalog_1%5B52%5D=52&arr_catalog_1%5B94%5D=94&arr_catalog%5B12%5D=12
    # добавлены страницы: 1 2
    # набор категорий: first_course classic

    # НЕСТАНДАРТНОЕ
    # здесь несколько рецептов из категорий разных национальных блюд
    # ссылки: 
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B8806%5D=8806&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B8864%5D=8864&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B6099%5D=6099&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B61%5D=61&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B73%5D=73&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B82%5D=82&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B85%5D=85&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B87%5D=87&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B95%5D=95&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B96%5D=96&arr_catalog%5B12%5D=12
    # https://1000.menu/catalog/supj?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B7%5D=7&arr_catalog_1%5B97%5D=97&arr_catalog%5B12%5D=12
    # набор категорий: first_course unusual

# ВТОРОЕ БЛЮДО
    # САЛАТЫ
    # ссылка https://1000.menu/catalog/salaty?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog%5B47%5D=47&arr_catalog_sub%5B47%5D%5B851%5D=851&arr_catalog_sub%5B47%5D%5B7709%5D=7709&arr_catalog_sub%5B47%5D%5B864%5D=864&arr_catalog_sub%5B47%5D%5B870%5D=870&arr_catalog_sub%5B47%5D%5B6468%5D=6468&arr_catalog_sub%5B47%5D%5B865%5D=865&arr_catalog_sub%5B47%5D%5B859%5D=859&arr_catalog_sub%5B47%5D%5B858%5D=858&arr_catalog_sub%5B47%5D%5B856%5D=856&arr_catalog_sub%5B47%5D%5B8185%5D=8185&arr_catalog_sub%5B47%5D%5B8950%5D=8950&arr_catalog_sub%5B47%5D%5B7913%5D=7913&arr_catalog_sub%5B47%5D%5B867%5D=867&arr_catalog_sub%5B47%5D%5B9054%5D=9054&arr_catalog_sub%5B47%5D%5B872%5D=872&arr_catalog_sub%5B47%5D%5B7472%5D=7472&arr_catalog_sub%5B47%5D%5B8304%5D=8304&arr_catalog_sub%5B47%5D%5B6841%5D=6841&arr_catalog_sub%5B47%5D%5B8829%5D=8829&arr_catalog_sub%5B47%5D%5B8447%5D=8447&arr_catalog_sub%5B47%5D%5B8846%5D=8846&arr_catalog_sub%5B47%5D%5B8962%5D=8962&arr_catalog_sub%5B47%5D%5B8168%5D=8168&arr_catalog_sub%5B47%5D%5B9193%5D=9193&arr_catalog_sub%5B47%5D%5B9048%5D=9048&arr_catalog_sub%5B47%5D%5B9434%5D=9434&arr_catalog_sub%5B47%5D%5B7255%5D=7255&arr_catalog_sub%5B47%5D%5B8965%5D=8965&arr_catalog_sub%5B47%5D%5B6580%5D=6580&arr_catalog_sub%5B47%5D%5B8990%5D=8990&arr_catalog_sub%5B47%5D%5B862%5D=862&arr_catalog_sub%5B47%5D%5B871%5D=871&arr_catalog_sub%5B47%5D%5B9021%5D=9021&arr_catalog_sub%5B47%5D%5B7963%5D=7963&arr_catalog_sub%5B47%5D%5B7977%5D=7977&arr_catalog_sub%5B47%5D%5B6600%5D=6600&arr_catalog_sub%5B47%5D%5B6175%5D=6175&arr_catalog_sub%5B47%5D%5B8545%5D=8545&arr_catalog_sub%5B47%5D%5B1000%5D=1000&arr_catalog_sub%5B47%5D%5B9012%5D=9012&arr_catalog_sub%5B47%5D%5B6773%5D=6773&arr_catalog_sub%5B47%5D%5B869%5D=869&arr_catalog_sub%5B47%5D%5B6202%5D=6202&arr_catalog_sub%5B47%5D%5B6195%5D=6195&arr_catalog_sub%5B47%5D%5B6204%5D=6204&arr_catalog_sub%5B47%5D%5B6203%5D=6203&arr_catalog_sub%5B47%5D%5B8939%5D=8939&arr_catalog_sub%5B47%5D%5B7344%5D=7344
    # добавлены страницы: 1 2 3
    # набор категорий: second_course salad
    
    # ЗАПЕЧЕННОЕ
        # ИЗ МЯСА И ПТИЦЫ
        # ссылка для поиска https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=18&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B963%5D=963&arr_catalog%5B13%5D=13
        # добавлены страницы: 1
        # набор категорий: second_course baked meat

        # ИЗ РЫБЫ И МОРЕПРОДУКТОВ
        # ссылка морепродукты https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=1699&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B963%5D=963&arr_catalog%5B13%5D=13
        # добавлены страницы: 1 (первые 100)
        # ссылка рыба https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=20&sostav_arr_remove%5B%5D=1699&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B963%5D=963&arr_catalog%5B13%5D=13
        # добавлены страницы: 1
        # набор категорий: second_course baked seafood

        # ИЗ ОВОЩЕЙ
        # ссылка https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=23&sostav_arr_remove%5B%5D=18&sostav_arr_remove%5B%5D=20&sostav_arr_remove%5B%5D=1699&sostav_arr_remove%5B%5D=38&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B963%5D=963&arr_catalog%5B13%5D=13
        # добавлены страницы: 1
        # набор категорий: second_course baked vegetables

    # ЖАРЕНОЕ
        # ИЗ МЯСА И ПТИЦЫ
        # ссылка https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=18&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B960%5D=960&arr_catalog_1%5B8644%5D=8644&arr_catalog%5B13%5D=13
        # добавлены страницы: 1
        # набор категорий: second_course fried meat

        # ИЗ РЫБЫ И МОРЕПРОДУКТОВ
        # ссылка морепродукты https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=1699&sostav_arr_remove%5B%5D=20&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B960%5D=960&arr_catalog_1%5B8644%5D=8644&arr_catalog%5B13%5D=13
        # добавлены страницы: 1 
        # ссылка рыба https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=20&sostav_arr_remove%5B%5D=1699&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B960%5D=960&arr_catalog_1%5B8644%5D=8644&arr_catalog%5B13%5D=13
        # добавлены страницы: 1 (первые 100)
        # набор категорий: second_course fried seafood

        # ИЗ ОВОЩЕЙ
        # ссылка https://1000.menu/cooking/search?ms=1&str=&sostav_arr_add%5B%5D=23&sostav_arr_remove%5B%5D=18&sostav_arr_remove%5B%5D=20&sostav_arr_remove%5B%5D=1699&sostav_arr_remove%5B%5D=38&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B960%5D=960&arr_catalog_1%5B8644%5D=8644&arr_catalog%5B13%5D=13
        # добавлены страницы: 1
        # набор категорий: second_course fried vegetables

    # ВАРЕНОЕ И ГАРНИРЫ
    # ссылка вареное - этот категория на сайте поломанная, так что пока гарниры только
    # добавлены страницы:
    # ссылка гарниры https://1000.menu/catalog/garnirj
    # добавлены страницы: 1 2
    # набор категорий: second_course boiled_side_dishes

# ДЕСЕРТЫ
    # НА СКОВОРОДКЕ
    # ссылка https://1000.menu/cooking/search?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B960%5D=960&arr_catalog%5B14%5D=14
    # добавлены страницы: 1 (до 66)
    # ссылка https://1000.menu/cooking/search?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B8644%5D=8644&arr_catalog%5B14%5D=14
    # добавлены страницы: 1 (до 21)
    # ссылка https://1000.menu/catalog/syrniki-na-skovorode
    # добавлены страницы: 1 (до 20)
    # ссылка https://1000.menu/catalog/pankeiki
    # добавлены страницы: 1 (до 20)
    # ссылка https://1000.menu/catalog/blinj-i-blinchiki
    # добавлены страницы: 1 (до 40)
    # набор категорий: desserts fried

    # В ДУХОВКЕ
    # ссылка https://1000.menu/cooking/search?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B963%5D=963&arr_catalog%5B14%5D=14
    # добавлены страницы: 1 
    # набор категорий: desserts oven

    # БЕЗ ВЫПЕЧКИ И ЖАРКИ
    # ссылка https://1000.menu/cooking/search?ms=1&str=&es_tf=0&es_tt=14&es_cf=0&es_ct=2000&arr_catalog_1%5B959%5D=959&arr_catalog_1%5B6630%5D=6630&arr_catalog%5B14%5D=14
    # добавлены страницы: 1 (до 160)
    # набор категорий: desserts without_heat 

# ЗАКУСКИ
    # ГОРЯЧИЕ
    # ссылка https://1000.menu/catalog/zakuski-goryachie
    # добавлены страницы: 1
    # набор категорий: snacks hot

    # ХОЛОДНЫЕ
    # ссылка https://1000.menu/catalog/zakuski-xolodnje
    # добавлены страницы: 1
    # набор категорий: snacks cold

# НАПИТКИ
# ссылка https://1000.menu/catalog/bezalkogolnje-napitki?arr_catalog_sub%5B6500%5D%5B16%5D=16
# добавлены страницы: 1
# набор категорий: drinks