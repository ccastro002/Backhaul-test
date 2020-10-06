import requests
class Cred():
    def __init__(self, username):
        """
        :rtype: object
        """
        self.organization = ''
        self.username = username
        self.email = ''
        self.password = ''
        self.client_key = ''
        self.client_id = 0
        self.api_key = ''


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