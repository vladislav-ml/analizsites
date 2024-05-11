from .common import CommonMethod


class Validator:

    """ Проверка на валидацию html документа """

    @classmethod
    def get_validator_html(cls, url: str) -> dict:

        validaror_url = f'https://validator.w3.org/nu/?doc={url}&out=json'
        response = CommonMethod.send_response(validaror_url)
        if not response: return {}
        try:
            if response.json()['messages'][0]['type'] == 'non-document-error':
                return {}
        except: pass

        errors, warnings, info_mes = [], [], []
        if response.json()['messages']:
            for item in response.json()['messages']:
                if item.get('type') == 'info' and item.get('subType') == 'warning':
                    warnings.append(item.get('type'))
                elif item.get('type') == 'error':
                    errors.append(item.get('type'))
                elif item.get('type') == 'info':
                    info_mes.append(item.get('type'))
        validator = ''
        if errors and warnings:
            validator = f'{len(errors)} {CommonMethod.get_ending(len(errors), ["ошибка","ошибки","ошибок"])}, {len(warnings)} {CommonMethod.get_ending(len(warnings), ["предупреждение","предупреждения","предупреждений"])}'
        elif errors:
            validator = f'{len(errors)} {CommonMethod.get_ending(len(errors), ["ошибка","ошибки","ошибок"])}'
        elif warnings:
            validator = f'{len(warnings)} {CommonMethod.get_ending(len(warnings), ["предупреждение","предупреждения","предупреждений"])}'
        else:
            validator = 'нет ошибок и предупреждений'
        return {'validator': validator}
