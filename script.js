function initMap() {
    var directionsService = new google.maps.DirectionsService();
    var directionsDisplay = new google.maps.DirectionsRenderer();

    var waypoints = [];

    var request = {};

    var map = new google.maps.Map(document.getElementById('map'), {
        zoom: 7,
        center: {
            lat: 49.83826,
            lng: 24.02324
        }
    });
    directionsDisplay.setMap(map);

    function calculateRoute() {

        for (pos in myData) {
            var addit_dict = {};
            var row = myData[pos];
            var newLatlng = new google.maps.LatLng(row[0], row[1]);
            if (pos == 0) {
                request["origin"] = newLatlng;
            } else if (pos == myData.length - 1) {
                request["destination"] = newLatlng;
            } else {
                addit_dict["location"] = newLatlng;
                addit_dict["stopover"] = true;
                waypoints.push(addit_dict);
            }
        }
        request["waypoints"] = waypoints;
        request["travelMode"] = 'DRIVING';

        directionsService.route(request, function(result, status) {
            if (status == 'OK') {
                directionsDisplay.setDirections(result);
            } else {
                window.alert('Directions request failed due to ' + status);
            }

        });
    }

    document.getElementById('get').onclick = function() {
        calculateRoute();
    };

}