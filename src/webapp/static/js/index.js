document.addEventListener('DOMContentLoaded', function () {
	document.getElementById('homeSubmit').onclick = function()
	{
		postHome();
	};

	document.getElementById('destinationSubmit').onclick = function()
	{
		postDestination();
	};

	// need to add hanlders for delete/edit primaries
});

postDestination = function() {
	formPostFavorite('newDestination');
	return false;
}

function postHome() {
	formPostFavorite('newHome');
	return false;
}

function formPostFavorite(formId) {
	var form = document.getElementById(formId)

	formData = {
		'command_type': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value
	}
	if (formId === "newDestination") {
		formData['primary'] = form.elements[3].checked
	}

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