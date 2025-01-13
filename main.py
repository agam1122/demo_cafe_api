import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes_new.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


# Error Handling > Boolean form values:
def str_to_bool(string):
    """
    It receives a string, check if the string is a valid positive answer and return the result. This function goal is
    to make the dev life easier, basically during form tests.
    :param string: the text.
    :return: bool
    """
    if string in ["1", "YES", "Yes", "yes", "Y", "y", "TRUE", "True", "true", "T", "t"]:
        return True
    return False


# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    random_cafe = random.choice(all_cafes)
    random_cafe_dict = {'id': random_cafe.id,
                        'name': random_cafe.name,
                        'map_url': random_cafe.map_url,
                        'img_url': random_cafe.img_url,
                        'location': random_cafe.location,
                        'seats': random_cafe.seats,
                        'has_toilet': random_cafe.has_toilet,
                        'has_wifi': random_cafe.has_wifi,
                        'has_sockets': random_cafe.has_sockets,
                        'can_take_calls': random_cafe.can_take_calls,
                        'coffee_price': random_cafe.coffee_price}
    return jsonify(random_cafe_dict)


@app.route("/all")
def get_all_cafes():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.id))
    all_cafes = result.scalars().all()
    all_cafes_dict = {}
    # i = 0
    # for cafe in all_cafes:
    #     # cafe_dict = {'id': cafe.id,
    #     #              'name': cafe.name,
    #     #              'map_url': cafe.map_url,
    #     #              'img_url': cafe.img_url,
    #     #              'location': cafe.location,
    #     #              'seats': cafe.seats,
    #     #              'has_toilet': cafe.has_toilet,
    #     #              'has_wifi': cafe.has_wifi,
    #     #              'has_sockets': cafe.has_sockets,
    #     #              'can_take_calls': cafe.can_take_calls,
    #     #              'coffee_price': cafe.coffee_price}
    #     # all_cafes_dict[i] = cafe_dict
    #     all_cafes_dict[i] = cafe.to_dict()
    #     i = i + 1

    # all_cafes_dict = [{'id': cafe.id,
    #                    'name': cafe.name,
    #                    'map_url': cafe.map_url,
    #                    'img_url': cafe.img_url,
    #                    'location': cafe.location,
    #                    'seats': cafe.seats,
    #                    'has_toilet': cafe.has_toilet,
    #                    'has_wifi': cafe.has_wifi,
    #                    'has_sockets': cafe.has_sockets,
    #                    'can_take_calls': cafe.can_take_calls,
    #                    'coffee_price': cafe.coffee_price} for cafe in all_cafes]

    all_cafes_dict = [cafe.to_dict() for cafe in all_cafes]

    return jsonify(all_cafes_dict)


@app.route("/search")
def search_cafe():
    query_location = request.args.get('loc')
    result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
    all_cafes_at_loc = result.scalars().all()

    all_cafes_at_loc_json = [cafe.to_dict() for cafe in all_cafes_at_loc]

    if all_cafes_at_loc:
        return jsonify(all_cafes_at_loc_json)
    else:
        error_dict = {
            "error": {
                "Not Found": "Sorry, we don't have a cafe at that location."
            }
        }
        return jsonify(error_dict)


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def post_new_cafe():
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        if request.method == "POST":
            new_cafe = Cafe(
                name=request.form.get("name"),
                map_url=request.form.get("map_url"),
                img_url=request.form.get("img_url"),
                location=request.form.get("location"),
                has_sockets=bool(request.form.get("has_sockets")),
                has_toilet=bool(request.form.get("has_toilet")),
                has_wifi=bool(request.form.get("has_wifi")),
                can_take_calls=bool(request.form.get("can_take_calls")),
                seats=request.form.get("seats"),
                coffee_price=request.form.get("coffee_price"),
            )
            db.session.add(new_cafe)
            db.session.commit()
            return jsonify(response={"success": "Successfully added the new cafe."})
    return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    if request.method == "PATCH":
        new_price = request.args.get("new_price")
        # data_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == cafe_id))  #this line is not working
        data_to_update = db.get_or_404(Cafe, cafe_id)
        data_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."})
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."})


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == "TopSecretAPIKey":
        cafe_to_delete = db.get_or_404(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
        else:
            return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404
    else:
        return jsonify(error={"Forbidden": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


if __name__ == '__main__':
    app.run(debug=True)
