var keys = require('./keys');
var express = require('express'),
    app = express();
var twilioAPI = require('twilio-api'),
    cli = new twilioAPI.Client(keys.sid, keys.token);
//OK... good so far. Now tell twilio-api to intercept incoming HTTP requests.
app.use(cli.middleware() );
//OK... now we need to register a Twilio application
cli.account.getApplication(keys.sid, function(err, app) {
    if(err) throw err; //Maybe do something else with the error instead of throwing?
    app.register();
});
