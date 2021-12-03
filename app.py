from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/menumakan'
db = SQLAlchemy(app)

class listmenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    timing = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer)
    status = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<menu %r>' % self.id

class status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<stat %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        menu_content = request.form['content']
        meal_time = request.form['timing']
        menu_score = request.form['score']
        #status = db.select(['status'])
        menu_status = request.form['status']
        #menu_status= select(user_table)
        new_menu = listmenu(content=menu_content, timing=meal_time, score=menu_score, status=menu_status)

        try:
            db.session.add(new_menu)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your menu'

    else:
        menus = listmenu.query.order_by(listmenu.id).all()
        return render_template('index.html', menus=menus)


@app.route('/delete/<int:id>')
def delete(id):
    menu_to_delete = listmenu.query.get_or_404(id)

    try:
        db.session.delete(menu_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that menu'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    menu = listmenu.query.get_or_404(id)

    if request.method == 'POST':
        menu.content = request.form['content']
        menu.timing = request.form['timing']
        menu.score = request.form['score']
        #menu.status = request.form.getlist('status')

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your menu'

    else:
        return render_template('update.html', menu=menu)


####################################################################################
@app.route('/scoring', methods=['GET'])
def scoring():
        menus = listmenu.query.order_by(listmenu.id).all()
        return render_template('scoring.html', menus=menus)

@app.route('/updatescore/<int:id>', methods=['GET', 'POST'])
def updatescore(id):
    menu = listmenu.query.get_or_404(id)

    if request.method == 'POST':
        menu.score = request.form['score']

        try:
            db.session.commit()
            return redirect('/scoring')
        except:
            return 'There was an issue updating your menu'

    else:
        return render_template('score_update.html', menu=menu)

if __name__ == "__main__":
    app.run(debug=True)
