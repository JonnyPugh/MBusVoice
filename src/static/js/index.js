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
	renderButton("Edit Preferences", enableEditMode, document.getElementById("buttons"), true);
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
	var div = document.getElementById(divId);
	var span = document.createElement("span");

	div.className += " list-group";
	if (nickname) {
		addToList(span, nickname, true);
		for (var i = 0; i < cachedRecord["groups"][nickname].length; i++) {
			addToList(span, stopIdToName[cachedRecord["groups"][nickname][i]], false);
		}
	}
	else {
		addToList(span, "Click the edit button to set up your " + divId + " group", true);
		var listElement = span.firstChild;
		listElement.classList.add("warning");
		// Manualy change color because list-elements do not support color changes using bootswatch
		listElement.style.backgroundColor = "#ff6600";
		listElement.style.borderColor = "#ff6600";
	}
	div.appendChild(span);
}

/*
Add an element to the specified list with the specified content
*/
function addToList(div, content, isActive) {
	var listElement = document.createElement("a");
	listElement.style.fontSize = "x-large"
	listElement.innerHTML = content;
	listElement.className = "list-group-item " + (isActive ? "active nickname" : "stop");
	div.appendChild(listElement);
}

/*
Enable edit mode
*/
function enableEditMode() {
	$("#buttons").empty();
	// $("#time").empty();
	renderButton("Submit", handleSubmit, document.getElementById("buttons"), true);
	renderButton("Cancel", renderUserPreferences, document.getElementById("buttons"), true);

	// time = document.createElement("input");
	// time.type = "number";
	// time.min = 0;
	// time.max = 30;
	// time.className = "form-control input-lg";
	// time.value = cachedRecord["time"];
	// time.id = "timeInput";
	// document.getElementById("time").appendChild(time);

	// Begin making home editable
	var homeDiv = document.getElementById("home");
	var homeNicknameElement = homeDiv.getElementsByClassName("nickname")[0];

	var div = document.createElement("div");
	div.className = "input-group";

	var text = homeNicknameElement.innerHTML;
	if (homeNicknameElement.classList.contains("warning")) {
		text = "";
	}

	var span = document.createElement("span");
	span.className = "input-group-btn";

	var field = document.createElement("input");
	field.value = text;

	field.className = "list-group-item input-lg form-control input group active nickname";
	renderButton("Clear", clearGroup(div), span, true);

	var parentSpan = homeNicknameElement.parentNode;
	div.appendChild(field);
	div.appendChild(span);

	parentSpan.replaceChild(div, homeNicknameElement);

	var homeStopElements = homeDiv.getElementsByClassName("stop");

	for (var i = 0; i < homeStopElements.length; i++) {
		var span = document.createElement("span");
		span.className = "input-group-btn";

		var field = document.createElement("input");
		field.value = homeStopElements[i].innerHTML;
		field.className = "list-group-item form-control input group stop";

		if (homeStopElements.length > 1) {
			renderButton("Delete", removeStop(homeDiv), span, false);
		}

		homeDiv.appendChild(field);
		homeDiv.appendChild(span);
	}

	renderImageButton(imageUrl + "plus.png", appendStop("home"), homeDiv);
}

function appendStop(parentDivId) {
	return function() {
		alert(parentDivId);
	}
}

function removeGroup(nickname) {
	return function(){

		// remove element with this id
		console.log(nickname);

	}
}

function clearGroup(nickname) {
	return function() {
		console.log(nickname)
	}
}

function removeStop(stop) {
	return function(){
		stop.remove()
	}
}

/*
Render a button with the image and callback function
*/
function renderImageButton(image, callback, parent) {
	var button = document.createElement("img");
	button.style.display = "block";
	button.style.margin = "0 auto";
	button.src = image;
	button.onclick = callback;
	parent.appendChild(button);
}

/*
Render a button with the specified text and callback function
*/
function renderButton(displayText, callback, parent, large) {
	var button = document.createElement("a");
	button.innerHTML = displayText;
	button.className = "btn btn-primary" + (large ? " btn-lg" : "");
	button.onclick = callback;
	parent.appendChild(button);
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

function appendListElement(listName, textValue) {
	var option = document.createElement('option');
	option.value = textValue;
	document.getElementById(listName).appendChild(option);
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
