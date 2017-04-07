var cachedRecord = {};
var stopIdToName;
var nameToStopId = {};
var stateValid = {};

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
	$("#new-group-button").remove();
	renderButton("Edit Preferences", enableEditMode, document.getElementById("buttons-div"));
	var time = document.createElement("h4");
	time.innerHTML = cachedRecord["time"] + " minutes";
	document.getElementById("time-div").appendChild(time);
	renderGroup(cachedRecord["home"], "home-div");
	renderGroup(cachedRecord["destination"], "destination-div");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		var div = document.createElement("div");
		div.id = cachedRecord["order"][i];
		div.classList.add("list-group");
		document.getElementById("groups-div").appendChild(div);
		renderGroup(cachedRecord["order"][i], cachedRecord["order"][i]);
	}
}

/*
Render the group with the specified nickname in the specified div
*/
function renderGroup(nickname, divId) {
	var div = document.getElementById(divId);
	var span = document.createElement("span");
	if (nickname) {
		addToList(span, nickname, true);
		for (var i = 0; i < cachedRecord["groups"][nickname].length; i++) {
			addToList(span, stopIdToName[cachedRecord["groups"][nickname][i]], false);
		}
	} else {
		var listElement = addToList(span, 
			"Click the edit button to set up your " + divId.split("-")[0] + " group", 
			true);
		listElement.classList.add("warning");

		// Manually change color because list-elements do 
		// not support color changes using bootswatch
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
	listElement.innerHTML = content;
	listElement.style.fontSize = "large";
	listElement.classList.add("list-group-item", isActive ? "active" : "stop");
	div.appendChild(listElement);
	return listElement;
}

/*
Enable edit mode
*/
function enableEditMode() {
	$("#buttons-div").empty();
	$("#time-div").empty();

	submit = renderButton("Submit", handleSubmit, document.getElementById("buttons-div"));
	submit.id = "submit-button";
	renderButton("Cancel", renderUserPreferences, document.getElementById("buttons-div"));

	timeElement = document.createElement("input");
	timeElement.type = "number";
	timeElement.min = 0;
	timeElement.max = 30;
	timeElement.classList.add("form-control", "input-lg");
	timeElement.value = cachedRecord["time"];
	timeElement.id = "time-input";
	timeElement.onkeypress = function(evt) {
		var charCode = evt.which ? evt.which : event.keyCode;
		return charCode <= 31 || (charCode >= 48 && charCode <= 57);
	};
	document.getElementById("time-div").appendChild(timeElement);

	$('#time-input').bind("keyup mouseup", function(){
		validateTime();
	});

	renderEditableGroup("home-div");
	renderEditableGroup("destination-div");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		renderEditableGroup(cachedRecord["order"][i]);
	}

	var groupsWellDiv = document.getElementsByClassName("well-lg")[3];
	var groupsDiv = document.getElementById("groups-div");
	var newButton = renderButton("New", createNewEditableNickname(groupsDiv), groupsWellDiv);
	newButton.id = "new-group-button";

	var datalist = document.getElementById("system-stops");
	if (datalist.childNodes.length === 0) {
		for (var stopName in nameToStopId) {
			var option = document.createElement("option");
			option.value = stopName;
			datalist.appendChild(option);
		}
	}
}

function validateTime() {
	var timeField = document.getElementById("time-input");
	var valid = (timeField.value >= 0) && (timeField.value <= 30);
	updateBorder(timeField, valid);
	setSubmitState("time", valid);
}

function renderEditableGroup(groupDivId) {
	var groupDiv = document.getElementById(groupDivId);
	var nicknameElement = groupDiv.getElementsByClassName("active")[0];

	var text = nicknameElement.classList.contains("warning") ? "" : nicknameElement.textContent;
	var buttonText;
	var buttonBehavior;
	if (groupDivId.includes("-")) {
		buttonText = "Clear";
		buttonBehavior = clearGroup(groupDiv);
	} else {
		buttonText = "Delete";
		buttonBehavior = deleteGroup(groupDiv);
	}

	var inputGroupElement = generateNicknameInputGroup(text, buttonText, buttonBehavior);
	nicknameElement.parentNode.replaceChild(inputGroupElement, nicknameElement);

	var stopElements = $.extend(true, [], groupDiv.getElementsByClassName("stop"));
	if (stopElements.length === 1) {
		var inputField = generateStopInputGroup(stopElements[0].textContent, false);
		stopElements[0].remove();
		inputGroupElement.parentNode.appendChild(inputField);
	} else {
		for (var i = 0; i < stopElements.length; i++) {
			div = generateStopInputGroup(stopElements[i].textContent, true);
			stopElements[i].remove();
			inputGroupElement.parentNode.appendChild(div);
		}
	}
	
	renderImageButton(imageUrl + "plus.png", appendStop(groupDiv), groupDiv);
}

/*
Returns an input div for nicknames
text is the nickname for a group
buttonText is the string "clear" or "delete"
func is the function to be executed by the clear/delete button is pressed
*/
function generateNicknameInputGroup(text, buttonText, func) {
	var inputDiv = generateInputDiv(text, true);
	var span = document.createElement("span");
	span.classList.add("input-group-btn");
	renderButton(buttonText, func, span);
	inputDiv.appendChild(span);
	return inputDiv;
}

/*
Returns an input div for stop names.
text is the stop name.
hasButton (true) indicates the stop row has a delete stop button.
*/
function generateStopInputGroup(text, hasButton) {
	var inputDiv = generateInputDiv(text, false);
	if (hasButton) {
		var span = document.createElement("span");
		span.classList.add("input-group-btn");
		renderImageButton(imageUrl + "x.png", deleteStop(inputDiv), span);
		inputDiv.appendChild(span);
	} else {
		inputDiv.classList.remove("input-group");
		var inputField = inputDiv.getElementsByTagName("input")[0];
		inputField.classList.add("form-group", "stop");
		inputField.classList.remove("list-group-item");
	}
	inputDiv.getElementsByTagName("input")[0].setAttribute("list", "system-stops");
	return inputDiv;
}

/*
Creates a div containing an input type field.
text is the text to be present in the field.
isNickname indicates whether it is a nickname or a stop.
*/
function generateInputDiv(text, isNickname) {
	var field = document.createElement("input");
	field.value = text;
	field.classList.add("list-group-item", "form-control", "input-lg");
	if (isNickname) {
		field.classList.add("active");
		field.setAttribute("maxlength", 30);
		field.oninput = function() {
			validateNickname(field);
		};
	} else {
		field.classList.add("stop");
		field.oninput = function() {
			validateStop(field);
		};
		// stop validation function
	}
	var inputDiv = document.createElement("div");
	inputDiv.classList.add("input-group");
	inputDiv.appendChild(field);
	return inputDiv;
}

function validateNickname(nicknameField) {
	var valid = true;

	// Verify nickname is not a duplicate
	var nicknameElements = document.getElementsByClassName("active");
	for (var i = 0; i < nicknameElements.length && valid; i++) {
		if (nicknameField.value === nicknameElements[i].value) {
			valid = nicknameField === nicknameElements[i];
		}
	}

	// Verify all characters are alphanumeric or spaces
	var regex = new RegExp("^[a-zA-Z0-9 ]+$");
	valid = valid && regex.test(nicknameField.value);

	updateBorder(nicknameField, valid);
	
	setSubmitState("nicknames", valid);
}

function validateStop(stopField) {
	var valid = stopField.value in nameToStopId || stopField.value === "";
	updateBorder(stopField, valid);
	setSubmitState("stops", valid);
}

function updateBorder(field, valid) {
	if (valid) {
		field.style.borderColor = "#dddddd";
		field.style.borderWidth = "0px"
	} else {
		field.style.borderColor = "#b94a48";
		field.style.borderWidth = "3px";
	}
}

/*
Create new nickname in the other section
*/
function createNewEditableNickname(parentNode) {
	var counter = 0;
	return function() {
		var div = document.createElement("div");
		div.id = "newnickname-" + counter++;
		div.classList.add("list-group");

		var span = document.createElement("span");
		span.appendChild(generateNicknameInputGroup("", "Delete", deleteGroup(div)));
		div.appendChild(span);

		renderImageButton(imageUrl + "plus.png", appendStop(div), div);
		parentNode.appendChild(div);
	}
}

function appendStop(parentDiv) {
	return function() {
		var span = parentDiv.childNodes[0];
		if (span.childNodes.length === 2) {
			var target = span.childNodes[1];
			span.replaceChild(generateStopInputGroup(target.childNodes[0].value, true), target);
		}
		span.appendChild(generateStopInputGroup("", span.childNodes.length !== 1));
	}
}

function deleteStop(stopElement) {
	return function() {
		var span = stopElement.parentNode;
		stopElement.remove();
		if (span.childNodes.length === 2) {
			var target = span.childNodes[1];
			span.replaceChild(generateStopInputGroup(target.childNodes[0].value, false), target);
		}
	}
}

function deleteGroup(groupElement) {
	return function() {
		groupElement.remove();
	}
}

function clearGroup(groupDiv) {
	return function() {
		var span = groupDiv.childNodes[0];
		span.innerHTML = "";
		span.appendChild(generateNicknameInputGroup("", "Clear", clearGroup(groupDiv)));
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
function renderButton(displayText, callback, parent) {
	var button = document.createElement("a");
	button.innerHTML = displayText;
	button.classList.add("btn", "btn-primary", "btn-lg");
	button.onclick = callback;
	parent.appendChild(button);
	return button;
}

/*
Handle a user submitting their changes
*/
function handleSubmit() {
	// Scrape the current state of the UI for the 
	// updated preferences and order of groups
	updated = {};
	homeDestinationOrder = [];
	var finishSubmit = true;
	var errorElements = [];
	var newHome = scrapeGroupData("home-div", updated, homeDestinationOrder);
	if (newHome && newHome.constructor === Array) {
		finishSubmit = false;
		errorElements = errorElements.concat(newHome);
	}
	var newDestination = scrapeGroupData("destination-div", updated, homeDestinationOrder);
	if (newDestination && newDestination.constructor === Array) {
		finishSubmit = false;
		errorElements = errorElements.concat(newDestination);
	}
	var groups = document.getElementById("groups-div").getElementsByClassName("list-group");
	updatedOrder = [];
	for (var i = 0; i < groups.length; i++) {
		var result = scrapeGroupData(groups[i].id, updated, updatedOrder);
		if (result && result.constructor === Array) {
			finishSubmit = false;
			errorElements = errorElements.concat(result);
		}
	}

	$(".alert").remove();
	if (!finishSubmit) {
		for (var i = 0; i < errorElements.length; i++) {
			updateBorder(errorElements[i], false);
		}

		// Show an error message to the user
		var errorDiv = document.createElement("div");
		errorDiv.classList.add("alert", "alert-dismissible", "alert-danger");
		errorDiv.innerHTML += "Please fill in or remove the highlighted preferences and submit again.";
		document.getElementById("buttons-div").appendChild(errorDiv);
		return;
	}

	// Delete all groups in cachedRecord and not in updated
	var updating = false;
	for (cachedNickname in cachedRecord["groups"]) {
		if (!(cachedNickname in updated)) {
			// Delete the cachedNickname from the database using the API
			updating = true;
			$.ajax({
				url: apiUrl + userId + "/groups/" + cachedNickname,
				type: "DELETE",
				success: function(data) {
					console.log("Deleted " + data["nickname"]);
				},
				error: function(data) {
					/* HANDLE THE ERROR */
					console.log("Failed delete");
				}
			});
		}
	}

	// Update all groups that are either in updated and not in cachedRecord
	// or have different stops in updated and cachedRecord
	combinedOrder = homeDestinationOrder.concat(updatedOrder);
	for (var index = 0; index < combinedOrder.length; index++) {
		updatedNickname = combinedOrder[index];
		var updatedStops = updated[updatedNickname];
		var putStops = !(updatedNickname in cachedRecord["groups"]);
		if (!putStops) {
			var cachedStops = cachedRecord["groups"][updatedNickname];
			var equal = cachedStops.length === updatedStops.length;
			for (var i = 0; i < cachedStops.length && equal; i++) {
				equal = cachedStops[i] === updatedStops[i];
			}
			putStops = !equal;
		}
		if (putStops) {
			// Put the updated group into the database using the API
			updating = true;
			var type = updatedNickname === newHome ? "home" : 
				updatedNickname === newDestination ? "destination" : 
				"other";
			$.ajax({
				url: apiUrl + userId + "/groups/" + updatedNickname,
				type: "PUT",
				contentType: "application/json",
				data: JSON.stringify({"stops": updatedStops, "type": type}),
				success: function(data) {
					for (nickname in data) {
						console.log("Put " + nickname);
					}
				},
				error: function(data) {
					/* HANDLE THE ERROR */
					console.log("Failed to update group");
				}
			});
		}
	}

	// Change the time with the API if the user changed the time
	var timeInput = document.getElementById("time-input");
	var value = timeInput.value ? parseInt(timeInput.value) : 0;
	if (value != cachedRecord["time"]) {
		updating = true;
		$.ajax({
			url: apiUrl + userId + "/time",
			type: "PUT",
			contentType: "application/json",
			data: JSON.stringify({"time": value}),
			success: function(data) {
				cachedRecord["time"] = data["time"];
			},
			error: function(data) {
				/* HANDLE THE ERROR */
				console.log("Failed to update time");
			}
		});
	}

	if (updating) {
		// When the user's preferences are finished updating, render them
		$(document).ajaxStop(function() {
			$(this).unbind("ajaxStop");
			cachedRecord["home"] = newHome;
			cachedRecord["destination"] = newDestination;
			cachedRecord["groups"] = updated;
			cachedRecord["order"] = updatedOrder;
			renderUserPreferences();
		});
	} else {
		renderUserPreferences();
	}
}

function scrapeGroupData(groupDivId, updated, order) {
	var groupDiv = document.getElementById(groupDivId);
	var nicknameElement = groupDiv.getElementsByClassName("active")[0];
	var nickname = nicknameElement.value;
	var stopElements = groupDiv.getElementsByClassName("stop");
	var stopIds = [];
	for (var i = 0; i < stopElements.length; i++) {
		var stopName = stopElements[i].value;
		if (stopName) {
			stopIds.push(parseInt(nameToStopId[stopName]));
		}
	}
	console.log(nickname);
	console.log(stopIds);
	if (nickname && stopIds) {
		updated[nickname] = stopIds;
		order.push(nickname);
		return nickname;
	} else if ((!nickname && !stopIds) || groupDivId.includes("-div")) {
		return null;
	} else if (!nickname) {
		return [nicknameElement];
	} else if (stopElements.length === 0) {
		// Make new stop and return its element
		var stopDiv = generateStopInputGroup("", false);
		groupDiv.appendChild(stopDiv);
		return stopDiv.getElementsByClassName("stop");
	}
	return stopElements;
}

function setSubmitState(caller, valid) {
	stateValid[caller] = valid;

	var submitOk = true;
	for (var key in stateValid) {
		submitOk = submitOk && stateValid[key];
	}

	if (submitOk) {
		document.getElementById("submit-button").removeAttribute('disabled')
	} else {
		document.getElementById("submit-button").setAttribute('disabled', 'disabled');	
	}
}
