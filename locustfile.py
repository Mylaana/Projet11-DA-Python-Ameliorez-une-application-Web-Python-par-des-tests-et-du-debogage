"""docstring"""
from locust import HttpUser, between, task
import server
import json


def cancel_bookings():
    # saving both JSON state before simulation
    competitions = server.loadCompetitions(True)
    clubs = server.loadClubs(True)
    
    yield

    # reverting JSON to before test state
    with open('competitions.json', 'w') as file:
        json.dump(competitions, file, indent=4)
    with open('clubs.json', 'w') as file:
        json.dump(clubs, file, indent=4)

class UserBehavior(HttpUser):
    wait_time = between(1.0, 2.0)

    @task
    def index(self):
        self.client.get('/')

    @task
    def show_summary(self):
        data = {"email": "john@simplylift.co"}
        self.client.post("/showSummary", data=data)

    @task
    def book(self):
        self.client.get("/book/Fake Competition/Simply Lift")

    @task
    def purchase_places(self):
        cancel_bookings()
        club = ["Simply Lift"]
        competition = ["Fake Competition"]
        places_bought = 1

        data = {"club": club, "competition": competition, "places": places_bought}
        self.client.post("/purchasePlaces", data=data)

    @task
    def logout(self):
        self.client.get("/logout")