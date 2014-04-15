import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from easyaspect import Aspect, before


class Car(object):
    running = False
    speed = 0

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def accelerate(self, delta=1):
        if self.running:
            self.speed += delta

    def brake(self, delta=1):
        if delta > self.speed:
            delta = self.speed
        if self.speed > 0:
            self.speed -= 1


class LoggerAspect(Aspect):
    @before('Car.*', target='methods')
    def log_methods_calls(cls, method_name, obj, *args, **kwargs):
        print('[LOG] Calling "{method_name}" (args={args}, kwargs={kwargs})'.
              format(method_name=method_name, args=args, kwargs=kwargs))

    @before('Car.speed')
    def log_speed_change(cls, prop_name, obj, value):
        print('[LOG] Changing {prop_name} from "{old_value}" to "{value}"'.
              format(prop_name=prop_name, old_value=getattr(obj, prop_name),
                     value=value))

if __name__ == '__main__':
    car = Car()

    for i in range(5):
        car.accelerate(i)
    """
    output:

        [LOG] Calling "accelerate" (args=(0,), kwargs={})
        [LOG] Calling "accelerate" (args=(1,), kwargs={})
        [LOG] Calling "accelerate" (args=(2,), kwargs={})
        [LOG] Calling "accelerate" (args=(3,), kwargs={})
        [LOG] Calling "accelerate" (args=(4,), kwargs={})

    """

    car.start()
    """
    output:
        [LOG] Calling "start" (args=(), kwargs={})
    """

    while car.speed < 10:
        car.accelerate(delta=2)
    """
    output:
        [LOG] Calling "accelerate" (args=(), kwargs={'delta': 2})
        [LOG] Changing speed from "0" to "2"
        [LOG] Calling "accelerate" (args=(), kwargs={'delta': 2})
        [LOG] Changing speed from "2" to "4"
        [LOG] Calling "accelerate" (args=(), kwargs={'delta': 2})
        [LOG] Changing speed from "4" to "6"
        [LOG] Calling "accelerate" (args=(), kwargs={'delta': 2})
        [LOG] Changing speed from "6" to "8"
        [LOG] Calling "accelerate" (args=(), kwargs={'delta': 2})
        [LOG] Changing speed from "8" to "10"
    """

    LoggerAspect.disable()

    while car.speed > 0:
        car.brake()
    """
    output:
    """

    LoggerAspect.enable()

    car.stop()
    """
    output:
        [LOG] Calling "stop" (args=(), kwargs={})
    """
