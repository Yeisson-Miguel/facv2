from api.anti_spoofing.urls import *
from api.anti_spoofing.config.settings import *

if __name__ == '__main__':

    app.run(host=host_app, port=port_app, debug=True,
            threaded=True, use_reloader=False)
    #app.run(port=5000,debug=False)