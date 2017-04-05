var cachedRecord = {};
var stopIdToName;
var nameToStopId = {};

document.addEventListener('DOMContentLoaded', function () {
	// Get bus stops and the user's preferences from the API
	$.get(apiUrl + "stops", function(data) {
		stopIdToName = data;
		for (var key in data) {
			nameToStopId[data[key]] = key;
		}
	});
	$.get(apiUrl + userId + "/time", function(data) {
		cachedRecord["time"] = data["time"];
	});
	$.get(apiUrl + userId + "/home", function(data) {
		cachedRecord["home"] = data["home"];
	});
	$.get(apiUrl + userId + "/destination", function(data) {
		cachedRecord["destination"] = data["destination"];
	});
	$.get(apiUrl + userId + "/groups", function(data) {
		cachedRecord["groups"] = data["groups"];
	});
	$.get(apiUrl + userId + "/order", function(data) {
		cachedRecord["order"] = data["order"];
	});

	// When the user's preferences are loaded, render them
	$(document).ajaxStop(function() {
		$(this).unbind("ajaxStop");
		renderUserPreferences();
	});
});

/*
Render the user preferences in cachedRecord
*/
function renderUserPreferences() {
	$(".preferences").empty();
	renderButton("Edit Preferences", enableEditMode);
	var time = document.createElement("h4");
	time.innerHTML = cachedRecord["time"] + " minutes";
	document.getElementById("time").appendChild(time);
	renderGroup(cachedRecord["home"], "home");
	renderGroup(cachedRecord["destination"], "destination");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		renderGroup(cachedRecord["order"][i], "groups");
	}
}

/*
Render the group with the specified nickname in the specified div
*/
function renderGroup(nickname, divId) {
	var div = document.createElement("div");
	if (nickname) {
		div.className = "list-group";
		addToList(div, nickname, true);
		for (var i = 0; i < cachedRecord["groups"][nickname].length; i++) {
			addToList(div, stopIdToName[cachedRecord["groups"][nickname][i]], false);
		}
	}
	else {
		div.className = "panel panel-warning";
		panelTitle = document.createElement("h3");
		panelTitle.className = "panel-heading panel-title";
		panelTitle.innerHTML = "Click the edit button to set up your " + divId + " group";
		div.appendChild(panelTitle);
	}
	document.getElementById(divId).appendChild(div);
}

/*
Add an element to the specified list with the specified content
*/
function addToList(div, content, isActive) {
	var listElement = document.createElement("a");
	listElement.innerHTML = content;
	listElement.className = "list-group-item" + (isActive ? " active" : "");
	div.appendChild(listElement);
}

/*
Enable edit mode
*/
function enableEditMode() {
	$(".preferences").empty();
	renderButton("Submit", handleSubmit);
	renderButton("Cancel", renderUserPreferences);

	time = document.createElement("input");
	time.type = "number";
	time.min = 0;
	time.max = 30;
	time.className = "form-control input-lg";
	time.value = cachedRecord["time"];
	time.id = "timeInput";
	document.getElementById("time").appendChild(time);

/*
	Add editable tables for the home, destination, and other sections
*/
}

/*
Render a button with the specified text and callback function
*/
function renderButton(displayText, callback) {
	var button = document.createElement("a");
	button.innerHTML = displayText;
	button.className = "btn btn-primary btn-lg";
	button.onclick = callback;
	document.getElementById("buttons").appendChild(button);
}

/*
Handle a user submitting their changes
*/
function handleSubmit() {
	var updating = false;
	var timeInput = document.getElementById("timeInput");
	if (timeInput.value && timeInput.value != cachedRecord["time"]) {
		updating = true;
		$.ajax({
			url: apiUrl + userId + "/time",
			type: "PUT",
			contentType: "application/json",
			data: JSON.stringify({"time": parseInt(timeInput.value)}),
			success: function(data) {
				cachedRecord["time"] = data["time"];
			},
			error: function(data) {
				/* HANDLE THE ERROR */
			}
		});
	}

/*
	# Pseudocode for logic
	# Scrape UI for updated dictionary and the order of groups
	order, updated = scrape()

	For nickname in cached:
		If nickname not in updated:
			api.delete(nickname)

	For nickname in order:
		If nickname not in cached or cached[nickname] != updated[nickname]:
			api.put(nickname, updated[nickname])

	cached = updated
*/
	if (updating) {
		// When the user's preferences are finished updating, render them
		$(document).ajaxStop(function() {
			$(this).unbind("ajaxStop");
			renderUserPreferences();
		});
	} else {
		renderUserPreferences();
	}
}

// Clears datalists and user favorites table before repopulating them
function renderUserFavorites() {

	clearTable("userFavorites");
	clearDatalist("userDestinations");
	clearDatalist("userStops");

	var favoriteTable = document.getElementById('userFavorites');
	$.get(favoriteTable.getAttribute('destination'), function(data) {
		
		// Render the user favorites table and the datalist of edit and delete
		var userStopsFull = data['user_stops'];
		for (var stop in userStopsFull) {
			var newRow = favoriteTable.getElementsByTagName('tbody')[0].insertRow();
			populateRow(newRow, userStopsFull[stop]);

			// Highlight the current primary row
			if (userStopsFull[stop]['alias'] === findPrimaryAlias(data)) {
				newRow.className = "success";
			}

			// Populate the datalists for primary editing and deletion forms
			appendListElement("userStops", userStopsFull[stop]['alias']);
			if (userStopsFull[stop]['favorite_type'] == "Destination") {
				appendListElement("userDestinations", userStopsFull[stop]['alias']);
			}
		}

		// Set default value for primary form
		document.getElementById('primaryAlias').value = findPrimaryAlias(data);
	});
}

function clearTable(tableName) {
	var table = document.getElementById(tableName);
	if (table.rows.length > 1) {
		var newBody = document.createElement('tbody');
		table.replaceChild(newBody, table.getElementsByTagName('tbody')[0]);
	}
}

function clearDatalist(listName) {
	var listChildren = document.getElementById(listName).children;
	if (listChildren.length > 0) {
		document.getElementById(listName).removeChild(listChildren[0]);
		clearDatalist(listName);
	}
}

function appendListElement(listName, textValue) {
	var option = document.createElement('option');
	option.value = textValue;
	document.getElementById(listName).appendChild(option);
}

function populateRow(row, rowData) {
	tableOrder = ['alias', 'stop_name', 'favorite_type']
	for (var i = 0; i < tableOrder.length; i++){
		var newCell = row.insertCell(-1);
		var newText = document.createTextNode(rowData[tableOrder[i]]);
		newCell.appendChild(newText);
	}
}

// Runs on every change of new origin or destination forms
function disableInvalidSubmission(fieldId, buttonId) {
	var listOptions = document.getElementsByClassName('systemLevelStop');
	systemLevelStops = [];
	for (var i = 0; i < listOptions.length; i++) {
		 systemLevelStops.push(listOptions[i].value);
	}

	// If the current value entered is not in the list of system stops
	if (systemLevelStops.indexOf(document.getElementById(fieldId).value) === -1) {
		document.getElementById(buttonId).setAttribute('disabled', 'disabled');
	} 
	else {
		document.getElementById(buttonId).removeAttribute('disabled')
	}
}
