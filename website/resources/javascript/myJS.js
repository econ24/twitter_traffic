(function() {
	var project = {
		version: "0.2.0-beta"
	};
	
	var leafletMap = false,				// Leaflet map object
		maxBarWidth = 330,				// maximum length of confidence bars
		fadeDuration = 250,				// fade time for hidable elements
		displayType = displayAlerts,	// function to be called to display tweets
		featureCollection = {},			// holds the geoJSON map data
		markers = [];					// array of leaflet map markers
		
	function loadData() {
		d3.xhr("http://localhost:8080/"+sinceTime)
			.send('GET', function(err, data) {
				featureCollection = formatData(data)
				displayType();
			})
			.response(function(request) {
				return JSON.parse(request.responseText);
			});
	}
	
	var minSince = 15,		// minimum time to receive tweets
		defaultSince = 30,	// default time
		maxSince = 1440,	// maximum time
		sinceTime = 30;		// time to receive tweets
	/*
	Method used to set the time to receive tweets.
	*/
	function setSinceTime(time) {
		var oldTime = sinceTime;
		sinceTime = Math.min(Math.max((parseInt(time, 10)) || defaultSince, minSince), maxSince);
		if (oldTime != sinceTime) {
			loadData();
		}
	}
	
	var interval = false;
	var minInterval = 15000;
	var defaultInterval = 30000;
	var maxInterval = 60000;
	function setInterval(time) {
		time = Math.min(Math.max((parseInt(time, 10)) || defaultInterval, minInterval), maxInterval);
		if (interval) {
			window.clearInterval(interval);
		}
		interval = window.setInterval(loadData, time);
	};
	
	var d_names = new Array("Sunday", "Monday", "Tuesday",
			"Wednesday", "Thursday", "Friday", "Saturday");

	var m_names = new Array("January", "February", "March", 
			"April", "May", "June", "July", "August", "September", 
			"October", "November", "December");
	
	function formatData(data) {
		var collection = {type: 'FeatureCollection', features: []},
			center = [42.6525, -73.7572];

		data.forEach(function(d) {
			var feature = {properties : {}, geometry: {}},
				date = new esc.DateObj(d.created_at);// + ' UTC');
			feature.properties.header = date.getTime()+' by '+d.screen_name;
			feature.properties.body1 = date.getDate();
			feature.properties.body2 = d.text;
			feature.properties.key = d.time_stamp;
			
			feature.type = 'Feature';

			var dist = Math.random()*.25,
				angle = Math.random()*2*Math.PI,
				x = dist * Math.cos(angle),
				y = dist * Math.sin(angle),
				coords = [center[0] + x, center[1] + y];
			feature.geometry = {type: 'Point', coordinates: coords};

			collection.features.push(feature);
		});
		
		if (collection.features.length === 0) {
			var feature = {properties : {}, geometry: {}},
				date = new esc.DateObj();
			feature.properties.header = date.getTime()+', '+' No Incidents';
			feature.properties.body1 = date.getDate();
			feature.properties.body2 = "Dad-a-chum, dod-a-cheer...not to worry, the roads are clear!!!";
			feature.properties.key = 0;
			
			feature.geometry = {type: 'Point', coordinates: center};
			
			collection.features.push(feature);
		}

		return collection
	};
	
	function displayAlerts() {
		var data = featureCollection.features
			
		var alerts = d3.select("#alertDiv")
			.selectAll(".alertDiv")
			.data(data);
			
		alerts.exit()
			.remove();
			
		alerts.enter().append('div')
			.attr("class", "alertDiv")
			.each(function(d) {
				d3.select(this)
					.append("p")
					.attr("class", "alertHeader");
				d3.select(this)
					.append("p")
					.attr("class", "alertBody1");
				d3.select(this)
					.append("p")
					.attr("class", "alertBody2");
			});
			
		alerts.attr("class", "alertDiv")
			.each(function(d, i) {
				if (i == data.length-1) {
					d3.select(this).attr("class", "alertDiv alertDivBottom");
				}
				d3.select(this).select(".alertHeader")
					.text(function(d) { return d.properties.header; })
				d3.select(this).select(".alertBody1")
					.text(function(d) { return d.properties.body1; })
				d3.select(this).select(".alertBody2")
					.text(function(d) { return d.properties.body2; })
			});
			
		alerts.sort(function(a, b) {
			return b.properties.key-a.properties.key;
		});
		alerts.order();
	};

	function displayOnMap() {
		var data = featureCollection.features
			
		for (var i = 0; i < Math.max(data.length, markers.length); i++) {
			if (i >= data.length) {
				// remove excess markers
				for (var j = i; j < markers.length; j++) {
					leafletMap.removeLayer(markers[j]);
				}
				// trim markers array
				markers = markers.slice(0, i);
				break;
			} else if (i >= markers.length) {
				// add new markers
				var marker = L.marker(L.latLng(data[i].geometry.coordinates));
				marker.bindPopup(popupText(data[i].properties));
				markers.push(marker);
				leafletMap.addLayer(marker);
			} else {
				// update existing markers
				markers[i].setLatLng(L.latLng(data[i].geometry.coordinates));
			}
		}
	};
	/*
	Method to generate popup text
	*/
	function popupText(data) {
		var text = '<p class="alertHeader">'+data.header+'</p>' +
					'<p class="alertBody1">'+data.body1+'</p>' +
					'<p class="alertBody2">'+data.body2+'</p>';
		return text;
	};
	/*
	Constructor function for drop down menu.
	*/
	function DropDown(el) {
		var self = this;
		
		self.IDtag = el;
		self.visible = false;
		
		var timer = false;
		
		self.move = function(i) {
			i = i*160+'px';
			d3.select(self.IDtag).style('left', i);
		};
	
		self.populate = function(list, func) {
			var options = d3.select(self.IDtag)
							.selectAll('a')
							.data(list);
				
			options.exit().remove();
							
			options.enter().append('a');
			
			options.text(function(d) { return d.text; })
				.on('click', function(d) {
					d3.selectAll(self.IDtag + ' a');
					func(d.value);
					self.toggle();
				}).on('mouseover', function(d, i) {
					self.clearTimer();
				}).on('mouseout', function() {
					self.setTimer();
				});
		};
	
		self.toggle = function() {
			self.visible = !self.visible;
			
			if (self.visible) {
				showElement(self.IDtag);
			}
			else {
				hideElement(self.IDtag);
			}
		};
		
		self.clearTimer = function() {
				if (timer) {
					window.clearTimeout(timer);
					timer = false;
				}
		}
		
		self.setTimer = function() {
			if (!timer && self.visible) {
				timer = window.setTimeout(self.toggle, 500);
			}
		}
	};
	/*
	Instantiate a new drop down menu object.
	*/
	var dropDown = new DropDown('#dropDown');
	
	var mapVisible = false;
	function toggleMap(){
		mapVisible = !mapVisible;
		if (mapVisible) {
			showElement('#mapDiv');
			hideElement('#alertDiv');
			displayType = displayOnMap;
			displayOnMap();
		} else {
			hideElement('#mapDiv');
			showElement('#alertDiv');
			displayType = displayAlerts;
			displayAlerts()
		}
	};
	
	var linksData = [{name: 'Past Time', options: [{text: '15 Minutes', value: 15}, {text: '30 Minutes', value:30},
												   {text: '1 Hour', value: 60}, {text: '2 Hours', value: 120},
												   {text: '6 Hours', value: 360}, {text: '12 Hours', value: 720},
												   {text: '24 Hours', value: 1440}],
												   func: setSinceTime},
					{name: 'Refresh Time', options: [{text: '15 Seconds', value: 15000},
													{text: '30 Seconds', value:30000},
													{text: '60 seconds', value: 60000}],
													func: setInterval},
					{name: 'Toggle Map', options: false, func: toggleMap}];
					
	function initializeMeunBar() {
		d3.select('#navBar')
			.selectAll('a')
			.data(linksData)
			.enter().append('a')
			.text(function(d) { return d.name; })
			.on("click", function(d) {
				if (!d.options) {
					d.func();
					if (dropDown.visible) {
						dropDown.toggle();
					}
				} else {
					dropDown.toggle();
				}
			}).on('mouseover', function(d, i) {
				dropDown.move(i);
				dropDown.populate(d.options, d.func);
				dropDown.clearTimer();
			}).on('mouseout', function() {
				dropDown.setTimer();
			});
	};
	
	function showElement(el) {
		d3.select(el)
			.style("display", "block")
			.transition()
			.duration(fadeDuration)
			.style("opacity", 1.0);
	};
	
	function hideElement(el) {
		d3.select(el)
			.transition()
			.duration(fadeDuration)
			.style("opacity", 0.0)
			.each("end", function() {
				d3.select(this)
					.style("display", "none");
			});
	};
	
	Object.defineProperty(project, 'init', {value: function() {
			L.Icon.Default.imagePath = 'resources/css/images/';
			leafletMap = new L.Map("mapDiv", {center: [42.6525, -73.7572], zoom: 11})
								.addOneTimeEventListener('layeradd', function() {
									d3.select('#mapDiv').style('opacity', 0).style('display', 'none');
								})
								.addLayer(new L.TileLayer("http://{s}.tiles.mapbox.com/v3/am3081.map-lkbhqenw/{z}/{x}/{y}.png"));
								
			loadData();
			setInterval(30);
			initializeMeunBar(); },
		writable: false,
		configurable: false});
											
	this.project = project;
})();

window.onload = function() {
	project.init();
}