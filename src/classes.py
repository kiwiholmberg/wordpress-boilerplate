class File(object):
    "store file metadata"
    def __init__(self, name='', url='', file_type='theme'):        
        self.name = name
        self.url = url
        self.file_type = file_type