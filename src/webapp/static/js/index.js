document.addEventListener('DOMContentLoaded', function () {

	// Add ajax call wrappers to onclick events for submit buttons
	document.getElementById('homeSubmit').onclick = function() { postHome(); };
	document.getElementById('destinationSubmit').onclick = function() { postDestination(); };
	document.getElementById('submitChangePrimary').onclick = function() { postChangePrimary(); };
	document.getElementById('submitDeleteFavorite').onclick = function() { postDeleteFavorite(); };

	// Disable submit buttons for new home and destination stops
	document.getElementById('homeSubmit').setAttribute('disabled', 'disabled')
	document.getElementById('destinationSubmit').setAttribute('disabled', 'disabled')

	populateSystemStops()

	// Add event handlers to submit buttons to monitor for valid stop name
	$('#homeStopName').bind('keyup input', function() {
		disableInvalidSubmission('homeStopName', 'homeSubmit'); 
	});
	$('#destinationStopName').bind('keyup input', function() {
		disableInvalidSubmission('destinationStopName', 'destinationSubmit'); 
	});

	renderUserFavorites();
});

function populateSystemStops() {
	var listOptions = document.getElementsByClassName('systemLevelStop');
	systemLevelStops = [];
	for (var i = 0; i < listOptions.length; i++) {
		 systemLevelStops.push(listOptions[i].value);
	}
}

function formPost(form, formData) {
	$.ajax({
		url: form.getAttribute('destination'),
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify(formData),
		success: function(data) {
			renderUserFavorites();
		},
		error: function(data) {
			console.log(data);
		}
	});
} 

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

function postChangePrimary() {
	var formId = "changePrimary";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	};

	formPost(form, formData);
}

function postDeleteFavorite() {
	var formId = "deleteFavorite";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	};

	formPost(form, formData);
}

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

function disableInvalidSubmission(fieldId, buttonId) {
	console.log(document.getElementById(fieldId).value)

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
