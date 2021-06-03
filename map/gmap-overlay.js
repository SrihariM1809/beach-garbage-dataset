var overlay1;

// Declare a second overlay variable
var overlay2;

USGSOverlay.prototype = new google.maps.OverlayView();

function initMap() {

  // Initialize the map and the custom overlay.

  var map = new google.maps.Map(document.getElementById('map'), {
    zoom: 24,
    center: {
      lat: 13.2208084,
      lng: 80.3263891
    },
    gestureHandling: 'cooperative',
    disableDoubleClickZoom: true,
    streetViewControl: false,
    mapTypeControl: false,
    mapTypeId: 'satellite'
  });

  var bounds1 = new google.maps.LatLngBounds(
    new google.maps.LatLng(13.2208, 80.3262),
    new google.maps.LatLng(13.220816, 80.326205));

  // Declared a second bounds object
  var bounds2 = new google.maps.LatLngBounds(
    new google.maps.LatLng(65.281819, -150.287132),
    new google.maps.LatLng(65.400471, -150.005608));

  // The photograph is courtesy of the U.S. Geological Survey.
  var srcImage = 'https://i.ibb.co/D517KR1/stacked.png';

  // The custom USGSOverlay object contains the USGS image,
  // the bounds of the image, and a reference to the map.
  overlay1 = new USGSOverlay(bounds1, srcImage, map);

  // Create a second overlay
  overlay2 = new USGSOverlay(bounds2, srcImage, map);
}

/** @constructor */
function USGSOverlay(bounds, image, map) {

  // Initialize all properties.
  this.bounds_ = bounds;
  this.image_ = image;
  this.map_ = map;

  // Define a property to hold the image's div. We'll
  // actually create this div upon receipt of the onAdd()
  // method so we'll leave it null for now.
  this.div_ = null;

  // Explicitly call setMap on this overlay.
  this.setMap(map);
}

/**
 * onAdd is called when the map's panes are ready and the overlay has been
 * added to the map.
 */
USGSOverlay.prototype.onAdd = function() {

  var div = document.createElement('div');
  div.style.borderStyle = 'none';
  div.style.borderWidth = '0px';
  div.style.position = 'absolute';

  // Create the img element and attach it to the div.
  var img = document.createElement('img');
  img.src = this.image_;
  img.style.width = '2000%';
  img.style.height = '2000%';
  img.style.position = 'absolute';
  div.appendChild(img);

  this.div_ = div;

  // Add the element to the "overlayLayer" pane.
  var panes = this.getPanes();
  panes.overlayLayer.appendChild(div);
};

USGSOverlay.prototype.draw = function() {

  // We use the south-west and north-east
  // coordinates of the overlay to peg it to the correct position and size.
  // To do this, we need to retrieve the projection from the overlay.
  var overlayProjection = this.getProjection();

  // Retrieve the south-west and north-east coordinates of this overlay
  // in LatLngs and convert them to pixel coordinates.
  // We'll use these coordinates to resize the div.
  var sw = overlayProjection.fromLatLngToDivPixel(this.bounds_.getSouthWest());
  var ne = overlayProjection.fromLatLngToDivPixel(this.bounds_.getNorthEast());

  // Resize the image's div to fit the indicated dimensions.
  var div = this.div_;
  div.style.left = sw.x + 'px';
  div.style.top = ne.y + 'px';
  div.style.width = (ne.x - sw.x) + 'px';
  div.style.height = (sw.y - ne.y) + 'px';
};

// The onRemove() method will be called automatically from the API if
// we ever set the overlay's map property to 'null'.
USGSOverlay.prototype.onRemove = function() {
  this.div_.parentNode.removeChild(this.div_);
  this.div_ = null;
};


initMap();
