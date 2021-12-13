from flask import Flask, render_template, url_for, request, redirect, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import csv
from io import TextIOWrapper
from io import StringIO
import io

app = Flask(__name__)

#database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db' #connect ke local directory
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/menumakan' #connect ke local server
db = SQLAlchemy(app)

class listmenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    timing = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer)
    status = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<menu %r>' % self.id

###############################################################
#INPUT menu through form
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        menu_content = request.form['content']
        meal_time = request.form['timing']
        menu_score = request.form['score']
        menu_status = request.form['status']
        
        new_menu = listmenu(content=menu_content, timing=meal_time, score=menu_score, status=menu_status)

        try:
            db.session.add(new_menu)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your menu'

#Read menu from database
    else:
        menus = listmenu.query.order_by(listmenu.id).all()
        return render_template('index.html', menus=menus)

###############################################################
#READ menu from file then INPUT/insert to database
@app.route('/uploadfiles', methods=['POST', 'GET'])
# Get the uploaded files
def uploadfiles():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        next(csv_reader)
        for row in csv_reader:
            new_menu = listmenu(content=row[0], timing=row[1], score=row[2], status=row[3])
            db.session.add(new_menu)
            db.session.commit()
        return redirect('/')
    return render_template('index.html')

################################################################
# DELETE menu
@app.route('/delete/<int:id>')
def delete(id):
    menu_to_delete = listmenu.query.get_or_404(id)

    try:
        db.session.delete(menu_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that menu'

###############################################################
#UPDATE menu
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    menu = listmenu.query.get_or_404(id)

    if request.method == 'POST':
        menu.content = request.form['content']
        menu.timing = request.form['timing']
        #menu.score = request.form['score']
        menu.status = request.form['status']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your menu'

    else:
        return render_template('update.html', menu=menu)

####################################################################################
#COMBINE through scoring and restore it into a database
@app.route('/scoring', methods=['GET'])
def scoring():
        menus = listmenu.query.filter_by(status = 'Active').all()
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

########################################################################
#Report
@app.route('/report')
def report():
    menus = listmenu.query.order_by(listmenu.id).all()
    return render_template('report.html', menus=menus)

########################################################################
#WRITE database into a file
@app.route('/download')
def download():
    menu = db.session.query(listmenu.id, listmenu.content, listmenu.timing, listmenu.score, listmenu.status)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    line=['id', 'menu', 'timing', 'score', 'status']
    #line = ['id, menu, timing, score, status'] #header pakai koma
    writer.writerow(line)
    
    for row in menu:
        writer.writerow(row)
    
    output.seek(0)
    
    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=data_makan.csv"})

if __name__ == "__main__":
    app.run(debug=True)
