from datetime import date, datetime

from django.contrib.postgres.fields import ArrayField
from django.core.files.base import ContentFile
from django.db import models

from allauth.core.internal import modelkit


def test_serializer():
    class SomeValue:
        pass

    some_value = SomeValue()

    class SomeField(models.Field):
        def get_prep_value(self, value):
            return "somevalue"

        def from_db_value(self, value, expression, connection):
            return some_value

    class SomeModel(models.Model):
        dt = models.DateTimeField()
        t = models.TimeField()
        d = models.DateField()
        img1 = models.ImageField()
        img2 = models.ImageField()
        img3 = models.ImageField()
        something = SomeField()
        ips = ArrayField(models.GenericIPAddressField(), default=list, blank=True)

    def method(self):
        pass

    instance = SomeModel(
        dt=datetime.now(),
        d=date.today(),
        something=some_value,
        t=datetime.now().time(),
        ips=["1.1.1.1", "1.2.3.4"],
    )
    instance.img1 = ContentFile(b"%PDF", name="foo.pdf")
    instance.img2 = ContentFile(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x01\x00"
        b"\x00\x00\x007n\xf9$\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf"
        b"\xa4q\x00\x00\x00\x00IEND\xaeB`\x82",
        name="foo.png",
    )
    # make sure serializer doesn't fail if a method is attached to
    # the instance
    instance.method = method
    instance.nonfield = "hello"
    data = modelkit.serialize_instance(instance)
    instance2 = modelkit.deserialize_instance(SomeModel, data)
    assert getattr(instance, "method", None) == method
    assert getattr(instance2, "method", None) is None
    assert instance2.something == some_value
    assert instance2.img1.name == "foo.pdf"
    assert instance2.img2.name == "foo.png"
    assert instance2.img3.name == ""
    assert instance.nonfield == instance2.nonfield
    assert instance.d == instance2.d
    assert instance.dt.date() == instance2.dt.date()
    assert instance.ips == instance2.ips
    for t1, t2 in [
        (instance.t, instance2.t),
        (instance.dt.time(), instance2.dt.time()),
    ]:
        assert t1.hour == t2.hour
        assert t1.minute == t2.minute
        assert t1.second == t2.second
        # AssertionError: datetime.time(10, 6, 28, 705776)
        #     != datetime.time(10, 6, 28, 705000)
        assert int(t1.microsecond / 1000) == int(t2.microsecond / 1000)


def test_serializer_binary_field():
    class SomeBinaryModel(models.Model):
        bb = models.BinaryField()
        bb_empty = models.BinaryField()

    instance = SomeBinaryModel(bb=b"some binary data")

    serialized = modelkit.serialize_instance(instance)
    deserialized = modelkit.deserialize_instance(SomeBinaryModel, serialized)

    assert serialized["bb"] == "c29tZSBiaW5hcnkgZGF0YQ=="
    assert serialized["bb_empty"] == ""
    assert deserialized.bb == b"some binary data"
    assert deserialized.bb_empty == b""
