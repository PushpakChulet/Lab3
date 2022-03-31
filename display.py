class Display(object):

    def __init__(self):
        self.pixel_number = 0
        self.is_ready = False

    def set(self, pixel_number):
        self.pixel_number = pixel_number
        self.__calculate()

    def __calculate(self):
        self.is_ready = True
