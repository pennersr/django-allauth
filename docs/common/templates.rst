Templates
=========

Introduction
------------

The templates that are offered out of the box are intentionally plain and
without any styling. We do not want to pick a side in the multitudes of frontend
styling options out there, and the look and feel typically should be adjusted to
match the branding of your project. Therefore it is recommended that you copy all
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
---------------------------------

The ``allauth`` app includes all templates, and can be found in the
`allauth/templates
<https://codeberg.org/allauth/django-allauth/src/branch/main/allauth/templates>`__
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


Layouts
^^^^^^^

The existing templates use two base page layouts:

- The entrance layout: These are all pages where the user is in the process of
  authenticating, such as the login and signup pages.

- The account management layout: The pages where an authenticated user can
  manage the account, such as changing the email address or password.

You can alter these layouts by providing these templates in your own project:

==========================================  ===========
Template file                               Description
==========================================  ===========
allauth/layouts/base.html                   The overall base template.
allauth/layouts/entrance.html               The entrance template, extending the base template.
allauth/layouts/manage.html                 The account management template, extending the base template.
==========================================  ===========


Elements
^^^^^^^^

When rendering e.g. a Bootstrap button you would typically use::

    <button class="btn btn-primary">Okay</button>

Yet, when a different CSS framework is used other class names apply, and
possibly even other markup. Therefore, the built-in templates do not include the
above content directly. Instead of referring to tags such ``<button>``, ``<h1>``
or ``<form>`` directly, the templates render those elements using a special
element `templatetag`::

    {% load allauth %}
    {% element h1 tags="foo,bar" %}Welcome{% endelement %}

Under the hood, this `templatetag` renders the ``allauth/elements/h1.html``
template, which out of the box contains this::

    {% load allauth %}<h1>{% slot %}{% endslot %}</h1>

If you want to change the styling of all headings across all pages, you can do
so by overriding that ``allauth/elements/h1.html`` template, as follows::

    {% load allauth %}
    <div class="myproject-h1 aa-{{ origin|slugify }}"
         style="font-size: {% if "foo" in attrs.tags %}3{% else %}5{% endif %}rem">
        {% slot %}{% endslot %}
    </div>

Of course, the above is a bit of a contrived example. In each of the element
templates the ``{{ origin }}`` context variable is available, which is equal to
the base template name where the element is used (e.g. ``account/login`` for
elements used from within the ``account/login.html`` template).

Slots may also be named. In that case, the ``element`` will be invoked like::

    {% load allauth %}
    {% element form method="post" action=action_url %}
        {% slot body %}
            ...
        {% endslot %}
        {% slot actions %}
            ...
        {% endslot %}
    {% endelement %}

When overriding an element with named slots, they may be injected in any order.
For example, with ``allauth/elements/form.html``::

    {% load allauth %}
    <form method="{{ attrs.method }}" action="{{ attrs.action }}">
        {% slot body %}
        {% endslot %}
        <hr>
        {% slot actions %}
        {% endslot %}
    </form>

The following elements are available -- override them as you see fit for your
project:

==========================================  ===========
Template file                               Description
==========================================  ===========
allauth/elements/alert.html                 Display alert messages.
allauth/elements/badge.html                 Badges for labeling purposes.
allauth/elements/button.html                A button (``<button>``).
allauth/elements/button_group.html          A group of related buttons.
allauth/elements/field.html                 A single form field.
allauth/elements/fields.html                The form fields, uses ``{{form.as_p}}`` by default, hence, not rendering the ``field.html``.
allauth/elements/form.html                  The ``<form>`` container tag.
allauth/elements/h1.html                    Level 1 heading (``<h1>``).
allauth/elements/h2.html                    Level 2 heading (``<h2>``).
allauth/elements/hr.html                    Horizontal rule (``<hr>``).
allauth/elements/img.html                   An image  tag (``<img>``).
allauth/elements/panel.html                 A panel (aka card), consisting of a title, body and actions.
allauth/elements/p.html                     Paragraphs (``<p>``).
allauth/elements/provider.html              A link to a third-party provider.
allauth/elements/provider_list.html         The container element for the list of third-party providers.
allauth/elements/table.html                 Table (``<table>``).
allauth/elements/tbody.html                 Table body (``<tbody>``).
allauth/elements/td.html                    Table data cell (``<td>``).
allauth/elements/th.html                    Table header cell (``<th>``).
allauth/elements/thead.html                 Table head (``<thead>``).
allauth/elements/tr.html                    Table row (``<tr>``).
==========================================  ===========


Example
^^^^^^^

The source repository contains a Bootstrap styled example project, which
provides a good example of how all of the above can be put together to provide
styling without altering any of the content templates.  Please take a look at
the `templates of the example project
<https://codeberg.org/allauth/django-allauth/src/branch/main/examples/regular-django/example/templates>`__.
You can see those templates live in the `running demo project
<https://django.demo.allauth.org>`__.
