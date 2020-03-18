import random
import uuid
import math
from locust import HttpLocust, TaskSet, task
import time
import requests
Names = "Beatrix,Blaire,Callie,Cecily,Cleo,Coco,Cosette,Cybil,Daisy".split(",")
# load user credentials from CSV
#user_credentials = read_user_credentials_from_csv()
# https://b08ad5a0.ap.ngrok.io/webhook/
#http://192.168.2.85:3000/ccs
webhook_line = "https://aoc-dev.appman.co.th/webhook/mock-line"
# webhook_line = 'http://192.168.2.85:8080/webhook/mock-line'
url= 'https://tdacwe7cl5hhpnd22xqfkf66ia.appsync-api.ap-southeast-1.amazonaws.com/graphql'

payload = {
    'username': 'test',
    'password': '1q2w3e4r',
    'grant_type': 'password',
    'client_id': 'ccs',
    'response_type': 'token'
}
r = requests.post("https://aoc-dev.appman.co.th/auth/realms/agm/protocol/openid-connect/token", data=payload)
access_token = r.json()['access_token']

class WebsiteTasks(TaskSet):
    def on_start(self):
        print("start init")
        self.headers = {'authority': 'tdacwe7cl5hhpnd22xqfkf66ia.appsync-api.ap-southeast-1.amazonaws.com',
                   'pragma': 'no-cache',
                   'cache-control': 'no-cache',
                   'accept': '*/*',
                   'sec-fetch-dest': 'empty',
                   'authorization': access_token,
                   'x-amz-user-agent': 'aws-amplify/2.0.1',
                   'Content-Type': 'application/json',
                   'accept-language': 'th,en;q=0.9'
                   }
        # r = requests.post("https://aoc-dev.appman.co.th/auth/realms/agm/protocol/openid-connect/token", data=payload)
        # self.access_token = r.json()['access_token']
        # credentials = random.choice(user_credentials)
        # self.client.post("/login/", {"username":credentials[0], "password":credentials[1]})
        # self.user_id = 'U52030c4abcb993fe5f868d7f48531406'
        self.user_id=str(uuid.uuid4())
        self.initialData()
        time.sleep(2)
        print("end init")
        # ws = create_connection('ws://127.0.0.1:5000/echo')
        # self.ws = ws

    def initialData(self):
        json = {
            "events": [
                {
                    "type": "message",
                    "mode": "active",
                    "timestamp": 1462629479859,
                    "source": {
                        "type": "user",
                        "userId": self.user_id
                    },
                    "message": {
                        "id": "325708",
                        "type": "text",
                        "text": "test1234 Webhook " + str(uuid.uuid4())
                    }
                }
            ]
        }
        r = self.client.post(webhook_line, json=json, headers={},
                             name='webhookMessages')

    @task(1)
    def getTasks(self):
        json = {"operationName": None, "variables": {"userId": self.user_id},
                "query": "{\n  listChats {\n    items {\n      ...task\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment task on Chat {\n  id\n  name\n  __typename\n}\n"}
        r = self.client.post(url, json=json, headers=self.headers,name='getTasks')

    @task(1)
    def getMessages(self):
        json = {"operationName": "getChat", "variables": {"id": self.user_id},
                "query": "query getChat($id: String!) {\n  getChat(id: $id) {\n    ...chat\n    __typename\n  }\n}\n\nfragment chat on Chat {\n  id\n  name\n  messages {\n    ...message\n    __typename\n  }\n  __typename\n}\n\nfragment message on Message {\n  source {\n    roomId\n    channel\n    __typename\n  }\n  type\n  content {\n    text\n    __typename\n  }\n  __typename\n}\n"}

        r = self.client.post(url, json=json, headers=self.headers,name='getMessages')


    # @task(20)
    # def postMessages(self):
    #     json ={"operationName":"updateMessage","variables":{"input":{"id":self.user_id,
    #              "from":"CCS","to":"LINE","type":"text","content":"{\"text\":\"jj "+ str(uuid.uuid4())+"\"}"}
    #         },"query":"mutation updateMessage($input: UpdateMessageInput!) {\n  updateMessage(input: $input) {\n    ...chatMessage\n    __typename\n  }\n}\n\nfragment chatMessage on ChatMessage {\n  id\n  from\n  to\n  message {\n    ...message\n    __typename\n  }\n  __typename\n}\n\nfragment message on Message {\n  source {\n    roomId\n    channel\n    __typename\n  }\n  type\n  content {\n    text\n    __typename\n  }\n  __typename\n}\n"}
    #     r = self.client.post(url, json=json, headers=self.headers,name='postMessages')
    #     # print(r.content[:100])
    #     response_data = r.json()
    #
    #     assert response_data.get("data",{}).get("updateMessage",{}) is not None , r.content[:256]

    @task(1)
    def postMessages(self):
        json ={"operationName":"updateMessage","variables":{"input":{"id":self.user_id,
                 "from":"CCS","to":"LINE","type":"text","content":"{\"text\":\"test1234 "+ str(uuid.uuid4())+"\"}"}
            },"query":"mutation updateMessage($input: UpdateMessageInput!) {\n  updateMessage(input: $input) {\n    ...chatMessage\n    __typename\n  }\n}\n\nfragment chatMessage on ChatMessage {\n  id\n  from\n  to\n  message {\n    ...message\n    __typename\n  }\n  __typename\n}\n\nfragment message on Message {\n  source {\n    roomId\n    channel\n    __typename\n  }\n  type\n  content {\n    text\n    __typename\n  }\n  __typename\n}\n"}
        with self.client.post(url, json=json, headers=self.headers, \
                              name='postMessages',  catch_response=True) as r:
            response_data = r.json()
            if response_data.get("data",{}).get("updateMessage",{}) is not None :
                r.success()
            else:
                r.failure(response_data.get("errors", {})[0]['message'][:160])
    @task(1)
    def webhookMessages(self):
        json ={
              "events": [
                {
                  "type": "message",
                  "mode": "active",
                  "timestamp": 1462629479859,
                  "source": {
                    "type": "user",
                    "userId": self.user_id
                  },
                  "message": {
                    "id": "325708",
                    "type": "text",
                    "text": "test1234 Webhook "+ str(uuid.uuid4())
                  }
                }
              ]
            }
        r = self.client.post(webhook_line , json=json, headers={},name='webhookMessages')
        # print(r.content[:100])



class WebsiteUser(HttpLocust):
    task_set = WebsiteTasks
    #By default the time is randomly chosen uniformly between min_wait and max_wait
    min_wait = 200
    max_wait = 500