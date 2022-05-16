import requests


def starttest(content):

    url = 'https://fac4365e-9312-4d58-bb4d-f6a6e5eafb9a.mock.pstmn.io/postdata'

    response = requests.post(url, data=content)

    print(response.text)

    return response.text
