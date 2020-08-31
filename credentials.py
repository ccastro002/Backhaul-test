import requests
class Cred():
    def __init__(self):
        """
        :rtype: object
        """
        self.organization = ''
        self.username = ''
        self.email = ''
        self.password = ''
        self.client_key = ''
        self.client_id = 0

    def get_token(self):
        base = 'https://portal-stage.gotennapro.com/'
        end_point = base + "oauth/token"
        data = {'username': '{email} {organization}'.format(email=self.email, organization=self.organization),
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