document.addEventListener('DOMContentLoaded', function () {
	document.getElementById('homeSubmit').onclick = function() { postHome(); };
	document.getElementById('destinationSubmit').onclick = function() { postDestination(); };
	document.getElementById('submitChangePrimary').onclick = function() { postChangePrimary(); };
	document.getElementById('submitDeleteFavorite').onclick = function() { postDeleteFavorite(); };

	renderUserFavorites();
});

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
	})
} 

function postHome() {
	var formId = "newHome";
	var form = document.getElementById(formId);
	var formData = {
		'command_type': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value
	}

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
	}	

	formPost(form, formData);
}

function postChangePrimary() {
	var formId = "changePrimary";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	}

	formPost(form, formData);
}

function postDeleteFavorite() {
	var formId = "deleteFavorite";
	var form = document.getElementById(formId);
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	}

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
		clearDatalist(listName)
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
