from flask import *
import random,string
import os 
import smtplib
from yt_iframe import yt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from lightdb import LightDB
from flask_hcaptcha import hCaptcha
db = LightDB('users.json')
verification = LightDB('verification.json')
courss = LightDB("cours.json")
app = Flask('')
app.config['UPLOAD_FOLDER'] = "/templates/"
app.config['HCAPTCHA_SITE_KEY'] = "ce48fba4-b515-4662-a6f5-03ba75ebee87"
app.config['HCAPTCHA_SECRET_KEY'] = "0x3e0630C82e46143Eb1Bbc76D58698a43ca7BD9f4"
mats = ["AR","FR","ANG","ED.ISL","H.G","MATHS","PC","SVT","INF"]
hcaptcha = hCaptcha(app)

def listemails():
    for key in db.keys():
        emails = []
        emails.append(db.get(key).get('email'))
        return emails
print(listemails())
def getTokenwithemail(email):
    for key in db.keys():
        if email in listemails():
            if db.get(key).get('email') == email:
                d = db.get(key)
                d['token'] = key
                return d
        else:
            return 400

@app.route('/')
def home():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template("login.html")
    else:
        return render_template('index.html',username=db.get(request.headers.get('cookie').split('=')[1]).get('username'))
@app.route('/calendrier')
def calendrier():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template("login.html")
    else:
        return render_template('calendrier.html',username=db.get(request.headers.get('cookie').split('=')[1]).get('username'))
@app.route('/cours')
def cours():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template("login.html")
    else:
        return render_template('cours.html',username=db.get(request.headers.get('cookie').split('=')[1]).get('username'))
@app.route('/devoirs')
def devoirs():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template("login.html")
    else:
        return render_template('devoirs.html',username=db.get(request.headers.get('cookie').split('=')[1]).get('username'))
@app.route('/api/login')
def login():
    info = getTokenwithemail(request.args.get('email'))
    if info == 400:
        return render_template("error_handler.html",error="Aucun compte avec cet e-mail n'a été trouvé!")
    else:
        if info.get('password') == request.args.get('password'):
            code = info.get('email')
            response = ""
            for n in range(6):
                response += random.choice(string.digits)
            verification.set(code,{"token":info.get('token'),"verification_response":response})
            s = smtplib.SMTP('smtp-mail.outlook.com', 587)
            s.ehlo()
            s.starttls()
            s.login('afifwassim2023@outlook.com','thetawamb5/')
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Le code de vérification"
            msg['From'] = "afifwassim2023@outlook.com"
            msg['To'] = info.get('email')
            text = f"""\
            <h1>Cher, utilisateur</h1>
            <p>Pour accedez à votre compte, vous devez saisir le code suivant :</>
            <p style="color:green">{response}</p>
            """
            part1 = MIMEText(text, 'html')
            msg.attach(part1)
            s.sendmail("afifwassim@programmer.net", info.get('email'), msg.as_string())
            return render_template('verify.html',verification_code=code)
        else:
            return render_template("error_handler.html",error="Mot de passe incorrect!")
@app.route('/verify')
def verify():
    if request.args.get('email') != None and request.args.get('verification_response') != None:
        verification_code = request.args.get('email')
        verification_response = request.args.get('verification_response')
        token = verification.get(verification_code).get('token')
        if verification.get(verification_code).get('verification_response') == verification_response:
            verification.pop(verification_code)
            return render_template("l.html",token=token)
    else:
        return render_template('error_handler_v.html',error="Code de vérification invalide! Veuillez réessayer")
@app.route('/api/role')
def role():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return "HTTP ERROR 400: UNAUTH",400
    else:
        return db.get(request.headers.get('cookie').split('=')[1]).get('role')
    return role
@app.route('/upload',methods=['GET'])
def upload():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template('login.html')
    else:
        if True:
            if db.get(request.headers.get('cookie').split('=')[1]).get('role') == "admin":
                code = """
                <script>
                alert("Cour ajoutiez!")
                </script>
                """
                courss.set(request.args.get('title').replace(' ','-'),{"mat":request.args.get('mat'),"video_url":request.args.get('video_url'),"pdf_url":request.args.get('pdf')})
                return redirect('/cours')
        else:
            return "HCAPTCHA Code n'est pas correct!"
@app.route('/voir_cour')
def c():
    if request.headers.get('cookie') == None or request.headers.get('cookie').split('=')[1] not in db.keys():
        return render_template('login.html')
    else:
        name = request.args.get("name")
        mat = request.args.get("mat")   
        pdf = courss.get(name).get('pdf_url')
        url =  courss.get(name).get('video_url')
        width = '900' 
        height = '520' 
        iframe = yt.video(url, width=width, height=height)
        return render_template("cour.html",title=name,date=courss.get(name).get('date'),mat=mat,embed_video=str(iframe),pdf_url=pdf,username=db.get(request.headers.get('cookie').split('=')[1]).get('username'))
@app.route('/<mat>/<name>')
def r(mat,name):
    return send_file(f"./templates/{mat}/{name}")
@app.route('/list_cours/<mat>')
def l(mat):
    global mats
    cours_ = ""
    if mat in mats:
        for key in courss.keys():
            print(key)
            if courss.get(key).get('mat') == mat:
                link = f"/voir_cour?mat={mat}&name={key}"
                code = f'<a href="{link}">• {key}</a>'
                print(code)
                cours_ += code +"<br>\n"
        return {"list":cours_}
    else:
        return "not found!"
@app.route('/ajoutez')
def ajoutez():
    if request.headers.get('cookie') != None or request.headers.get('cookie').split('=')[1] in db.keys():
        if db.get(request.headers.get('cookie').split('=')[1]).get('role') == "admin":
            return render_template("ajoutez.html")
        else:
            return "<script>alert('Vous n'avez pas la permission d'accéder à cette page!')"
    else:
        return render_template('login.html')
app.run(port=8080)