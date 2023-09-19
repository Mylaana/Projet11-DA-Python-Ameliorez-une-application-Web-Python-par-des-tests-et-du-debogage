import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

MAXIMUM_PLACES_BOOKED_PER_CLUB = 12

def loadClubs(returnFullJson=False):
    with open('clubs.json') as c:
        if returnFullJson:
            return json.load(c)
        return json.load(c)['clubs']

def saveClubs(saveclub):
    listOfClubs = loadClubs(True)
    for club in listOfClubs['clubs']:
        if club['name'] == saveclub['name']:
            club.update(saveclub)
            break

    with open('clubs.json', 'w') as c:
        json.dump(listOfClubs, c, indent=4)

def loadCompetitions(returnFullJson=False):
    with open('competitions.json') as comps:
        if returnFullJson:
            return json.load(comps)
        return json.load(comps)['competitions']

def saveCompetitions(saveCompetition):
    listOfCompetitions = loadCompetitions(True)
    for competition in listOfCompetitions['competitions']:
        if competition['name'] == saveCompetition['name']:
            competition.update(saveCompetition)
            break

    with open('competitions.json', 'w') as comps:
        json.dump(listOfCompetitions, comps, indent=4)

def getpointsSummary(clubs):
    pointsSummary = []
    for club in clubs:
        pointsSummary.append(f"{club['name']}: {club['points']}pts")
    return pointsSummary

app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    found_club = None
    for club in clubs:
        if request.form['email'] == club['email']:
            found_club = club
            break

    if found_club is None:
        flash('Please enter a valid email')
        return render_template('index.html')

    return render_template('welcome.html',club=found_club,competitions=competitions,
                           pointsSummary=getpointsSummary(clubs))

@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = None
    foundCompetition = None

    for c in clubs:
        if c['name'] == club:
            foundClub = c
            break

    for comp in competitions:
        if comp['name'] == competition:
            foundCompetition = comp
            break

    if not (foundClub and foundCompetition):
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions,
                               pointsSummary=getpointsSummary(clubs))

    if datetime.now() > datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S"):
        flash("You cannot book places for a past competition.")
        return render_template('welcome.html', club=foundClub, competitions=competitions,
                               pointsSummary=getpointsSummary(clubs))

    return render_template('booking.html',club=foundClub,competition=foundCompetition)

@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # check if not trying to buy negative number of places
    pointsAvailable = int(club['points'])
    if placesRequired < 0:
        flash('You can not book negative number of places !')
        return render_template('welcome.html', club=club, competitions=competitions,
                               pointsSummary=getpointsSummary(clubs))

    # check if club has enough points
    if pointsAvailable < placesRequired:
        flash(f'You only have {pointsAvailable} points !')
        return render_template('welcome.html', club=club, competitions=competitions,
                               pointsSummary=getpointsSummary(clubs))

    # get the number of places already booked by club in selected competition
    alreadyBooked = None
    if 'booked' not in competition:
        competition['booked'] = {club['name']: "0"}
        alreadyBooked = 0

    if club['name'] not in competition['booked']:
        competition['booked'][club['name']] =  "0"
        alreadyBooked = 0

    if alreadyBooked is None:
        alreadyBooked = int(competition['booked'][club['name']])

    if placesRequired + alreadyBooked > MAXIMUM_PLACES_BOOKED_PER_CLUB:
        remaining = MAXIMUM_PLACES_BOOKED_PER_CLUB - alreadyBooked
        flash(f'You can not book more than {MAXIMUM_PLACES_BOOKED_PER_CLUB} total places per competition,'
              f' you already booked {alreadyBooked}, you can book {remaining} additionnal.')
        return render_template('welcome.html', club=club, competitions=competitions,
                               pointsSummary=getpointsSummary(clubs))

    competition['booked'][club['name']] = str(int(competition['booked'][club['name']]) + placesRequired)
    competition['numberOfPlaces'] = str(int(competition['numberOfPlaces'])-placesRequired)
    club['points'] = str(int(club['points']) - placesRequired)
    saveCompetitions(competition)
    saveClubs(club)
    flash('Great-booking complete!')
    return render_template('welcome.html', club=club, competitions=competitions, pointsSummary=getpointsSummary(clubs))

@app.route('/logout')
def logout():
    return redirect(url_for('index'))
