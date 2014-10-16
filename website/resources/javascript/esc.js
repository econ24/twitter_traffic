!function() {
	esc = {
		version: "0.0.3"
	}
	/*
	Function: randInt
	Method that generates and returns an integer in the range [min, max].
	Parameter: min - lower bound of range, inclusive.
	Parameter: max - upper bound of range, inclusive.
	Return: an integer in the range [min, max].
	*/
	esc.randInt = function(min, max) {
		return Math.round(Math.random()*(max-min))+min;
	};
	/*
	Capitalizes the first character of the argument string and returns result.
	Ignores leading whitespace.
	*/
	esc.capitalize = function (string) {
		var i = 0;
		while (/\s/.test(string.charAt(i))) {
			++i;
		}
		return string.slice(0, i) + string.charAt(i).toUpperCase() + string.slice(i+1)
	};
	/*
	Capitalizes the first letter of all words in the argument string.
	Also eliminates extraneous whitespace within the string. Returns
	the result. An optional separator can be specified. It is used to
	split the string before capitalizing each word.
	*/
	esc.capitalizeAll = function (string, seperator) {
		var joiner = seperator || ' ';
		seperator = seperator || /\s+/;
		string = string.trim().split(seperator);
		var temp = [];
		string.forEach(function(d, i) {
			if (string[i].length > 0)
				temp.push(esc.capitalize(string[i]));
		});
		return temp.join(joiner);
	}
	/*
	JavaScript Date object wrapper.
	Parameter: dStr - optional JavaScript interpretable UTC date string
	Usage: var name = new DateObj([date]);
	*/
	esc.DateObj = function(dStr) {
		dStr = dStr || false;
		
		var self = this,
			date;
	
		if (dStr)
			date = new Date(dStr);
		else
			date = new Date();
		
		var ampm = date.getHours() > 12 ? "PM" : "AM",
			hours24 = date.getHours(),
			hours12 = (date.getHours()-12 > 0 ? date.getHours()-12 : date.getHours()===0 ? date.getHours()+12 : date.getHours()),
			minutes = (date.getMinutes()<10 ? '0'+date.getMinutes() : date.getMinutes()),
			weekDay = d_names[date.getDay()],
			month = m_names[date.getMonth()],
			monthDay = date.getDate(),
			year = date.getFullYear();
		
		self.getTime = function(get24) {
			get24 = get24 || false;
			if (get24)
				return hours24+':'+minutes;
			return hours12+':'+minutes+' '+ampm;
		};
		self.getDate = function() {
			return weekDay+', '+month+' '+monthDay+', '+year;
		};
	};
	/*
	Array of names of days of the week.
	*/
	var d_names = new Array("Sunday", "Monday", "Tuesday",
			"Wednesday", "Thursday", "Friday", "Saturday");
	/*
	Array of abbreviated names of days of the week.
	*/
	var d_names = new Array("Sun", "Mon", "Tue", "Wed", "Thr", "Fri", "Sat");
	/*
	Array of month names.
	*/
	var m_names = new Array("January", "February", "March", 
			"April", "May", "June", "July", "August", "September", 
			"October", "November", "December");
	/*
	Array of abbreviated month names.
	*/
	var m_names_abbrev = new Array("Jan", "Feb", "Mar", "Apr", "May",
			"Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec");
	
	this.esc = esc;
}();