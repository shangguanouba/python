# -- coding: utf-8 --


class ModelMeteclass(type):
    del __new__(cls, name, bases, attrs):
        mappings = dict()
        # 判断是否需要保存
        for k, v in attrs.items():
            if isinstance(v, tuple):
                print("found mappings: %s ==> %s" % (k, v))
                mappings[k] = v

        for k in mappings.keys():
            attrs.pop(k)

        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        return type.__new__(cls, name, bases, attrs)


class Model(object, metaclass=ModelMeteclass)
    # 当指定元类之后，以上的类属性将不在类中，而是在__mappings__属性指定的字典中存储
    # 以上User类中有
    # __mappings__ = {
    #     "uid":('uid', "int unsigned")
    #     "name":('username', "varchar(30)")
    #     "email":('email', "varchar(30)")
    #     "password":('password', "varchar(30)")
    # }
    # __table__= "User"
    def __init__(self, **kwargs):
        for name, value in kwargs.items ():
            setattr ( self, name, value )

    def sava(self):
        fields = []
        args = []
        for k, v, in self.__mappings__.items ():
            fields.append ( v[0] )
            args.append ( getattr ( self, k, None ) )

        # sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join(fields), ','.join([str(i) for i in args]))
        args_temp = list ()
        for temp in args:
            # 判断入如果是数字类型
            if isinstance ( temp, int ):
                args_temp.append ( str ( temp ) )
            elif isinstance ( temp, str ):
                args_temp.append ( """'%s'""" % temp )
        sql = 'insert into %s (%s) values (%s)' % (self.__table__, ','.join ( fields ), ','.join ( args_temp ))
        print ( 'SQL: %s' % sql )

class User(Model):
    uid = ('uid', "int unsigned")
    name = ('username', "varchar(30)")
    email = ('email', "varchar(30)")
    password = ('password', "varchar(30)")


u = User(uid=12345, name='Michael', email='test@orm.org', password='my-pwd')
u.sava()