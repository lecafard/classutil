class Course:
    def __init__(self, code, name, term, year):
        self.code = code
        self.name = name
        self.term = term
        self.year = year
        self.components = []

    def __repr__(self):
        return f'Course<{self.term} {self.year} - {self.code} - {self.name}>'

    def toJSON(self):
        return {
            'code': self.code,
            'name': self.name,
            'term': self.term,
            'year': self.year,
            'components': [i.toJSON() for i in self.components]
        }

class Component:
    def __init__(self, id, cmp_type, type, section, status, filled, maximum, times):
        self.id = id
        self.cmp_type = cmp_type
        self.type = type
        self.section = section
        self.status = status
        self.filled = filled
        self.maximum = maximum
        self.times = times

    def toJSON(self):
        return {
            'id': self.id,
            'cmp_type': self.cmp_type,
            'type': self.type,
            'section': self.section,
            'status': self.status,
            'filled': self.filled,
            'maximum': self.maximum,
            'times': self.times
        }
