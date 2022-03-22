import requests
from bs4 import BeautifulSoup as bs
import random
from urllib.request import urlopen


def get_html(URL):
    r = requests.get(URL)
    soup = bs(r.content, "html.parser")
    return soup

# Получение советов
def get_hints(soup):
    hints = {}
    i = 1
    try:
        for hint in soup.find('div', class_ = 'method-preparation').find_all('p', class_ = 'bi ib biboard a-err'):
            if not hint.find('a'):
                ind = str(i) if i < 10 else '_' + str(i)
                hints[ind] = hint.text
                i += 1
    except AttributeError:
        return hints
    return hints

# Получение инструкций к рецепту
def get_instructions(soup):
    instructions = {}
    i = 1
    try:
        for instruction in soup.find('ol', class_ = 'instructions').find_all('p', class_ = 'instruction'):
            ind = str(i) if i < 10 else '_' + str(i)
            instructions[ind] = instruction.text.replace(' \r\n', ' ').replace('\r\n', ' ')
            i+=1
    except AttributeError:
        return instructions
    return instructions

# Получение ингредиентов
def get_ingredients(soup):
    ingredients = {}
    i = 1
    for ingredient in soup.find_all('div', class_ = 'ingredient list-item'):
        squant_value = ingredient.findNext('span',class_ = 'squant value').text
        ind = str(i) if i < 10 else '_' + str(i)
        ingredients[ind] = { 'name': ingredient.findNext('a',class_ = 'name').text, 
            'quantity' : squant_value + ' ' +  ingredient.findNext('option', selected = True).text if squant_value != '' else ingredient.findNext('span', class_ = 'type').text}
        i+=1
    return ingredients

# Получение основных данных рецепта
def get_recipe_dict(soup):
    recipe_dict = {}
    recipe_dict['name'] = soup.find('h1', itemprop = 'name').text
    recipe_dict['description'] = soup.find('div', class_ = 'description is-citation').contents[0]
    recipe_info = soup.find('section', id = 'pt_info')
    recipe_dict['image'] = recipe_info.find('img', itemprop = 'image').get('src')
    recipe_dict['cookTime'] = recipe_info.find('span', class_ = 'duration').text.replace('PT', "")
    recipe_dict['servings'] = recipe_info.find('input', id = 'yield_num_input').get('value')
    
    recipe_dict['nutrition'] = {}
    nutration_info = recipe_info.find('div', id = 'nutr_cont_wrap')
    recipe_dict['nutrition']['for'] = nutration_info.find('option', selected = True).text
    recipe_dict['nutrition']['proteins'] = [nutration_info.find('span', id = 'nutr_ratio_p').text + ' %', nutration_info.find('span', id = 'nutr_p').text + ' г']
    recipe_dict['nutrition']['fats'] = [nutration_info.find('span', id = 'nutr_ratio_f').text + ' %', nutration_info.find('span', id = 'nutr_f').text + ' г']
    recipe_dict['nutrition']['carbs'] = [nutration_info.find('span', id = 'nutr_ratio_c').text + ' %', nutration_info.find('span', id = 'nutr_c').text + ' г']
    recipe_dict['nutrition']['kcal'] = nutration_info.find('span', id = 'nutr_kcal').text  + ' ккал'

    recipe_dict['rating'] = random.randint(35, 50)/10

    return recipe_dict

def add_keywords(dict):
    dict['keywords'] = []
    for word in dict['name'].split(' '):
        for i in range(1, len(word)):
            dict['keywords'].append(word[:i + 1].lower())
