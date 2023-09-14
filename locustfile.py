from locust import HttpUser, TaskSet, between, task

def index(l):
    l.client.get("/")

class UserBehavior(HttpUser):
    @task
    def index(self):
        self.client.get('/')
        #self.client.get('/purchasePlaces')


class WebsiteUser(HttpUser):
    task_set = UserBehavior
    wait_time = between(5.0, 9.0)
