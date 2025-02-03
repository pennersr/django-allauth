Canvas
------------

Contact your administrator to request an api key. They will ask for the following information (each provided with a possible example value):

#. Name: MeApp
#. Owner Email: me@example.com
#. Redirect URIs:
    #. http://localhost:8000/accounts/canvas/login/callback/
    #. http://127.0.0.1:8000/accounts/canvas/login/callback/
    #. https://me.me/accounts/canvas/login/callback/
#. Icon URL: https://me.me/static/images/icons/campusq-canvas.png
#. Scopes:
    #. Read only
    #. Courses
    #. Enrollment Terms
    #. Enrollments
    #. Sections
    #. Users

They will provide you with a "key" and a "secret". When configuring the social application instance for Canvas in your django admin site, you will need to use the "key id" they gave you in the "client id" field, the "key" they gave you in the "secret key" field, and your Canvas instance's base URL (e.g. https://canvas.instructure.com) for the "key" field.
