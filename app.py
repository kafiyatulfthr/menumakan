from MySQLdb.cursors import Cursor
from flask import Flask, render_template, url_for, request, redirect, make_response, Response
from flask_sqlalchemy import SQLAlchemy
import csv
from io import TextIOWrapper
from io import StringIO
import io

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

def transform(text_file_contents):
    return text_file_contents.replace("=", ",")

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

    else:
        menus = listmenu.query.order_by(listmenu.id).all()
        return render_template('index.html', menus=menus)

###############################################################
@app.route('/uploadfiles', methods=['POST', 'GET'])
# Get the uploaded files
def uploadfiles():
    if request.method == 'POST':
        csv_file = request.files['file']
        csv_file = TextIOWrapper(csv_file, encoding='utf-8')
        csv_reader = csv.reader(csv_file, delimiter=',')
        for row in csv_reader:
            new_menu = listmenu(content=row[0], timing=row[1], score=row[2], status=row[3])
            db.session.add(new_menu)
            db.session.commit()
        return redirect('/')
    return render_template('upload-files.html')
################################################################

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
        menu.status = request.form['status']

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
#Download Report to CSV
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
