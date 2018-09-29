from datetime import datetime

class OnVistaDateUtil:
    
    def __init__(self, base_date = datetime.now()):
        self.base_date = base_date    
    
    def get_last_year(self):
        return str(self.base_date.year - 1)
    
    
    def get_current_year(self):
        return str(self.base_date.year) + "e"
    
    
    def get_next_year(self):
        return str(self.base_date.year + 1) + "e"
    
    
    def get_last_cross_year(self):
        return str(self.base_date.year - 2)[2:] + "/" + str(self.base_date.year - 1)[2:]
    
    
    def get_current_cross_year(self):
        return str(self.base_date.year - 1)[2:] + "/" + str(self.base_date.year)[2:] + "e"
    
    
    def get_next_cross_year(self):
        return str(self.base_date.year)[2:] + "/" + str(self.base_date.year + 1)[2:] + "e"
