from app import app
# this is  a test
app.run(host=app.config['HOST'], port=app.config['PORT'], debug=app.config['DEBUG'])