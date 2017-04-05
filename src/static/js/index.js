var cachedRecord = {};
var stopIdToName;
var nameToStopId = {};
var numAjax = 6;

document.addEventListener('DOMContentLoaded', function () {

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

	$(document).ajaxStop(function() {
		$(this).unbind("ajaxStop");
		renderUserPreferences();
	});
	// Add ajax call wrappers to onclick events for submit buttons
	// document.getElementById('homeSubmit').onclick = function() { postHome(); };
	// document.getElementById('destinationSubmit').onclick = function() { postDestination(); };
	// document.getElementById('submitChangePrimary').onclick = function() { postChangePrimary(); };
	// document.getElementById('submitDeleteFavorite').onclick = function() { postDeleteFavorite(); };

	// // Disable submit buttons for new home and destination stops
	// document.getElementById('homeSubmit').setAttribute('disabled', 'disabled')
	// document.getElementById('destinationSubmit').setAttribute('disabled', 'disabled')

	// populateSystemStops()

	// // Add event handlers to submit buttons to monitor for valid stop name
	// $('#homeStopName').bind('keyup input', function() {
	// 	disableInvalidSubmission('homeStopName', 'homeSubmit'); 
	// });
	// $('#destinationStopName').bind('keyup input', function() {
	// 	disableInvalidSubmission('destinationStopName', 'destinationSubmit'); 
	// });

});

function renderUserPreferences() {
	$(".preferences").empty();

	renderButton("Edit Preferences", enableEditMode);

	document.getElementById("time").innerHTML = cachedRecord["time"] + " minutes";

	renderGroup(cachedRecord["home"], "home");
	renderGroup(cachedRecord["destination"], "destination");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		renderGroup(cachedRecord["order"][i], "groups");
	}
}

function renderButton(displayText, func) {
	var button = document.createElement("a");
	button.innerHTML = displayText;
	button.className = "btn btn-primary btn-lg";
	button.onclick = func;
	document.getElementById("buttons").appendChild(button);
}

function renderGroup(nickname, divId) {
	// Render nickname, or indicate unpopulated group
	var div = document.createElement("div");
	div.className = "list-group";

	if (nickname == null) {
		nickname = "This group has not been set";
		return
	}
	// Do not show the user a populated nickname and instead show an error if nickname is null
	var nicknameElement = document.createElement("a");
	nicknameElement.innerHTML = nickname;
	nicknameElement.className = "list-group-item active";
	div.appendChild(nicknameElement);
	for (var i = 0; i < cachedRecord["groups"][nickname].length; i++) {
		var listElement = document.createElement("a");
		listElement.innerHTML = stopIdToName[cachedRecord["groups"][nickname][i]];
		listElement.className = "list-group-item"
		div.appendChild(listElement)
	}

	document.getElementById(divId).appendChild(div);
}

function enableEditMode() {

}

function formPost(form, formData) {
	$.ajax({
		url: form.getAttribute('destination'),
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify(formData),
		success: function(data) {
			displayError("");
			renderUserFavorites();
		},
		error: function(data) {
			displayError(JSON.parse(data.responseText).errors[0].message);
		}
	});
} 

function displayError(message){
	document.getElementById('displayError').innerHTML=message;
}

// Function added to submission button onclick to submit form values
function postHome() {
	var formId = "newHome";
	var form = document.getElementById(formId);
	var formData = {
		'command_type': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value
	};

	formPost(form, formData);
}

// Function added to submission button onclick to submit form values
function postDestination() {
	var formId = "newDestination";
	var form = document.getElementById(formId);
	var formData = {
		'command_type': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value,
		'primary': form.elements[3].checked
	};

	formPost(form, formData);
}

// Function added to submission button onclick to submit form values
function postChangePrimary() {
	var formId = "changePrimary";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	};

	formPost(form, formData);
}

// Function added to submission button onclick to submit form values
function postDeleteFavorite() {
	var formId = "deleteFavorite";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	};

	formPost(form, formData);
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

// Accepts the modified user record and determines the primary destination
function findPrimaryAlias(data) {
	for (var i = 0; i < data['user_stops'].length; i++) {
		if (data['user_stops'][i]['stop_name'] === data['primary']) {
			return data['user_stops'][i]['alias'];
		}
	}
	return "";
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
