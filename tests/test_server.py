"""testing server functions"""
import server
import pytest
from .fixtures import app, captured_template, client
from unittest.mock import patch

"""
running coverage report :
coverage run -m pytest
coverage report -m
"""

# ======================================================================
# UNIT TESTS
# ======================================================================

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
    expected_value = [
        {
            "name": "Spring Festival",
            "date": "2020-03-27 10:00:00",
            "numberOfPlaces": "25"
        },
        {
            "name": "Fall Classic",
            "date": "2020-10-22 13:30:00",
            "numberOfPlaces": "13"
        }
    ]
    assert isinstance(server.loadCompetitions(), list)
    assert isinstance(server.loadCompetitions()[0], dict)
    assert server.loadCompetitions() == expected_value

def test_index(client, captured_template):
    response = client.get("/")
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "index.html"

def test_showsummary(client, captured_template):
    data = {"email": "john@simplylift.co"}
    response = client.post("/showSummary", data=data)
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "welcome.html"
    assert context['club']['name'] == 'Simply Lift'
    assert context['competitions'][0]['name'] == 'Spring Festival'

def test_book(client, captured_template):
    response = client.get("book/Spring Festival/Simply Lift")
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "booking.html"
    assert context['club']['name'] == 'Simply Lift'
    assert context['competition']['name'] == 'Spring Festival'

@patch('server.clubs', [])
def test_book_club_not_found(client, captured_template):
    response = client.get("book/notfound/Simply Lift")
    assert response.status_code == 200


@patch('server.competitions', [])
def test_book_competitions_not_found(client):
    response = client.get("book/Spring Festival/not found")
    assert response.status_code == 200

@patch('server.clubs', [])
@patch('server.competitions', [])
def test_book_nothing_found(client):
    response = client.get("book/not found/not found")
    assert response.status_code == 200

def test_logout(client, captured_template):
    response = client.get("/logout")
    template, context = captured_template[0]
    assert response.status_code == 200
    assert len(captured_template) == 1
    assert template.name == "index.html"

# peut etre on peut passer email en arg pour le sad path de book