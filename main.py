from vkapi import VKApiMethods, VKApiLongPolling
import secrets
import time

vk = VKApiMethods(secrets.vk_api_key, is_group=True)
polling = VKApiLongPolling(vk)

"""def test(rule, **options):
    def decorator(f):
        endpoint = options.pop("endpoint", None)
        print(str(rule), str(f))
        return f
    return decorator

@test('test-command')
def test():
    print("Test function")"""


@polling.rule(r"[Бб][Оо][Тт],* *(?i)рецепт")
def recipe():
    print("User asked for recipe")


if __name__ == "__main__":
    polling.start_polling(secrets.vk_group_id)
