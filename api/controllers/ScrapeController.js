/**
 * ScrapeController
 *
 * @description :: Server-side logic for managing scrapes
 * @help        :: See http://links.sailsjs.org/docs/controllers
 */

var spawn = require('child_process').spawn

module.exports = {

	scrape: function (req, res){
		var packet = req.params.all();
		sails.log.info(packet);
		if(packet.url){
			var python = spawn("python", ['/flipkart_scraper.py', packet.url]);
			output = ""
			python.stdout.on('data', function (chunk){
				sails.log.info(output) 
				output += chunk.toString()
			});
			python.stderr.on("data", function (data){
				sails.log.error(data.toString());
			})
			python.on("close", function (code){
				if(code != 0){
					return res.json(500, {"error": "error parsing url"});
				}
				else{
					return res.json(200, JSON.parse(output));
				}
			});
		} else {
			return res.json(500, {"error": "invalid request"});
		}
	},

	form: function (req, res){
		return res.view()
	}

};

