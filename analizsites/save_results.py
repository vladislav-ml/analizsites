from users.utils import titles


class SaveResult:

    @classmethod
    def write_result_csv(cls, file_name: str, res_dict: dict) -> None:
        with (open(f'{file_name}.csv', 'a', encoding='utf-8')) as f:
            for block in titles:
                for item in block:
                    if not isinstance(item, tuple): continue
                    key, value = item
                    f.write(f'{value} {res_dict.get(key, "")}\n')
