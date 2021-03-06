import requests
import asyncio
import re
from typing import Callable


class VKApiMethods:
    __url = 'https://api.vk.com/method/'
    __api_version = '5.130'

    def __init__(self, access_token: str, is_group=False):
        self.__access_token = access_token
        self.__is_group = is_group

    def get_long_poll_server(self, group_id: int) -> dict:
        method_url = self.__url + 'groups.getLongPollServer'
        request_payload = {'access_token': self.__access_token,
                           'group_id': group_id,
                           'v': self.__api_version
                           }
        received_json = requests.get(method_url, request_payload).json()
        if 'error' in received_json and 'response' not in received_json:
            raise VKApiErrors(received_json['error'])
        return received_json['response']


class VKApiLongPolling:
    polling = False
    temp_list = []
    group_id = 0
    dispatching_array = {}

    def __init__(self, vk_api_methods: VKApiMethods, update_timeout=30):
        self.__vk_api_class = vk_api_methods
        self.__update_timeout = update_timeout
        json = self.__vk_api_class.get_long_poll_server(202959880)
        self.__ts = json['ts']
        self.__vk_polling_server = f"{json['server']}?act=a_check&key={json['key']}&wait=30"

    async def __bot_polling(self):
        self.polling = True  # Theoretically, it is possible to stop polling by setting this to False from outside.
        while self.polling:
            response = requests.get(self.__vk_polling_server + '&ts=' + self.__ts).json()
            if 'failed' in response:
                if response['failed'] == 2:
                    json = self.__vk_api_class.get_long_poll_server(self.group_id)
                    self.__vk_polling_server = f"{json['server']}?act=a_check&key={json['key']}&wait=30"
                    await asyncio.sleep(1)
                # TODO: handle more errors
            if 'updates' in response:
                self.__ts = response['ts']
                for item in response['updates']:
                    if item['type'] == 'message_new' and not item['object']['message']['text'] == '':
                        for i in self.dispatching_array.keys():
                            if i.match(item['object']['message']['text']):
                                self.dispatching_array[i]()

    def start_polling(self, group_id: int) -> None:
        self.group_id = group_id
        asyncio.run(self.__bot_polling())

    def stop_polling(self) -> None:
        self.polling = False

    def add_to_dispatcher(self, regular_expression: str, function: Callable) -> None:
        if regular_expression == "":
            raise ValueError("Dispatching regular expression is empty.")
        regular_pattern = re.compile(regular_expression)
        if regular_pattern in self.dispatching_array:
            raise ValueError("You have already set this regular expression.")
        self.dispatching_array[regular_pattern] = function

    def rule(self, regular_expression: str):
        def decorator(f):
            self.add_to_dispatcher(regular_expression, f)
            return f
        return decorator


class VKApiErrors(BaseException):
    pass
