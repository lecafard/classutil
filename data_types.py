class Course:
    def __init__(self, code, name, term, year):
        self.code = code
        self.name = name
        self.term = term
        self.year = year
        self.components = []

    def __repr__(self):
        return f'Course<{self.term} {self.year} - {self.code} - {self.name}>'

class Component:
    def __init__(self, id, cmp_type, type, section, status, capacity, times):
        self.id = id
        self.cmp_type = cmp_type
        self.type = type
        self.section = section
        self.status = status
        self.capacity = capacity
        self.times = times
