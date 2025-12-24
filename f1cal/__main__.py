from bottle import run

# Import to run all the decorators

print("Running Waitress server on 0.0.0.0:8000...")

# This is a very nice API to allow using the default @route decorators with
# other WSGI servers
# https://bottlepy.org/docs/dev/deployment.html#scaling-for-production
run(host='0.0.0.0', server='waitress', port=8000)
