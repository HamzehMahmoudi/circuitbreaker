import logging
import requests
logger = logging.getLogger('django')

def fallback(treshold,func, *args, **kwargs):
    """
    handle error here 
    """
    for _ in range(treshold):
        try:
            print(f"trying to call {func.__name__}")
            return func(*args, **kwargs)
        except Exception as e:
            continue
    else:      
        return {"status": "fail", "message": f"{type(e).__name__}"}

def circuitbreakear(fallback_function=fallback, treshold=3):
    def wrapp(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                #logger.error(f"somthing wrong because {type(e).__name__} trying to handle it ")
                return fallback_function(treshold, func, *args, **kwargs)
        return wrapper
    return wrapp
