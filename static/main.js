$(document).ready(function(){
  
  // Global / Init Variables
  const namespace = '/mqtt';
  const socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port + namespace);

  // $Element Variables
  const $messages = $( "#messages" )
  const $testSocketButton = $('#test-control');
  const $clearMessagesButton = $('#clear-messages');

  // State Variables
  let testDeviceOn = undefined
  let hideTestDeviceMessages = false
  
  // Add new message
  const addMessage = (message) => {
    $messages.prepend( "<p>" + message + "</p>" );
  }

  // Add test message if we are allowed
  const addTestingMessage = (message) => {
    if (!hideTestDeviceMessages && testDeviceOn) {
      addMessage(message);
    }
  }

  // Toggle Device Test State
  setDeviceTestingState = (test_device_on) => {
    testDeviceOn = test_device_on
    $testSocketButton.html(testDeviceOn ? 'Stop Test Device' : 'Start Test Device')
  }
  
  const toggleTestDevice = () => {
    // Must be boolean type
    if (typeof(testDeviceOn) === typeof(true)) {
      socket.emit('test state change', {test_device_on: !testDeviceOn});
    }
  }

  // Keyboard events
  
  // Click events
  
  $clearMessagesButton.click(() => {
    $messages.empty();
  });
  
  $testSocketButton.click(() => {
      toggleTestDevice()
  });

  // Socket events
  
  socket.on('new message', (message) => {
    addMessage(message.data);
  });

  socket.on('test message', (message) => {
    addTestingMessage(message.data);
  });

  socket.on('test device status', (message) => {
    console.log('test device is on: ', message)
    setDeviceTestingState(message.test_device_on)
  });

  socket.on('connect', function(data) {
    socket.emit('client connected');
    console.log('socket connected...')
  });
  
  socket.on('disconnect', () => {
    console.log('socket disconnected...');
  });
  
  socket.on('reconnect', () => {
    socket.emit('client connected');
    console.log('socket reconnecting...');
  });
  
  socket.on('reconnect_error', () => {
    console.log('attempt to reconnect has failed...');
  });
  
});
