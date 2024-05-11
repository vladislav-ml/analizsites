import json
import os
from urllib.parse import urlparse

import redis

from sitemain.settings import (BASE_DIR, REDIS_BASE, REDIS_HOST, REDIS_PORT,
                               logger)


class MyRedis:

    __instance = None

    @staticmethod
    def get_connection():
        if not MyRedis.__instance:
            MyRedis.__instance = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_BASE,
            )
        return MyRedis.__instance

    @classmethod
    def save_redis(cls, url: str, response_dict: dict, screen_bool: bool) -> None:
        domen = urlparse(url).hostname
        # save redis
        try:
            r = MyRedis.get_connection()
            if r:
                res_json = r.get(domen)
                if res_json:
                    current_dict = json.loads(res_json)
                    # remove old pdf
                    if current_dict.get('path_pdf'):
                        cls.remove_current_file(current_dict.get('path_pdf'))
                    # remove old img
                    if screen_bool and response_dict.get('img'):
                        if current_dict.get('img'):
                            cls.remove_current_file(current_dict.get('img'))

                    if not screen_bool:
                        response_dict['img'] = current_dict.get('img')

                result = json.dumps(response_dict, default=str)
                r.set(domen, result)

        except Exception as e:
            logger.error(f'Redis - save_redis - {type(e)}\n{e}')

    @classmethod
    def get_redis(cls, domen: str) -> dict | bool:
        try:
            r = MyRedis.get_connection()
            if r:
                result = r.get(domen)
                if result:
                    return json.loads(result)
        except Exception as e:
            logger.error(f'Redis - get_redis - {type(e)}\n{e}')
        return False

    @classmethod
    def update_redis_value(cls, domen: str, key: str, value: str) -> bool:
        try:
            r = MyRedis.get_connection()
            if r:
                res_object = r.get(domen)
                current_dict = json.loads(res_object)
                current_dict[key] = value
                result = json.dumps(current_dict, default=str)
                res = r.set(domen, result)
                return res

        except Exception as e:
            logger.error(f'Redis - update_redis_value - {type(e)}\n{e}')

        return False

    @classmethod
    def get_redis_all(cls, count: int = False) -> list:
        results = []
        try:
            r = MyRedis.get_connection()
            if r:
                if not count:
                    results = r.keys()
                else:
                    results = r.keys()[:count]

        except Exception as e:
            logger.error(f'Redis - get_redis_map - {type(e)}\n{e}')
        return results

    @classmethod
    def remove_current_file(cls, file: str) -> None:
        full_path = os.path.join(BASE_DIR, file[1:])
        if os.path.isfile(full_path):
            os.remove(full_path)
