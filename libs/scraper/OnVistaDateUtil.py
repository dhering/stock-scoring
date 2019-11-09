from datetime import datetime

class OnVistaDateUtil:
    
    def __init__(self, base_date = datetime.now()):
        self.base_date = base_date    
    
    def get_last_year(self, estimated = False, min_years: int = 1):
        return str(self.base_date.year - min_years) + ("e" if estimated else "")
    
    
    def get_current_year(self, estimated = True):
        return str(self.base_date.year) + ("e" if estimated else "")
    
    
    def get_next_year(self, estimated = True):
        return str(self.base_date.year + 1) + ("e" if estimated else "")
    
    
    def get_last_cross_year(self, estimated = False, min_years: int = 1):
        return str(self.base_date.year - min_years - 1)[2:] + "/" + str(self.base_date.year - min_years)[2:] + ("e" if estimated else "")
    
    
    def get_current_cross_year(self, estimated = True):
        return str(self.base_date.year - 1)[2:] + "/" + str(self.base_date.year)[2:] + ("e" if estimated else "")
    
    
    def get_next_cross_year(self):
        return str(self.base_date.year)[2:] + "/" + str(self.base_date.year + 1)[2:] + "e"
