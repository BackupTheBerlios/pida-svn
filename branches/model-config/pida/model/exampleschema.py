

import attrtypes as types

class AddressDefinition(object):

    __order__ = ['general', 'email']

    class general:
        """General information."""
        label = 'General Information'
        stock_id = 'gtk-preferences'
        __order__ = ['name', 'knows_age', 'age']
        class name:
            """Person's name"""
            label = 'Name'
            rtype = types.string
            default = 'unnamed'
        class knows_age:
            """Whether you know the person's age"""
            label = 'Age known?'
            rtype = types.boolean
            default = False
        class age:
            """The age of the person"""
            label = 'Age'
            rtype = types.intrange(0, 110, 1)
            default = 35
            sensitive_attr = 'general__knows_age'

    class email:
        """Email addresses for the person"""
        label = 'Email Addresses'
        stock_id = 'gtk-new'
        __order__ = ['home', 'work', 'extra']

        class home:
            """Home email address"""
            label = 'Home Email'
            rtype = types.string
            default = ''

        class work:
            """Work email address"""
            label = 'Work Email'
            rtype = types.readonly
            dependents = ['email__home']

            def fget(self):
                return self.email__home

        class extra:
            """Extra email address"""
            label = 'Extra Email'
            rtype = types.stringlist('11', '22', '33')
            default = '11'

    def __markup__(self):
        mu = self.general__name
        if self.general__knows_age:
            mu += "\n [ %s ] " % self.general__age
        return mu
