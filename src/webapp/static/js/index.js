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
	var formId = "newHome"
	var form = document.getElementById(formId)
	var formData = {
		'command_type': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value
	}

	formPost(form, formData);
}

function postDestination() {
	var formId = "newDestination"
	var form = document.getElementById(formId)
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
	var formId = "changePrimary"
	var form = document.getElementById(formId)
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	}

	formPost(form, formData);
}

function postDeleteFavorite() {
	var formId = "deleteFavorite"
	var form = document.getElementById(formId)
	var formData = {
		'stop_alias': form.elements[0].value,
		'alexa_id': form.elements[1].value
	}

	formPost(form, formData);
}
