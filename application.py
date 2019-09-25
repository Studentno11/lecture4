from flask import Flask, render_template, request, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os

app = Flask('Kititpat')
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("index.html", flights=flights)

@app.route('/book', methods=["POST"])
def book():
    name = request.form.get("name")
    try:
        flight_id = int(request.form.get("flight_id"))
    except ValueError:
        return render_template("error.html", message="Invalid flight number.")
    if db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).rowcount == 0:
        return render_template("error.html", message="No such flight with that id.")
    db.execute("INSERT INTO passengers (name, flight_id) VALUES (:name, :flight_id)",
                {"name": name, "flight_id": flight_id})
    db.commit()
    return render_template("success.html")

@app.route('/flights')
def flights():
    """List all flights."""
    flights = db.execute("SELECT * FROM flights").fetchall()
    return render_template("flights.html", flights=flights)

@app.route('/flights/<int:flight_id>')
def flight(flight_id):
    """List details about a single flight."""
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        return render_template("error.html", message="No such flgiht.")
    
    passengers = db.execute("SELECT name FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    return render_template("flight.html", flight=flight, passengers=passengers)

@app.route('/api/flights/<int:flight_id>')
def flight_api(flight_id):

    # Make sure flight exists.
    flight = db.execute("SELECT * FROM flights WHERE id = :id", {"id": flight_id}).fetchone()
    if flight is None:
        return jsonify({"error": "Invalid flight_id"}), 422
    
    # Get all passengers.
    passengers = db.execute("SELECT * FROM passengers WHERE flight_id = :flight_id",
                            {"flight_id": flight_id}).fetchall()
    names = []
    for passenger in passengers:
        names.append(passenger.name)
    return jsonify({
        "origin": flight.origin,
        "destination": flight.destination,
        "duration": flight.duration,
        "passengers": names
    })