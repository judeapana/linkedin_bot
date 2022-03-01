import os

from flask import render_template, request, jsonify
from selenium import webdriver

from linkedin.app import app
from scrap import Bot

PATH = 'drivers/geckodriver.exe'


@app.route('/')
def index():
    return render_template('app/index.html', title='LinkedIn BOT')


@app.route('/api/search')
async def search():
    q = request.args.get('q')
    driver = webdriver.Firefox(executable_path=PATH)
    bot = Bot(driver)
    bot.login(_username=os.environ.get('_USERNAME'), _password=os.environ.get('_PASSWORD'))
    bot.search(q)
    driver.quit()
    return jsonify(bot.search_to_list)


@app.route('/api/retrieve')
async def retrieve():
    pk = request.args.get('id', 0, int)
    q = request.args.get('q')
    driver = webdriver.Firefox(executable_path=PATH)
    bot = Bot(driver)
    bot.login(_username=os.environ.get('_USERNAME'), _password=os.environ.get('_PASSWORD'))
    searches = bot.search(q)
    bot.exec(searches[pk])
    driver.quit()
    return 'Completed'
