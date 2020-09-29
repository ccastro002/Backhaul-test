import requests
class Cred():
    def __init__(self, username):
        """
        :rtype: object
        """
        self.organization = 'gotennaqa'
        self.username = username
        self.email = 'christian@gotenna.com'
        self.password = 'test123$'
        self.client_key = 'jJXcr6wHK9NE3fVKf0nRUyIH3FFn3q61jSbigQLo'
        self.client_id = 2
        self.api_key = '5b3ce3597851110001cf6248a599d05c89d643dfac0bfd25d8c71c4a'


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