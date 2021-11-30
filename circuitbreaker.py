import requests

circuit_config=dict(treshold=3, timeout=3)

class CircuitBreaker:
    """
    CircuitBreaker class
    """
    STATE_OPEN = "open"
    STATE_HALF_OPEN = "half_open"
    STATE_CLOSE = "close"

    circuits = []

    def __init__(self, treshold=3, timeout=3):
        self.treshold = treshold
        self.timeout = timeout
        self.state = CircuitBreaker.STATE_CLOSE
        self.fail = 0
        self.circuits.append(self)

    def set_state(self):
        if self.fail >= self.treshold:
            self.open_circuit()
        else:
            self.close_circuit()
    
    def fallback(self , func, *args, **kwargs):
        """
        handle error here 
        """
        ex = None

        if self.is_close():
            for _ in range(self.treshold):
                try:
                    print(f"trying to call {func.__name__}")
                    res = func(*args, **kwargs)
                    return res
                except Exception as e:
                    self.fail += 1
                    print(self.fail)
                    ex = e
                    continue
            else:
                self.open_circuit()
                return {"status": "fail", "message": f"{type(ex).__name__}"}
        elif self.is_open():
            return {"status": "fail", "message": "we cant sent your request right now try again"}

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
    def __init__(self, circuit_config):
        self.circuit_config = circuit_config
        self.circuit_breaker = CircuitBreaker(**circuit_config)

    def monitor(self):
        """
        monitor circuit
        """
        self.circuit_breaker.state

breaker = CircuitBreaker(**circuit_config)

def circuit(cb=breaker , treshold=3, timeout=3):
    def wrapp(func):
        
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                return cb.fallback(func, *args, **kwargs)
        return wrapper
    return wrapp


@circuit()
def req():
    requests.get("http://facebook.com")

print(req())