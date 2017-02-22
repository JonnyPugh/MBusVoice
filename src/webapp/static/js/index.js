document.addEventListener('DOMContentLoaded', function () {
	document.getElementById('homeSubmit').onclick = function()
	{
		postHome();
	};
	document.getElementById('destinationSubmit').onclick = function()
	{
		postDestination();
	};
	document.getElementById('submitChangePrimary').onclick = function()
	{
		postChangePrimary();
	};
	document.getElementById('submitDeleteFavorite').onclick = function()
	{
		postDeleteFavorite();
	};

	renderUserFavorites();
});

function formPost(form, formData) {
	$.ajax({
		url: form.getAttribute('destination'),
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify(formData),
		success: function(data) {
			console.log(data);
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
	// hit api endpoint and get list of user stops and primary value
	var favoriteTable = document.getElementById('userFavorites')
	$.get(favoriteTable.getAttribute('destination'), function(data) {
		
		// Render the user Favorites table and the datalist of edit and delete
		var tableRef = favoriteTable.getElementsByTagName('tbody')[0];
		var userStopsFull = data['user_stops']
		for (var stop in userStopsFull) {
			var newRow = tableRef.insertRow();
			for (var stopAttribute in userStopsFull[stop]){
				var newCell = newRow.insertCell(-1);
				var newText = document.createTextNode(userStopsFull[stop][stopAttribute]);
				newCell.appendChild(newText);
			}
			if (userStopsFull[stop]['alias'] === data['primary']) {
				newRow.className = "success";
			}
		}

		// Iterating twice to improve readability, can change for effiency but probably not necessary
		var fullListRef = document.getElementById("userStops");
		var destinationsListRef = document.getElementById("userDestinations")
		for (var stop in userStopsFull) {
			var option = document.createElement('option')
			option.value = userStopsFull[stop]['alias']
			fullListRef.appendChild(option)

			// Cannot append one option to two datalists
			if (userStopsFull[stop]['favorite_type'] == "Destination") {
				var copyOption = document.createElement('option')
				copyOption.value = userStopsFull[stop]['alias']
				destinationsListRef.appendChild(copyOption)
			}
		}

		document.getElementById('primaryAlias').value = data['primary']
	});

	// render datalist for use with edit and delete, add primary to value of edit primary

}