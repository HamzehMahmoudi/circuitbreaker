import requests
import time
circuit_config=dict(treshold=3, timeout=3)

class CircuitBreaker:
    """
    CircuitBreaker class
    """
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"
    STATE_CLOSE = "close"

    circuits = []

    def __init__(self, treshold=3, timeout=3, fallback_func=None):
        self.treshold = treshold
        self.timeout = timeout
        self.state = CircuitBreaker.STATE_CLOSE
        self.fail = 0
        self.fallback_func = fallback_func
        self.circuits.append(self)

    def set_state(self):
        if self.fail >= self.treshold:
            self.open_circuit()
        else:
            self.close_circuit()
    
    def fallback(self , *args, **kwargs):
        """
        return fallback function
        """
        return self.fallback_func(*args, **kwargs)


    def add_fallback(self, fallback: callable):
        """
        add fallback function
        """
        self.fallback = fallback

    def open_circuit(self):
        self.state = CircuitBreaker.STATE_OPEN

    def close_circuit(self):
        """
        close circuit breaker
        """
        self.state = CircuitBreaker.STATE_CLOSE

    def half_open_circuit(self):
        """
        set state to half open
        """
        self.state = CircuitBreaker.STATE_HALF_OPEN
    
    def reset_fail(self):
        """
        reset fail
        """
        self.fail = 0

    def is_open(self):
        """
        check if circuit is open
        """
        return self.state == CircuitBreaker.STATE_OPEN
    
    def is_close(self):
        """
        check if circuit is close
        """
        return self.state == CircuitBreaker.STATE_CLOSE

    def close_all(self):
        """
        close all circuit
        """
        for circuit in self.circuits:
            circuit.close_circuit()

class CircuitMonitoring:
    """
    CircuitMonitoring class
    """
    def __init__(self, cb):
        self.circuit_breaker = cb

    def monitor(self):
        """
        monitor circuit
        """
        self.circuit_breaker.state

breaker = CircuitBreaker(**circuit_config)

def circuit(cb=breaker):
    def wrapp(func):
        def wrapper(*args, **kwargs):
            ex = None
            if cb.is_close():
                for _ in range(cb.treshold):
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        print(f"trying to call {func.__name__}")
                        ex = e
                        cb.fail += 1
                        print(cb.fail)
                        continue
                else:
                    if cb.fallback_func:
                        cb.reset_fail()
                        cb.open_circuit()
                        return cb.fallback(*args, **kwargs)
                    else:
                        cb.reset_fail()
                        cb.open_circuit()
                        return {"status": "fail", "message": f"{type(ex).__name__}"}
            elif cb.is_open():
                return {"status": "fail", "message": "we cant sent your request right now try again"}
            elif cb.is_half_open():
                return {"status": "fail", "message": "we cant sent your request right now try again"}
        return wrapper
    return wrapp



