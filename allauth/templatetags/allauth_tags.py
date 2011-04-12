# HACK ALERT! If you use the following construct, openid_tags is still
# referenced even if allauth.openid is not enabled.
#
#     {% if allauth.openid_enabled %}
#     {% load openid_tags %}
#     <a href="{% openid_login_url next="/welcome/" %}">Login</a>
#     {% endif %}
#
# Therefore, we need to do some trickery here and import the tags from
# enabled sub-applications here. It's ugly, but at least it allows us
# to do:
#
#     {% load allauth_tags %}
#     {% if allauth.openid_enabled %}
#     <a href="{% openid_login_url next="/welcome/" %}">Login</a>
#     {% endif %}


from django import template
from allauth import app_settings 

register = template.Library()

class NotImplementedNode(template.Node):
    def render(self, context):
        raise NotImplementedError

if app_settings.OPENID_ENABLED:
    from allauth.openid.templatetags.openid_tags import register_tags
    register_tags(register)
else:
    def openid_login_url(parser, token):
        return NotImplementedNode()
    register.tag(openid_login_url)

if app_settings.TWITTER_ENABLED:
    from allauth.twitter.templatetags.twitter_tags import register_tags
    register_tags(register)
else:
    def twitter_login_url(parser, token):
        return NotImplementedNode()
    register.tag(twitter_login_url)

if app_settings.FACEBOOK_ENABLED:
    from allauth.facebook.templatetags.facebook_tags import register_tags
    register_tags(register)
else:
    def facebook_login_url(parser, token):
        return NotImplementedNode()
    def fbconnect(parser, token):
        return NotImplementedNode()
    register.tag(facebook_login_url)
    register.tag(fbconnect)


