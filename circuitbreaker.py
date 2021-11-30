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
    
    def on_open(self, func, *args, **kwargs):
        """
        on open function
        """
        # these are not final code thes are randome shit that i think will work
        try:
            res = func(*args, **kwargs)
            self.reset_fail()
            self.close_circuit()
            return res
        except:
            self.half_open_circuit()
            return {"status": "fail", "message": "we cant sent your request right now try again"}

    def close_circuit(self):
        """
        close circuit breaker
        """
        self.state = CircuitBreaker.STATE_CLOSE

    def on_close(self, func, *args, **kwargs):
        """
        on close function
        """
        # these are not final code thes are randome shit that i think will work
        ex = None
        for _ in range(self.treshold):
            try:
                res = func(*args, **kwargs)
                self.reset_fail()
                return res
            except Exception as e:
                print(f"trying to call {func.__name__}")
                ex = e
                self.fail += 1
                print(self.fail)
                continue
        else:
            if self.fallback_func:
                self.reset_fail()
                self.open_circuit()
                return self.fallback(*args, **kwargs)
            else:
                self.reset_fail()
                self.open_circuit()
                return {"status": "fail", "message": f"{type(ex).__name__}"}


    def half_open_circuit(self):
        """
        set state to half open
        """
        self.state = CircuitBreaker.STATE_HALF_OPEN
    
    def on_half_open(self, func, *args, **kwargs):
        """
        on half open function
        """
        # these are not final code thes are randome shit that i think will work
        try:
            res = func(*args, **kwargs)
            self.reset_fail()
            self.close_circuit()
            return res
        except Exception as e:
            self.open_circuit()
            return {"status": "fail", "message": f"{type(e).__name__}"}
    
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
            if cb.is_close():
                cb.on_close(func, *args, **kwargs)
            elif cb.is_open():
                cb.on_open(func, *args, **kwargs)
            elif cb.is_half_open():
                cb.on_half_open(func, *args, **kwargs)
        return wrapper
    return wrapp


