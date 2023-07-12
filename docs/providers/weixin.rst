Weixin
------

The Weixin OAuth2 documentation:

    https://open.weixin.qq.com/cgi-bin/showdocument?action=dir_list&t=resource/res_list&verify=1&id=open1419316505&token=&lang=zh_CN

Weixin supports two kinds of oauth2 authorization, one for open platform and
one for media platform, AUTHORIZE_URL is the only difference between them, you
can specify ``AUTHORIZE_URL`` in setting, If no ``AUTHORIZE_URL`` value is set
will support open platform by default, which value is
``https://open.weixin.qq.com/connect/qrconnect``.

You can optionally specify additional scope to use. If no ``SCOPE`` value
is set, will use ``snsapi_login`` by default(for Open Platform Account, need
registration). Other ``SCOPE`` options are: snsapi_base, snsapi_userinfo.

.. code-block:: python

    SOCIALACCOUNT_PROVIDERS = {
        'weixin': {
            'AUTHORIZE_URL': 'https://open.weixin.qq.com/connect/oauth2/authorize',  # for media platform
            'SCOPE': ['snsapi_base'],
        }
    }
