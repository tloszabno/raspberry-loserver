def Response(data=None, ok=True, errors=[]):
    return {
        'data': data,
        'ok': ok,
        'errors': errors
    }
