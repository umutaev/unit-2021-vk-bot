import requests
import asyncio


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

    def __init__(self, vk_api_methods: VKApiMethods, update_ts=True, update_timeout=30):
        self.__vk_api_class = vk_api_methods
        self.__update_ts = update_ts
        self.__update_timeout = update_timeout
        json = self.__vk_api_class.get_long_poll_server(202959880)
        self.__vk_polling_server = f"{json['server']}?key={json['key']}&ts={json['ts']}&wait=30"

    async def start_bot_polling(self, group_id):
        self.polling = True  # Theoretically, it is possible to stop polling by setting this to False from outside.
        while self.polling:
            response = requests.get(self.__vk_polling_server).json()
            if 'failed' in response:
                if response['failed'] == 2:
                    json = self.__vk_api_class.get_long_poll_server(202959880)
                    self.__vk_polling_server = f"{json['server']}?key={json['key']}&ts={json['ts']}&wait=30"
                    await asyncio.sleep(1)
                # TODO: handle more errors

            pass


class VKApiErrors(BaseException):
    pass
