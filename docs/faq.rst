Frequently Asked Questions
==========================

Overall
-------

Why don't you implement support for ... ?
*****************************************

This app is just about authentication. Anything that is project
specific, such as making choices on what to display in a profile page,
or, what information is stored for a user (e.g. home address, or
favorite color?), is beyond scope and therefore not offered.

This information is nice and all, but... I need more!
*****************************************************

Here are a few third party resources to help you get started:

- https://speakerdeck.com/tedtieken/signing-up-and-signing-in-users-in-django-with-django-allauth
- http://stackoverflow.com/questions/tagged/django-allauth
- http://www.sarahhagstrom.com/2013/09/the-missing-django-allauth-tutorial/
- https://github.com/aellerton/demo-allauth-bootstrap
- https://www.tumblr.com/blog/geekynancy

Troubleshooting
---------------

The /accounts/ URL is giving me a 404
*************************************

There is no such URL. Try `/accounts/login/` instead.

When I attempt to login I run into a 404 on /accounts/profile/
**************************************************************

When you end up here you have successfully logged in. However, you
will need to implement a view for this URL yourself, as whatever is to
be displayed here is project specific. You can also decide to redirect
elsewhere:

https://docs.djangoproject.com/en/dev/ref/settings/#login-redirect-url

When I sign up I run into connectivity errors (connection refused et al)
************************************************************************

You probably have not got an e-mail (SMTP) server running on the
machine you are developing on. Therefore, `allauth` is unable to send
verification mails.

You can work around this by adding the following line to
``settings.py``:

    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

This will avoid the need for an SMTP server as e-mails will be printed
to the console. For more information, please refer to:

https://docs.djangoproject.com/en/dev/ref/settings/#email-host

My own templates could not be found
-----------------------------------

You need to puth te path to your templates in the TEMPLATES settins.  Without the path to your own templates, they will not load.  

My templates load but the allauth templates do not
--------------------------------------------------

Allauth uses base.html in it's templates.  If you also have a base.html, it will cause a collision, whichever one is found fires is the one that will load.  This was easily solved by changing the name of your base.html and, of course, editing the templates that extend it.

What is the link to the allauth url?
------------------------------------
  
You have to reference account + underscore + the page you want to link to.  For example:href="{% url 'account_login' %}".  You can view the names in the urls.py.  

Where are the allauth source files?
-----------------------------------

If you want to look at urls.py as well as the other source files on you computer, they are located in your python site-packages folder.  On a Mac, that path is:  /usr/local/lib/python2.7/site-packages/allauth.  

How id I customize the Allauth templates?
-----------------------------------------

The easiest is to just copy them to a  new folder in your project’s template folder.  For example, MyProject/templates/account.

File not found – http://127.0.0.1:8000/accounts/profile/
--------------------------------------------------------

This can be solved by adding LOGIN_REDIRECT_URL = '/' to your settings.py.  

Why does it go to accounts/profile? 
-----------------------------------------

Allauth is a wrapper for the Django authentication system and this is the default behavior of the Django login system.  From the docs: 

"If called via POST with user submitted credentials, it tries to log the user in. If login is successful, the view redirects to the URL specified in next. If next isn’t provided, it redirects to settings.LOGIN_REDIRECT_URL (which defaults to /accounts/profile/). If login isn’t successful, it redisplays the login form.”

How do I redirect to a page that is not my home page?
-----------------------------------------------------

You cannot accomplish this by putting the relative path in LOGIN_REDIRECT_URL.  It will take you to /account/login/page_you_put_in.  One way to accomplish this is through inheritance.  Put this in one of your project’s files (i.e, views.py)):

    from allauth.account.adapter import DefaultAccountAdapter

    class MyAccountAdapter(DefaultAccountAdapter):

        def get_login_redirect_url(self, request):
            return relative_path_of_page
            
and make a reference to that in your settings.py, for example:

    ADAPTER = "app.views.MyAccountAdapter"
    ACCOUNT_ADAPTER = "app.views.MyAccountAdapter"



