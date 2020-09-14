import requests
class Cred():
    def __init__(self, username):
        """
        :rtype: object
        """
        self.organization = 'gotennaqa'
        self.username = username
        self.email = 'christian@gotenna.com'
        self.password = 'testingqa123$$'
        self.client_key = 'jJXcr6wHK9NE3fVKf0nRUyIH3FFn3q61jSbigQLo'
        self.client_id = 2
        self.api_key = '5b3ce3597851110001cf6248d4c71ce7a2854a8db35ac96903e7fed3'


    def get_token(self):
        base = 'https://portal-stage.gotennapro.com/'
        end_point = base + "oauth/token"
        data = {'username': '{username} {organization}'.format(username=self.username, organization=self.organization),
                'password': self.password,
                'client_id': self.client_id,
                'client_secret': self.client_key,
                'grant_type': 'password'}
        r = requests.post(url=end_point, data=data)
        if r.status_code == 200:
            data = r.json()
            return data['access_token']
        else:
            print('Error getting token')