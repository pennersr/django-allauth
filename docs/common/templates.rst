Templates
=========

Introduction
------------

The templates that are offered out of the box are intentionally plain and
without any styling. We do not want to pick a side in the multitudes of frontend
styling options out there, and the look and feel typically should be adjusted to
match the branding of your poject. Therefore it is recommended that you copy all
templates over to your own project and adjust them as you see fit.

Having said that, over time the years the complexity of authentication grew
considerably. For example, with features such as third party account providers
and two-factor authentication adjusting the templates involves a lot more than
just styling a ``login.html`` and a ``signup.html`` template. Therefore, a
mechanism is included that allows you to adjust the look and feel of all
templates by only overriding a few core templates.  This approach allows you to
achieve visual results fast, but is of course more limited compared to styling
all templates yourself.


Overriding the Built-In Templates
--------------------------------

The ``allauth`` app includes all templates, and can be found in the
`allauth/templates
<https://github.com/pennersr/django-allauth/tree/main/allauth/templates>`__
directory. When ``allauth`` is part of your ``INSTALLED_APPS``, and
``"APP_DIRS": True`` is configured, Django will be able to find its templates.
As ``DIRS`` is searched before ``APP_DIRS``, overriding the templates involves
adding an entry to ``DIRS`` that points to your a project specific template
folder, as follows::

    from pathlib import Path

    BASE_DIR = Path(__file__).resolve().parent.parent

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [
                BASE_DIR / "templates"
            ],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

If you copy over all templates to your ``BASE_DIR / "templates"`` it should
contain these entries (a.o.):

- An ``account`` folder containing the templates from the ``allauth.account`` app.
- A ``socialaccount`` folder containing the templates from the ``allauth.socialaccount`` app.
- A ``mfa`` folder containing the templates from the ``allauth.mfa`` app.
- An ``allauth`` folder containing the overall styling templates (see the next section).


Styling the Existing Templates
------------------------------

Instead of copying all templates, a mechanism is included that allows you to
adjust the look and feel of all templates by only overriding a few core
templates.  This approach allows you to achieve visual results fast, but is of
course more limited compared to styling all templates yourself.

The built-in templates do not render headings, buttons or forms directly. So, you will not find this::

  <h1>Welcome</h1>

Instead, the above is rendered using::

  {% load allauth %}
  {% element h1 %}Welcome{% endelement %}

The ``{% element h1 %}`` template tag results in ``allauth/elements/h1.html`` being rendered. Here, you can decide to render the `h1` heading using as you see fit::

  {% load allauth %}
  <div class="myproject-h1" style="font-size: 3rem">
      {% slot default %}{% endslot %}
  </div>
