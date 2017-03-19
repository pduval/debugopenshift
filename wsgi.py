import os
def application(environ, start_response):
    req_data = "\n".join(["{0}: {1}".format(key,val) for (key,val) in environ.iteritems()])
    sys_data = "\n".join(["{0}: {1}".format(key,val) for (key,val) in os.environ.iteritems()])
    data = "Request Data:\n{0}\n\nEnvironment:\n{1}\n\n".format(req_data, sys_data)
    start_response("200 OK", [
        ("Content-Type", "text/plain"),
        ("Content-Length", str(len(data)))
    ])
    return iter([data])
