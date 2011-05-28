# -*- coding: utf-8 -*-
"""
    flask.wrappers
    ~~~~~~~~~~~~~~

    Implements the WSGI wrappers (request and response).

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

from werkzeug import Request as RequestBase, Response as ResponseBase, \
    cached_property

from .helpers import json, _assert_have_json
from .globals import _request_ctx_stack


class Request(RequestBase):
    """The request object used by default in Flask.  Remembers the
    matched endpoint and view arguments.

    It is what ends up as :class:`~flask.request`.  If you want to replace
    the request object used you can subclass this and set
    :attr:`~flask.Flask.request_class` to your subclass.
    """

    #: the internal URL rule that matched the request.  This can be
    #: useful to inspect which methods are allowed for the URL from
    #: a before/after handler (``request.url_rule.methods``) etc.
    #:
    #: .. versionadded:: 0.6
    url_rule = None

    #: a dict of view arguments that matched the request.  If an exception
    #: happened when matching, this will be `None`.
    view_args = None

    #: if matching the URL failed, this is the exception that will be
    #: raised / was raised as part of the request handling.  This is
    #: usually a :exc:`~werkzeug.exceptions.NotFound` exception or
    #: something similar.
    routing_exception = None

    @property
    def max_content_length(self):
        """Read-only view of the `MAX_CONTENT_LENGTH` config key."""
        ctx = _request_ctx_stack.top
        if ctx is not None:
            return ctx.app.config['MAX_CONTENT_LENGTH']

    @property
    def endpoint(self):
        """The endpoint that matched the request.  This in combination with
        :attr:`view_args` can be used to reconstruct the same or a
        modified URL.  If an exception happened when matching, this will
        be `None`.
        """
        if self.url_rule is not None:
            return self.url_rule.endpoint

    @property
    def module(self):
        """The name of the current module"""
        if self.url_rule and \
           ':' not in self.url_rule.endpoint and \
           '.' in self.url_rule.endpoint:
            return self.url_rule.endpoint.rsplit('.', 1)[0]

    @property
    def blueprint(self):
        """The name of the current blueprint"""
        if self.url_rule and ':' in self.url_rule.endpoint:
            return self.url_rule.endpoint.split(':', 1)[0]

    @cached_property
    def json(self):
        """If the mimetype is `application/json` this will contain the
        parsed JSON data.
        """
        if __debug__:
            _assert_have_json()
        if self.mimetype == 'application/json':
            request_charset = self.mimetype_params.get('charset')
            if request_charset is not None:
                j = json.loads(self.data, encoding=request_charset )
            else:
                j = json.loads(self.data)

            return j


class Response(ResponseBase):
    """The response object that is used by default in Flask.  Works like the
    response object from Werkzeug but is set to have an HTML mimetype by
    default.  Quite often you don't have to create this object yourself because
    :meth:`~flask.Flask.make_response` will take care of that for you.

    If you want to replace the response object used you can subclass this and
    set :attr:`~flask.Flask.response_class` to your subclass.
    """
    default_mimetype = 'text/html'
