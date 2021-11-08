import logging
import requests
logger = logging.getLogger('django')

def fallback(treshold,func, *args, **kwargs):
    """
    handle error here 
    """
    ex = None
    error_count = 0
    try_count = 0
    for _ in range(treshold):
        try:
            try_count += 1
            print(f"trying to call {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            error_count += 1
            ex = e 
            continue
    else:      
        return {"status": "fail", "message": f"{type(ex).__name__}"}

def circuitbreakear(fallback_function=fallback, treshold=1):
    def wrapp(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                #logger.error(f"somthing wrong because {type(e).__name__} trying to handle it ")
                return fallback_function(treshold, func, *args, **kwargs)
        return wrapper
    return wrapp

@circuitbreakear()
def req():
    requests.get("http://facebook.com")

print(req())