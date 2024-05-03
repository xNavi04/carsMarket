from flask import Flask, request, redirect, url_for, render_template, Response, abort
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_ckeditor import CKEditor
from werkzeug.security import check_password_hash, generate_password_hash
from forms import CreateCars, ChooseBrand, EditProfile
from datetime import datetime
from decorators import adminonly, notlogin
from models import User, Message, FavoriteAdvertisement, Advertisement, Room, ContactMessage, db
from base64 import b64encode
from werkzeug.utils import secure_filename
from utils import sorted_room


app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = "lsakdjflahgiuuyguygiugysdjflk"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cars.db"
db.init_app(app)
CKEditor(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

#########################>>>>>>>>>>>>>>>>>>>> LOGIN PAGE<<<<<<<<<<<#####################################
@app.route("/login", methods=["POST", "GET"])
@notlogin
def loginPage():
    alert = ""
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = db.session.execute(db.Select(User).where(User.email == email)).scalar()
        if email == "" or password == "":
            alert = "Something is empty!"
        elif not user:
            alert = "This user is not exist!"
        elif check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("indexPage"))
        else:
            alert = "Wrong password"
    content = {
        "alert": alert,
        "logged_in": current_user.is_authenticated
    }
    return render_template("login.html", **content)
#########################>>>>>>>>>>>>>>>>>>>> LOGIN PAGE<<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> REGISTER PAGE<<<<<<<<<<<######################################
@app.route("/register", methods=["POST", "GET"])
@notlogin
def registerPage():
    alerts = []
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        user_2 = db.session.execute(db.select(User).where(User.username == username)).scalar()
        if user or user_2:
            alerts.append("This user is already exist!")
        elif password != confirmPassword:
            alerts.append("Password do not match!")
        elif username == "" or email == "" or password == "":
            alerts.append("Something is empty!")
        elif not "@" in email:
            alerts.append("Email is wrong!")
        else:
            hashPassword = generate_password_hash(password, salt_length=8)
            new_user = User(username=username,
                            email=email,
                            password=hashPassword)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for("indexPage"))
    return render_template("register.html", alerts=alerts, logged_in=current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> REGISTER PAGE<<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> LOGOUT PAGE<<<<<<<<<<<######################################
@app.route("/logout")
@login_required
def logoutPage():
    logout_user()
    return redirect(url_for("indexPage"))

@app.route("/chat")
@login_required
def chatFind():
    rooms = db.session.execute(db.select(Room).where(Room.participants.contains(current_user))).scalars().all()
    rooms = sorted_room(rooms)

    content = {
        "rooms": rooms,
        "logged_in": current_user.is_authenticated,
        "b64encode": b64encode
    }
    return render_template("chooseChat.html", **content)
#########################>>>>>>>>>>>>>>>>>>>> LOGOUT PAGE<<<<<<<<<<<######################################
@app.route("/")
def indexPage():
    content = {
        "logged_in": current_user.is_authenticated
    }
    return render_template("index.html", **content)

#########################>>>>>>>>>>>>>>>>>>>> PRODUCTS PAGE <<<<<<<<<<<######################################
@app.route("/cars", methods=["POST", "GET"])
def carsPage():
    form = ChooseBrand()
    if form.validate_on_submit():
        advertisements = db.session.execute(db.select(Advertisement).where(Advertisement.brand == form.brand.data, Advertisement.verified == 1)).scalars().all()
    else:
        advertisements = db.session.execute(db.select(Advertisement).where(Advertisement.verified == 1)).scalars().all()
    return render_template("cars.html", logged_in=current_user.is_authenticated, advertisements=advertisements, b64encode=b64encode, form=form)
#########################>>>>>>>>>>>>>>>>>>>> PRODUCTS PAGE <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> ADD ADVERTISEMENT <<<<<<<<<<<######################################
@app.route("/addAdvertisement", methods=["GET", "POST"])
@login_required
def addAdvertisement():
    form = CreateCars()
    if form.validate_on_submit():
        file = form.file.data
        new_advertisement = Advertisement(name=form.name.data,
                                          brand=form.brand.data,
                                          description=form.description.data,
                                          data=datetime.now().strftime("%Y - %m - %d"),
                                          image_name=secure_filename(file.filename),
                                          image=file.read(),
                                          image_mimetype=file.mimetype,
                                          owner=current_user,
                                          price=form.price.data,
                                          number=form.phone.data,
                                          verified=0,
                                          blocked=0)
        db.session.add(new_advertisement)
        db.session.commit()
        return redirect(url_for("indexPage"))
    content = {
        "form": form,
        "logged_in": current_user.is_authenticated
    }
    return render_template("addCars.html", **content)
#########################>>>>>>>>>>>>>>>>>>>> ADD ADVERTISEMENT <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> CONFIRM ADVERTISEMENT BY ADMIN <<<<<<<<<<<######################################
@app.route("/confirmAdv")
@adminonly
def confirmAdv():
    content = {
        "advertisements": db.session.execute(db.select(Advertisement)).scalars().all(),
        "logged_in": current_user.is_authenticated
    }
    return render_template("confirmAdv.html", **content)
#########################>>>>>>>>>>>>>>>>>>>> CONFIRM ADVERTISEMENT BY ADMIN <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> CHECK IMAGE <<<<<<<<<<<######################################
@app.route("/checkImage/<int:num>")
@adminonly
def checkImage(num):
    advertisement = db.get_or_404(Advertisement, num)
    content = {
        "mimetype": advertisement.image_mimetype
    }
    return Response(advertisement.image, **content)
#########################>>>>>>>>>>>>>>>>>>>> CHECK IMAGE <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> MANAGE ADVERTISEMENTS <<<<<<<<<<<######################################
@app.route("/allowAdv/<int:num>")
@adminonly
def allowAdv(num):
    advertisement = db.get_or_404(Advertisement, num)
    advertisement.verified = 1
    db.session.commit()
    return redirect(url_for("confirmAdv"))

@app.route("/allowAdv/<int:num>")
@adminonly
def denyAdv(num):
    advertisement = db.get_or_404(Advertisement, num)
    db.session.delete(advertisement)
    db.session.commit()
    return redirect(url_for("confirmAdv"))

@app.route("/allowAdvm/<int:num>")
@adminonly
def denyAdvm(num):
    favoriteAdvertisements = db.session.execute(
        db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.advertisement_id == num)).scalars().all()
    for favoriteAdvertisement in favoriteAdvertisements:
        db.session.delete(favoriteAdvertisement)
        db.session.commit()
    advertisement = db.get_or_404(Advertisement, num)
    db.session.delete(advertisement)
    db.session.commit()
    return redirect(url_for("manageAdv"))

@app.route("/blockAdv/<int:num>")
@adminonly
def blockAdv(num):
    advertisement = db.get_or_404(Advertisement, num)
    advertisement.blocked = 1
    db.session.commit()
    return redirect(url_for("manageAdv"))

@app.route("/unblockAdv<int:num>")
@adminonly
def unblockAdv(num):
    advertisement = db.get_or_404(Advertisement, num)
    advertisement.blocked = 0
    db.session.commit()
    return redirect(url_for("manageAdv"))


@app.route("/manageAdv")
@adminonly
def manageAdv():
    advertisements = db.session.execute(db.Select(Advertisement).where(Advertisement.verified == 1)).scalars().all()
    return render_template("manageAdv.html", advertisements=advertisements, logged_in=current_user.is_authenticated)

@app.route("/addToFavorites/<int:num>")
@login_required
def addToFavorites(num):
    favoriteCars = db.session.execute(db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.user_id == current_user.id)).scalars().all()
    for favoriteCar in favoriteCars:
        if favoriteCar.advertisement_id == num:
            return redirect(url_for("favoriteCars"))
    advertisement = db.get_or_404(Advertisement, num)
    newfavoriteAdvertisement = FavoriteAdvertisement(owner=current_user, advertisement=advertisement)
    db.session.add(newfavoriteAdvertisement)
    db.session.commit()
    return redirect(url_for("favoriteCars"))


@app.route("/deleteFromFavorites/<int:num>")
@login_required
def deleteFromFavorites(num):
    favoriteCar = db.session.execute(db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.advertisement_id == num, FavoriteAdvertisement.user_id == current_user.id)).scalar()
    db.session.delete(favoriteCar)
    db.session.commit()
    return redirect(url_for("favoriteCars"))
#########################>>>>>>>>>>>>>>>>>>>> MANAGE ADVERTISEMENTS <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> ONE PRODUCT PAGE <<<<<<<<<<<######################################
@app.route("/car/<int:num>")
def oneProduct(num):
    advertisement = db.get_or_404(Advertisement, num)
    try:
        if db.session.execute(db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.user_id == current_user.id, FavoriteAdvertisement.advertisement_id == num)).scalar():
            favorite = 1
        else:
            favorite = 0
    except Exception:
        favorite = 2
    return render_template("oneProduct.html", logged_in=current_user.is_authenticated, advertisement=advertisement, b64encode=b64encode, favorite=favorite)
#########################>>>>>>>>>>>>>>>>>>>> ONE PRODUCT PAGE <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> FAVORITES CARS PAGE <<<<<<<<<<<######################################
@app.route("/favoriteCars")
@login_required
def favoriteCars():
    advertisements = db.session.execute(db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.user_id == current_user.id)).scalars().all()
    for advertisement in advertisements:
        if advertisement.advertisement.blocked == 1:
            advertisements.remove(advertisement)
    return render_template("favoritesCar.html", advertisements=advertisements, b64encode=b64encode, logged_in=current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> FAVORITES CARS PAGE <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> CHAT PAGE <<<<<<<<<<<######################################
@app.route("/chat/<int:num>", methods=["POST", "GET"])
@login_required
def chatPage(num):
    if current_user.id == num:
        return abort(404)
    host = db.get_or_404(User, num)
    room = db.session.execute(db.select(Room).where(Room.participants.contains(current_user), Room.participants.contains(host))).scalar()
    if not room:
        room = Room(participants=[current_user, host])
        db.session.add(room)
        db.session.commit()
    if request.method == "POST":
        x = request.form["chat"]
        date = datetime.now()
        message = Message(room=room, sender=current_user, text=x, date=date)
        db.session.add(message)
        db.session.commit()

    rooms = db.session.execute(db.select(Room).where(Room.participants.contains(current_user))).scalars().all()
    rooms = sorted_room(rooms)

    foreign_user = None

    for user in room.participants:
        if user.id != current_user.id:
            foreign_user = user

    context = {
        "b64encode": b64encode,
        "foreign_user": foreign_user,
        "rooms": rooms,
        "logged_in": current_user.is_authenticated,
        "room": room
    }
    return render_template("chat.html", **context)

@app.route("/deleteChat/<int:num>")
@login_required
def deleteChat(num):
    room = db.session.execute(db.select(Room).where(Room.participants.contains(current_user),
                                                    Room.participants.contains(db.get_or_404(User, num)))).scalar()
    messages = db.session.execute(db.select(Message).where(Message.room == room)).scalars().all()
    for message in messages:
        db.session.delete(message)
    db.session.commit()
    if room:
        db.session.delete(room)
        db.session.commit()
    return redirect(url_for("chatFind"))

@app.route("/deleteMessage/<int:num>")
@login_required
def deleteMessage(num):
    message = db.session.execute(db.select(Message).where(Message.id == num)).scalar()
    if message.sender_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
        return redirect(request.referrer)
    else:
        return redirect(url_for("indexPage"))
#########################>>>>>>>>>>>>>>>>>>>> CHAT PAGE <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> CONTACT PAGE <<<<<<<<<<<######################################
@app.route("/contact", methods=["POST", "GET"])
def contact():
    alerts = []
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]
        if name == "" or email == "" or subject == "" or message == "":
            alerts.append("Something is empty!")
        elif "@" not in email:
            alerts.append("Wrong email!")
        else:
            new_contactMessage = ContactMessage(name=name, email=email, subject=subject, message=message)
            db.session.add(new_contactMessage)
            db.session.commit()

    return render_template("contact.html", alerts=alerts, logged_in = current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> CONTACT PAGE <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> EDIT PROFILE <<<<<<<<<<<######################################
@app.route("/edit_profile", methods=["POST", "GET"])
@login_required
def editProfile():
    user = db.get_or_404(User, current_user.id)
    form = EditProfile(username=current_user.username, email=current_user.email)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        file = form.file.data
        if file:
            user.image = file.read()
            user.image_mimetype = file.mimetype
        db.session.commit()
    return render_template("edit_user.html", logged_in = current_user.is_authenticated, form=form)
#########################>>>>>>>>>>>>>>>>>>>> EDIT PROFILE <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> DELETE ADVERTISEMENT <<<<<<<<<<<######################################
@app.route("/deleteAdvertisement/<int:num>")
def deleteAdvertisement(num):
    advertisement = db.session.execute(db.select(Advertisement).where(Advertisement.id == num)).scalar()
    if advertisement.owner == current_user:
        db.session.delete(advertisement)
        db.session.commit()
        return redirect(url_for("carsPage"))
#########################>>>>>>>>>>>>>>>>>>>> DELETE ADVERTISEMENT <<<<<<<<<<<######################################

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int("3000"), debug=True)

