from flask import Flask, render_template, request, redirect, url_for, abort, Response, flash, session
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from forms import CreateCars, ChooseBrand
from base64 import b64encode
from datetime import datetime
from functools import wraps
from flask_ckeditor import CKEditor
from sqlalchemy import or_, and_



app = Flask(__name__)
Bootstrap5(app)
app.config['SECRET_KEY'] = "adfa789y6789dsagfghjkdf"
#app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///posts.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://xNavi04:telefon04@database-1.cdq5bzc5st5i.eu-north-1.rds.amazonaws.com:5432/"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
CKEditor(app)
login_manager = LoginManager(app)
login_manager.init_app(app)


#########################>>>>>>>>>>>>>>>>>>>> DECORATORS <<<<<<<<<<<######################################
def notlogin(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return f(*args, **kwargs)
        else:
            return abort(404)
    return decorator_function

def adminonly(f):
    @wraps(f)
    def decorator_function(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(404)
    return decorator_function

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)
#########################>>>>>>>>>>>>>>>>>>>> DECORATORS <<<<<<<<<<<######################################







#########################>>>>>>>>>>>>>>>>>>>> DATABASE <<<<<<<<<<<######################################
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    advertisements = db.relationship("Advertisement", back_populates="owner")
    favoriteAdvertisements = db.relationship("FavoriteAdvertisement", back_populates="owner")
    rooms_owner = db.relationship("Room", back_populates="owner", foreign_keys="Room.owner_id")
    rooms_host = db.relationship("Room", back_populates="host_user", foreign_keys="Room.user_id")
    messages = db.relationship("Message", back_populates="owner")

class Advertisement(db.Model):
    __tablename__ = "advertisement"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    brand = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)
    image_name = db.Column(db.String, nullable=False)
    image = db.Column(db.String, nullable=False)
    image_mimetype = db.Column(db.String, nullable=False)
    price = db.Column(db.String, nullable=False)
    verified = db.Column(db.Integer, nullable=False)
    blocked = db.Column(db.Integer, nullable=False)
    number = db.Column(db.Integer, nullable=False)

    owner = db.relationship("User", back_populates="advertisements")
    favoriteAdvertisements = db.relationship("FavoriteAdvertisement", back_populates="advertisement")

class FavoriteAdvertisement(db.Model):
    __tablename__ = "favoriteAdvertisements"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    advertisement_id = db.Column(db.Integer, db.ForeignKey("advertisement.id"))
    owner = db.relationship("User", back_populates="favoriteAdvertisements")
    advertisement = db.relationship("Advertisement", back_populates="favoriteAdvertisements")

class Room(db.Model):
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    owner = db.relationship("User", back_populates="rooms_owner", foreign_keys=[owner_id])
    host_user = db.relationship("User", back_populates="rooms_host", foreign_keys=[user_id])
    data = db.Column(db.String, nullable=False)
    messages = db.relationship("Message", back_populates="room")

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"))
    context = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)
    owner = db.relationship("User", back_populates="messages")
    room = db.relationship("Room", back_populates="messages")

with app.app_context():
    db.create_all()
#########################>>>>>>>>>>>>>>>>>>>> DATABASE <<<<<<<<<<<######################################




#########################>>>>>>>>>>>>>>>>>>>> HOME PAGE <<<<<<<<<<<######################################


@app.route("/")
def indexPage():
    return render_template("index.html", logged_in=current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> HOME PAGE <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> LOGIN PAGE<<<<<<<<<<<######################################
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
    return render_template("login.html", logged_in=current_user.is_authenticated, alert=alert)
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
        else:
            hashPassword = generate_password_hash(password, salt_length=8)
            new_user = User(username=username, email=email, password=hashPassword)
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
#########################>>>>>>>>>>>>>>>>>>>> LOGOUT PAGE<<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> PRODUCTS PAGE <<<<<<<<<<<######################################
@app.route("/cars", methods=["POST", "GET"])
def carsPage():
    form = ChooseBrand()
    if form.validate_on_submit():
        print(form.brand.data)
        advertisements = db.session.execute(db.select(Advertisement).where(Advertisement.brand == form.brand.data, Advertisement.verified == 1)).scalars().all()
        return render_template("cars.html", logged_in=current_user.is_authenticated, advertisements=advertisements, b64encode=b64encode, form=form)
    advertisements = db.session.execute(db.select(Advertisement).where(Advertisement.verified == 1)).scalars().all()
    return render_template("cars.html", logged_in=current_user.is_authenticated, advertisements=advertisements, b64encode=b64encode, form=form)
#########################>>>>>>>>>>>>>>>>>>>> PRODUCTS PAGE <<<<<<<<<<<######################################




#########################>>>>>>>>>>>>>>>>>>>> ADD ADVERTISEMENT <<<<<<<<<<<######################################
@app.route("/addAdvertisement", methods=["GET", "POST"])
@login_required
def addAdvertisement():
    form = CreateCars()
    if form.validate_on_submit():
        brand = form.brand.data
        name = form.name.data
        description = form.description.data
        file = form.file.data
        price = form.price.data
        filename = secure_filename(file.filename)
        mimetype = file.mimetype
        image = file.read()
        number = form.phone.data
        new_advertisement = Advertisement(name=name, brand=brand, description=description, data=datetime.now().strftime("%Y - %m - %d"), image_name=filename, image=image, image_mimetype=mimetype, owner=current_user, price=price, number=number, verified=0, blocked=0)
        db.session.add(new_advertisement)
        db.session.commit()
        return redirect(url_for("indexPage"))
    return render_template("searchCar.html", form=form, logged_in=current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> ADD ADVERTISEMENT <<<<<<<<<<<######################################


#########################>>>>>>>>>>>>>>>>>>>> CONFIRM ADVERTISEMENT BY ADMIN <<<<<<<<<<<######################################
@app.route("/confirmAdv")
@adminonly
def confirmAdv():
    addvertisements = db.session.execute(db.select(Advertisement)).scalars().all()
    return render_template("confirmAdv.html", advertisements=addvertisements, logged_in=current_user.is_authenticated)
#########################>>>>>>>>>>>>>>>>>>>> CONFIRM ADVERTISEMENT BY ADMIN <<<<<<<<<<<######################################



#########################>>>>>>>>>>>>>>>>>>>> CHECK IMAGE <<<<<<<<<<<######################################
@app.route("/checkImage/<int:num>")
@adminonly
def checkImage(num):
    advertisement = db.get_or_404(Advertisement, num)
    return Response(advertisement.image, mimetype=advertisement.image_mimetype)
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
    favoriteAdvertisements = db.session.execute(db.select(FavoriteAdvertisement).where(FavoriteAdvertisement.advertisement_id == num)).scalars().all()
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
    print(num)
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
def createChat(num):
    if current_user.id == num:
        return abort(404)
    room = db.session.execute(db.select(Room).where(Room.owner_id == current_user.id, Room.user_id == num)).scalar()
    if room:
        print("1")
        if request.method == "POST":
            chat = request.form["chat"]
            if chat != "":
                print(f"room0: {room}")
                new_message = Message(room=room, owner=current_user, context=chat, data=datetime.now().strftime("%H:%M  %A"))
                db.session.add(new_message)
                db.session.commit()
            return redirect(url_for("createChat", num=num))
        rooms = db.session.execute(db.select(Room)).scalars().all()
        users = []
        for room in rooms:
            if room.owner.id == current_user.id or room.host_user.id == current_user.id:
                user = db.session.execute(db.select(User).where(User.id == room.owner.id)).scalar_one()
                if user not in users and user.id is not current_user.id:
                    users.append(user)
                user = db.session.execute(db.select(User).where(User.id == room.host_user.id)).scalar_one()
                if user not in users and user.id is not current_user.id:
                    users.append(user)
        room = db.session.execute(db.select(Room).where(Room.owner_id == current_user.id, Room.user_id == num)).scalar()
        amount_users = len(room.messages)
        return render_template("chat.html", messages=room.messages, users=users, logged_in=current_user.id, foreign_user=room.host_user, amount_users=amount_users)
    room = db.session.execute(db.select(Room).where(Room.owner_id == num, Room.user_id == current_user.id)).scalar()
    if room:
        print("2")
        if request.method == "POST":
            chat = request.form["chat"]
            if chat != "":
                print(f"room: {room}")
                new_message = Message(room=room, owner=current_user, context=chat, data=datetime.now().strftime("%H:%M  %A"))
                db.session.add(new_message)
                db.session.commit()
            return redirect(url_for("createChat", num=num))
        rooms = db.session.execute(db.select(Room)).scalars().all()
        users = []
        for room in rooms:
            if room.owner.id == current_user.id or room.host_user.id == current_user.id:
                user = db.session.execute(db.select(User).where(User.id == room.owner.id)).scalar_one()
                if user not in users and user.id is not current_user.id:
                    users.append(user)
                user = db.session.execute(db.select(User).where(User.id == room.host_user.id)).scalar_one()
                if user not in users and user.id is not current_user.id:
                    users.append(user)
        room = db.session.execute(db.select(Room).where(Room.owner_id == num, Room.user_id == current_user.id)).scalar()
        amount_users = len(room.messages)
        return render_template("chat.html", messages=room.messages, users=users, logged_in=current_user.id, foreign_user=room.owner, amount_users=amount_users)
    host_user = db.get_or_404(User, num)
    print("to")
    new_room = Room(owner=current_user, host_user=host_user, data="adsf")
    db.session.add(new_room)
    db.session.commit()
    return redirect(url_for("createChat", num=num))

@app.route("/deleteChat/<int:num>")
def deleteChat(num):
    room = Room.query.filter(
        or_(
            and_(Room.owner_id == num, Room.user_id == current_user.id),
            and_(Room.owner_id == current_user.id, Room.user_id == num)
        )
    ).first()
    if room:
        db.session.delete(room)
        db.session.commit()
        return redirect(url_for("indexPage"))
    else:
        return abort(404)

@app.route("/chat")
def chat():
    room = Room.query.filter(
        or_(
            and_(Room.owner_id == current_user.id),
            and_(Room.user_id == current_user.id)
        )
    ).order_by(Room.id.desc()).first()
    print(room)
    try:
        if current_user.id == room.owner_id:
            return redirect(url_for("createChat", num=room.user_id))
        elif current_user.id == room.user_id:
            return redirect(url_for("createChat", num=room.owner_id))
        else:
            return abort(404)
    except Exception:
        return render_template("Error.html")


@app.route("/deleteMessage/<int:num>/<int:userId>")
def deleteMessage(num, userId):
    message = db.session.execute(db.select(Message).where(Message.id == num)).scalar()
    if message.owner_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
        return redirect(url_for("createChat", num=userId))
    else:
        return redirect(url_for("indexPage"))
#########################>>>>>>>>>>>>>>>>>>>> CHAT PAGE <<<<<<<<<<<######################################



@app.route("/contact")
def contact():
    return render_template("chat.html")



if __name__ == "__main__":
    app.run(debug=True)