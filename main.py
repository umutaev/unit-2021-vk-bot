from vkapi import VKApiMethods
from secrets import vk_api_key, vk_group_id

if __name__ == "__main__":
    vk = VKApiMethods(vk_api_key, is_group=True)
    print(vk.get_long_poll_server(vk_group_id))
