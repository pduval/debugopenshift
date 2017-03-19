def application(environ, start_response):
    data = "\n".join(["{0}: {1}".format(key,val) for (key,val) in environ.iteritems()])
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
