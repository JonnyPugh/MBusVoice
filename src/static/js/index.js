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
	$("#new-group-button").remove();
	renderButton("Edit Preferences", enableEditMode, document.getElementById("buttons"));
	var time = document.createElement("h4");
	time.innerHTML = cachedRecord["time"] + " minutes";
	document.getElementById("time-div").appendChild(time);
	renderGroup(cachedRecord["home"], "home-div");
	renderGroup(cachedRecord["destination"], "destination-div");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		var div = document.createElement("div");
		div.id = cachedRecord["order"][i];
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
	div.classList.add("list-group");
	if (nickname) {
		addToList(span, nickname, true);
		for (var i = 0; i < cachedRecord["groups"][nickname].length; i++) {
			addToList(span, stopIdToName[cachedRecord["groups"][nickname][i]], false);
		}
	}
	else {
		addToList(span, "Click the edit button to set up your " + divId.split('-')[0] + " group", true);
		var listElement = span.firstChild;
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
	listElement.classList.add("list-group-item");
	if (isActive) {
		listElement.classList.add("active");
	}
	else {
		listElement.classList.add("stop");
	}
	div.appendChild(listElement);
}

/*
Enable edit mode
*/
function enableEditMode() {
	$("#buttons").empty();
	$("#time-div").empty();

	renderButton("Submit", handleSubmit, document.getElementById("buttons"));
	renderButton("Cancel", renderUserPreferences, document.getElementById("buttons"));

	time = document.createElement("input");
	time.type = "number";
	time.min = 0;
	time.max = 30;
	time.classList.add("form-control", "input-lg");
	time.value = cachedRecord["time"];
	time.id = "timeInput";
	document.getElementById("time-div").appendChild(time);

	renderEditableGroup("home-div");
	renderEditableGroup("destination-div");
	for (var i = 0; i < cachedRecord["order"].length; i++) {
		renderEditableGroup(cachedRecord["order"][i]);
	}

	var groupsWellDiv = document.getElementsByClassName("well-lg")[3];
	var groupsDiv = document.getElementById("groups-div");
	var newButton = renderButton("New", createNewEditableNickname(groupsDiv), groupsWellDiv);
	newButton.id = "new-group-button";
}

function renderEditableGroup(groupDivId) {
	var groupDiv = document.getElementById(groupDivId);
	var nicknameElement = groupDiv.getElementsByClassName("active")[0];

	var field = document.createElement("input");
	field.value = nicknameElement.classList.contains("warning") ? "" : nicknameElement.textContent;
	field.classList.add("list-group-item", "form-control", "input-lg", "active");

	var inputDiv = document.createElement("div");
	inputDiv.classList.add("input-group");
	inputDiv.appendChild(field);

	var span = document.createElement("span");
	span.classList.add("input-group-btn");
	if (groupDivId === "home-div" || groupDivId === "destination-div") {
		renderButton("Clear", clearGroup(inputDiv), span);
	}
	else {
		renderButton("Delete", deleteGroup(groupDiv), span);
	}
	inputDiv.appendChild(span);
		
	nicknameElement.parentNode.replaceChild(inputDiv, nicknameElement);

	var stopElements = $.extend(true, [], groupDiv.getElementsByClassName("stop"));
	if (stopElements.length === 1) {
		var field = document.createElement("input");
		field.value = stopElements[0].textContent;
		field.classList.add("form-group", "form-control", "input-lg", "stop");
		stopElements[0].remove();
		inputDiv.parentNode.appendChild(field);
	}
	else {
		for (var i = 0; i < stopElements.length; i++) {
			var div = document.createElement("div");
			div.classList.add("input-group");

			var field = document.createElement("input");
			field.value = stopElements[i].textContent;
			field.classList.add("list-group-item", "form-control", "input-lg", "stop");
			div.appendChild(field);

			var span = document.createElement("span");
			span.classList.add("input-group-btn");
			renderImageButton(imageUrl + "x.png", deleteStop(div), span);
			div.appendChild(span);

			stopElements[i].remove();
			inputDiv.parentNode.appendChild(div);
		}
	}

	renderImageButton(imageUrl + "plus.png", appendStop(groupDivId), groupDiv);
}

/*
	Create new nickname in the other section
*/
function createNewEditableNickname(parentNode) {
	var counter = 0;
	return function() {
		var field = document.createElement("input");
		field.value = "";
		field.classList.add("list-group-item", "form-control", "input-lg", "active");

		var inputGroupDiv = document.createElement("div");
		inputGroupDiv.classList.add("input-group");
		inputGroupDiv.appendChild(field);

		var span = document.createElement("span");
		span.classList.add("input-group-btn");
		renderButton("Delete", deleteGroup(parentNode), span);

		inputGroupDiv.appendChild(span);

		var outerSpan = document.createElement("span");
		outerSpan.appendChild(inputGroupDiv);

		var outerDiv = document.createElement("div");
		outerDiv.classList.add("list-group");
		outerDiv.id = "newnickname-" + counter++;

		outerDiv.appendChild(outerSpan);
		renderImageButton(imageUrl + "plus.png", appendStop(parentNode.id), outerDiv);
		parentNode.appendChild(outerDiv);
	}
}

function appendStop(parentDivId) {
	return function() {
		alert(parentDivId);
	}
}

function deleteStop(stopElement) {
	return function() {
		stopElement.remove();
	}
}

function deleteGroup(groupElement) {
	return function() {
		groupElement.remove();
	}
}

function clearGroup(groupElement) {
	return function() {
		console.log(groupElement);
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

	// Scrape the current state of the UI for the 
	// updated preferences and order of groups
	updated = {};
	homeDestinationOrder = [];
	var newHome = scrapeGroupData("home-div", updated, homeDestinationOrder);
	var newDestination = scrapeGroupData("destination-div", updated, homeDestinationOrder);
	var groups = document.getElementById("groups-div").getElementsByClassName("list-group");
	updatedOrder = [];
	for (var i = 0; i < groups.length; i++) {
		scrapeGroupData(groups[i].id, updated, updatedOrder);
	}

	// Delete all groups in cachedRecord and not in updated
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
		var putStops = !(updatedNickname in cachedRecord["groups"])
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
				"other"
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
					console.log("Failed put");
				}
			});
		}
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
	var nickname = groupDiv.getElementsByClassName("active")[0].value;
	if (nickname) {
		var stopElements = groupDiv.getElementsByClassName("stop");
		var stopIds = [];
		for (var i = 0; i < stopElements.length; i++) {
			stopIds.push(parseInt(nameToStopId[stopElements[i].value]));
		}
		if (stopIds) {
			updated[nickname] = stopIds;
			order.push(nickname);
			return nickname;
		}
	}
	return null;
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
