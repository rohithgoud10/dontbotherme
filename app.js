// Required modules
const express = require('express');
const session = require('express-session');
const bodyParser = require('body-parser');
const sql = require('mssql');
const ejs = require('ejs');

const app = express();

// MySQL Connection
// const pool = mssql.pool({
//   host: 'localhost',
//   user: 'sa',
//   password: 'Strong.Pwd-123',
//   database: 'cabAssist',
//   port:1433
// });

//await db.connect((err) => {
//  if (err) {
//    throw err;
//  }
//  console.log('Connected to the database.');
//});

const config = {
                 server: 'localhost',
                 user: 'sa',
                 password: 'Strong.Pwd-123',
                 port:1433,
                 options: {trustServerCertificate: true}
               }

// Middleware
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(
  session({
    secret: 'your_secret_key',
    resave: true,
    saveUninitialized: true
  })
);

// Routes
app.get('/', (req, res) => {
  res.render('index', { message: '' });
});

app.get('/login', (req, res) => {
  res.render('login', { message: '' });
});

app.post('/login', (req, res) => {
  const username = req.body.username;
  const password = req.body.password;

  if (username && password) {
      // do whatever you want with your connection here
      var dbConn = new sql.ConnectionPool(config);
      dbConn.connect().then(function () {
        dbConn.query("SELECT * FROM users WHERE username = '"+username+"' AND password = '"+username+"'").then(function (recordSet) {
              console.log(recordSet);
              if (recordSet.recordset.length === 1) {
                req.session.loggedin = true;
                req.session.username = username;
                res.redirect('/home');
              } else {
                res.render('login', { message: 'Incorrect username or password.' });
              }
              dbConn.close();
          }).catch(function (err) {
              //8.
              console.log(err);
              dbConn.close();
          });
      }).catch(function (err) {
          //9.
          console.log(err);
      });
  } else {
    res.render('login', { message: 'Please enter username and password.' });
  }
});

app.get('/signup', (req, res) => {
  res.render('signup', { message: '' });
});

app.post('/signup', (req, res) => {
  const { username, password, type, location } = req.body;
  console.log("USER: "+ username);
  if (username && password) {
    var dbConn = new sql.ConnectionPool(config);
    console.log("INSERT INTO users (username, password, type, location) VALUES ('"+username+"' , '" +password+"','"+type+"','"+location+"')");
    dbConn.connect().then(function () {
      dbConn.query("INSERT INTO users (username, password, type, location) VALUES ('"+username+"' , '" +password+"','"+type+"','"+location+"')").then(function (recordSet) {
            console.log(recordSet);
            res.redirect('/login');
            dbConn.close();
        }).catch(function (err) {
            console.log(err);
            dbConn.close();
        });
    }).catch(function (err) {
        console.log(err);
    });
  } else {
    res.render('signup', { message: 'Please enter username and password.' });
  }
});

app.get('/home', (req, res) => {
  if (req.session.loggedin) {
    res.render('home', { message: 'Welcome back, ' + req.session.username + '!' });
  } else {
    res.redirect('/login');
  }
});

app.get('/signout', (req, res) => {
  res.redirect('/login');
});

// Server
app.listen(3000, () => {
  console.log('Server started on http://localhost:3000');
});
