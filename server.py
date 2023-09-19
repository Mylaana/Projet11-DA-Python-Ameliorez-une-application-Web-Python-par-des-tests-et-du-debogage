import json
from flask import Flask,render_template,request,redirect,flash,url_for

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


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/showSummary',methods=['POST'])
def showSummary():
    club = [club for club in clubs if club['email'] == request.form['email']][0]
    return render_template('welcome.html',club=club,competitions=competitions)


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces',methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])

    # check if not trying to buy negative number of places
    pointsAvailable = int(club['points'])
    if placesRequired < 0:
        flash('You can not book negative number of places !')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    # check if club has enough points
    if pointsAvailable < placesRequired:
        flash(f'You only have {pointsAvailable} points !')
        return render_template('welcome.html', club=club, competitions=competitions)

    # get the number of places already booked by club in selected competition
    alreadyBooked = None
    if 'booked' not in competition or club['name'] not in competition['booked']:
        competition['booked'] = {club['name']: "0"}
        alreadyBooked = 0

    if alreadyBooked is None:
        alreadyBooked = int(competition['booked'][club['name']])
    
    if placesRequired + alreadyBooked > MAXIMUM_PLACES_BOOKED_PER_CLUB:
        remaining = MAXIMUM_PLACES_BOOKED_PER_CLUB - alreadyBooked
        flash(f'You can not book more than {MAXIMUM_PLACES_BOOKED_PER_CLUB} total places per competition,'
              f' you already booked {alreadyBooked}, you can book {remaining} additionnal.')
        return render_template('welcome.html', club=club, competitions=competitions)

    competition['booked'][club['name']] = int(competition['booked'][club['name']]) + placesRequired
    competition['numberOfPlaces'] = str(int(competition['numberOfPlaces'])-placesRequired)
    club['points'] = str(int(club['points']) - placesRequired)
    saveCompetitions(competition)
    saveClubs(club)
    flash('Great-booking complete!')
    print(competition)
    return render_template('welcome.html', club=club, competitions=competitions)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))