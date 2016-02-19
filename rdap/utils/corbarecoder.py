import codecs
import exceptions
import types


class UnsupportedEncodingError(Exception):
    pass

class DecodeError(Exception):
    pass

class CorbaRecode(object):

    def __init__(self, coding='utf-8'):
        object.__init__(self)
        self.BasicTypes = (
                types.BooleanType,
                types.FloatType,
                types.IntType,
                types.LongType
                )
        self.IterTypes = (
                types.TupleType,
                types.ListType
                )
        try:
            codecs.lookup(coding)
            self.coding = coding
        except (codecs.LookupError,), (val, no):
            raise UnsupportedEncodingError(val, no)

    def decode(self, answer):
        if type(answer) in types.StringTypes:
            return answer.decode(self.coding)
        if type(answer) in self.BasicTypes:
            return answer
        elif type(answer) in self.IterTypes:
            return [ self.decode(x) for x in answer ]
        elif type(answer) == types.InstanceType or (hasattr(answer, '__class__') and ('__dict__' in dir(answer) or hasattr(answer, '__slots__'))):
            for name in dir(answer):
                item = getattr(answer, name)
                if name.startswith('__'): continue # internal python methods / attributes
                if type(item) in types.StringTypes:
                    answer.__dict__[name] = item.decode(self.coding)
                if name.startswith('_'): continue # internal module defined methods / attributes
                if type(item) == types.MethodType: continue # methods - don't call them
                if type(item) == types.InstanceType or (hasattr(answer, '__class__') and ('__dict__' in dir(answer) or hasattr(answer, '__slots__'))):
                    answer.__dict__[name] = self.decode(item)
                if type(item) in self.IterTypes:
                    answer.__dict__[name] = [ self.decode(x) for x in item ]
            return answer

    def encode(self, answer):
        if type(answer) in types.StringTypes:
            return answer.encode(self.coding)
        if type(answer) in self.BasicTypes:
            return answer
        elif type(answer) in self.IterTypes:
            return [ self.encode(x) for x in answer ]
        elif type(answer) == types.InstanceType or (hasattr(answer, '__class__') and ('__dict__' in dir(answer) or hasattr(answer, '__slots__'))):
            for name in dir(answer):
                item = getattr(answer, name)
                if name.startswith('__'): continue # internal python methods / attributes
                if type(item) in types.StringTypes:
                    answer.__dict__[name] = item.encode(self.coding)
                if name.startswith('_'): continue # internal module defined methods / attributes
                if type(item) == types.MethodType: continue # methods - don't call them
                if type(item) == types.InstanceType or (hasattr(answer, '__class__') and ('__dict__' in dir(answer) or hasattr(answer, '__slots__'))):
                    answer.__dict__[name] = self.encode(item)
                if type(item) in self.IterTypes:
                    answer.__dict__[name] = [ self.encode(x) for x in item ]
            return answer

recoder = CorbaRecode()
c2u = recoder.decode # recode from corba string to unicode
u2c = recoder.encode # recode from unicode to strings
