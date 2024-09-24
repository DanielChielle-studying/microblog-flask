from flask import render_template
from app import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Daniel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Foz do Iguaçu'
        },
        {
            'author': {'username': 'Gabriel'},
            'body': 'I really like Flask'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)