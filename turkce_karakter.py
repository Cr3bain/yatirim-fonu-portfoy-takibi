import re
def turkish_lower(self):
    self = re.sub(r'İ', 'i', self)
    self = re.sub(r'I', 'ı', self)
    self = self.lower()
    return self

def turkish_upper(self):
    self = re.sub(r'i', 'İ', self)
    self = self.upper()
    return self
