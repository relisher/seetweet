var json_schema = require('json-schema')
var cityToCoords = require("city-to-coords")



var fs = require('fs');
var parse = require('csv-parse');
var async = require('async');

var inputFile='ukr_cities.csv';

var output_string = "";
var parser = parse({delimiter: ','}, function (err, data) {
  async.eachSeries(data, function (line, callback) {
    // do something with the line
    for (city in data) {
      if(city != 0) {
          city = data[city][5];
          getCity(city)
                  }
                }
              });
            });
fs.createReadStream(inputFile).pipe(parser);

function getCity(city) {
  try {
    cityToCoords(city)
          .then((coords, err) => {
              if (err) {

              } else {
                output_string = output_string + city + ",UA,"  + coords.lat + "," + coords.lng + "\n";
              }
            })
  } catch(err) {
    // do nothing
  }
}


setTimeout(function() {
  fs.writeFile("test_city_lat_long.csv", output_string, function(err) {
    if(err) {
        return console.log(err);
    }

    console.log("The file was saved!");
});
}, 20000);
