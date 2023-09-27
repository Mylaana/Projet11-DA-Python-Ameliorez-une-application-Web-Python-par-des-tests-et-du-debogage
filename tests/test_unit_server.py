"""unit testing server functions"""
from unittest.mock import patch
from flask import url_for
import server
from .fixtures import app, captured_template, client, revert_competitions_json, revert_clubs_json


def test_should_return_clubs():
    expected_value = [
    {
        "name":"Simply Lift",
        "email":"john@simplylift.co",
        "points":"13"
    },
    {
        "name":"Iron Temple",
        "email": "admin@irontemple.com",
        "points":"4"
    },
    {   "name":"She Lifts",
        "email": "kate@shelifts.co.uk",
        "points":"12"
    }]
    assert isinstance(server.loadClubs(), list)
    assert isinstance(server.loadClubs()[0], dict)
    assert server.loadClubs() == expected_value

def test_should_return_competitions():
    expected_value = {
            "name": "Spring Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        }
    assert isinstance(server.loadCompetitions(), list)
    assert isinstance(server.loadCompetitions()[0], dict)
    assert expected_value in server.loadCompetitions()

def test_index(client, captured_template):
    response = client.get("/")
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "index.html"

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_showsummary(client, captured_template):
    data = {"email": "john@simplylift.co"}
    response = client.post("/showSummary", data=data)
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"
    assert context['club']['name'] == 'Simply Lift'
    assert context['competitions'][0]['name'] == 'Spring Festival'

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [{"name": "Fake Competition", "date": "2050-01-31 00:00:00", "numberOfPlaces": "10"}])
def test_book_should_render_booking(client, captured_template):
    response = client.get("book/Fake Competition/Simply Lift")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "booking.html"

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_book_past_competition(client, captured_template):
    response = client.get("book/Spring Festival/Simply Lift")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"

@patch('server.clubs', [])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_book_club_not_found(client, captured_template):
    response = client.get("book/notfound/Simply Lift")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"


@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [])
def test_book_competitions_not_found(client, captured_template):
    response = client.get("book/Spring Festival/not found")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"

@patch('server.clubs', [])
@patch('server.competitions', [])
def test_book_nothing_found(client, captured_template):
    response = client.get("book/not found/not found")
    template, context = captured_template[0]

    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_purchase_places(client, captured_template, revert_competitions_json, revert_clubs_json):
    club = ["Simply Lift"]
    competition = ["Spring Festival"]
    places_before = 25
    places_bought = 3
    data = {"club": club, "competition": competition, "places": places_bought}

    response = client.post("/purchasePlaces", data=data)
    expected_value = places_before - places_bought

    template, context = captured_template[0]
    assert response.status_code == 200
    assert str(expected_value) == context['competitions'][0]['numberOfPlaces']
    assert template.name == 'welcome.html'

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"13"}])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_purchase_places_negative_number(client, captured_template, revert_competitions_json, revert_clubs_json):
    club = ["Simply Lift"]
    competition = ["Spring Festival"]
    places_before = 25
    places_bought = -5
    data = {"club": club, "competition": competition, "places": places_bought}

    response = client.post("/purchasePlaces", data=data)

    # expected value should be equal to places before
    expected_value = places_before

    template, context = captured_template[0]
    assert response.status_code == 200
    assert str(expected_value) == context['competitions'][0]['numberOfPlaces']
    assert template.name == 'welcome.html'

@patch('server.clubs', [{"name":"Simply Lift", "email":"john@simplylift.co", "points":"0"}])
@patch('server.competitions', [{"name": "Spring Festival", "date": "2020-03-27 10:00:00", "numberOfPlaces": "25"}])
def test_purchase_places_not_enough_points(client, captured_template, revert_competitions_json, revert_clubs_json):
    club = ["Simply Lift"]
    competition = ["Spring Festival"]
    places_before = 25
    places_bought = 5
    data = {"club": club, "competition": competition, "places": places_bought}

    response = client.post("/purchasePlaces", data=data)

    # expected value should be equal to places before
    expected_value = places_before

    template, context = captured_template[0]
    assert response.status_code == 200
    assert str(expected_value) == context['competitions'][0]['numberOfPlaces']
    assert template.name == 'welcome.html'

def test_logout(client, captured_template, app):
    response = client.get("/logout")
    assert response.status_code == 302

    with app.app_context():
        redirect_response = client.get(url_for("logout"), follow_redirects=True)

        template, context = captured_template[0]
        assert redirect_response.status_code == 200
        assert len(captured_template) == 1
        assert template.name == "index.html"
