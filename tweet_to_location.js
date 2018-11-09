var fs = require('fs');
var parse = require('csv-parse');
var async = require('async');

var inputFile='QUERY.DATE.csv';
var inputFile2='NationalFile_20120204.txt.cities'

var tweet_quant_dict = {};
var output_dict = {};
var output_string = "";
var parser = parse({delimiter: ','}, function (err, data) {
  async.eachSeries(data, function (line, callback) {
    // do something with the line
    for (city in data) {
        curr_city = data[city][0];
        curr_lat_long = data[city][2] + "," + data[city][3]
        output_dict[curr_city.toLowerCase()] = curr_lat_long;
                  }
                });
              });
fs.createReadStream(inputFile2).pipe(parser);
var parser2 = parse({delimiter: ',', relax_column_count: true, relax: true}, function (err, data) {
  async.eachSeries(data, function (line, callback) {
    // do something with the line
    for (tweet in data) {
      if (tweet > 3) {
        if(output_dict[data[tweet][8]] in tweet_quant_dict) {
          tweet_quant_dict[output_dict[data[tweet][8]]] = tweet_quant_dict[output_dict[data[tweet][8]]] + 1
        } else {
          tweet_quant_dict[output_dict[data[tweet][8]]] = 1;
        }
      }
    }
  });
  console.log(tweet_quant_dict)
});
fs.createReadStream(inputFile).pipe(parser2);
// 8
