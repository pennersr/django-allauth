# -*- coding: utf-8 -*-

from django.test import TestCase

import utils


class BasicTests(TestCase):

    def test_generate_unique_username(self):
        examples = [('a.b-c@gmail.com', 'a.b-c'),
                    (u'Üsêrnamê', 'username'),
                    ('', 'user')]
        for input, username in examples:
            self.assertEquals(utils.generate_unique_username(input),
                              username)

    def test_email_validation(self):
        s = 'unfortunately.django.user.email.max_length.is.set.to.75.which.is.too.short@bummer.com'
        self.assertEquals(None, utils.valid_email_or_none(s))
        s = 'this.email.address.is.a.bit.too.long.but.should.still.validate.ok@short.com'
        self.assertEquals(s, utils.valid_email_or_none(s))
        s = 'x' + s
        self.assertEquals(None, utils.valid_email_or_none(s))
        self.assertEquals(None, utils.valid_email_or_none("Bad ?"))
