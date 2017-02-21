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
	formPostFavorite('destinationForm');
	return false;
}

function postHome() {
	formPostFavorite('homeForm');
	return false;
}

function formPostFavorite(formId) {
	var form = document.getElementById(formId)
	formData = {
		'form_id': formId,
		'stop_name': form.elements[0].value,
		'stop_alias': form.elements[1].value,
		'alexa_id': form.elements[2].value
	}
	if (formId === "destinationForm") {
		console.log(form.elements[3].value)
		formData['primary'] = form.elements[3].checked
	}
	$.ajax({
		url: form.getAttribute('destination'),
		type: "POST",
		contentType: "application/json",
		data: JSON.stringify(formData),
		success: function() {
			console.log('sent');
		},
		error: function() {
			alert("failure");
		}
	})
} 