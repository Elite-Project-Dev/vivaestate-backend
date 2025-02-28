// Listen for when the 'Get My Location' button is clicked
document.getElementById("get-location-btn").addEventListener("click", function() {
    if (navigator.geolocation) {
      // Use the Geolocation API to get the current location
      navigator.geolocation.getCurrentPosition(function(position) {
        // Get latitude and longitude from the position
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
  
        // Show the location info on the page
        document.getElementById("location").innerHTML = `Latitude: ${latitude}, Longitude: ${longitude}`;
  
        // Send the latitude and longitude to the backend
        updatePropertyLocation(latitude, longitude, 1); // 1 is the property ID (you'll need to replace this with the actual ID)
      }, function(error) {
        console.log("Error getting location:", error);
      });
    } else {
      alert("Geolocation is not supported by this browser.");
    }
  });
  
  // Function to send the latitude and longitude to your Django API
  function updatePropertyLocation(latitude, longitude, propertyId) {
    fetch(`/api/properties/${propertyId}/update-location/`, {
      method: "PUT",  // The HTTP method is PUT because we're updating data
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ latitude: latitude, longitude: longitude }),
    })
    .then(response => response.json())
    .then(data => {
      alert("Location updated successfully!");
    })
    .catch(error => {
      console.error("Error:", error);
    });
  }
  