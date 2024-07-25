let val;



function getText() {
    // Get the input element by its id
    var inputElement = document.getElementById("textInput");
    var inppass = document.getElementById("pass");
    // Get the value entered by the user
    var userInput = inputElement.value;
  var passinput = inppass.value; 
    // Do something with the user input, for example, log it to the console
  console.log("User input:", userInput);
  console.log("User password:", passinput);
////////////////////////////////////////////////////////////////////////////////////////////////////////////
fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userInput: userInput,
                    passinput: passinput
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Response:', data);
                if (data.status === 'success') {
                  
                  console.log("true");
                  document.getElementById("demo").innerHTML = "true";
                  val = true; 
                } else {
                  alert(data.message);
                  console.log("false");
                  document.getElementById("demo").innerHTML = "false";
                  val = false; 
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    
//////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // You can also pass the user input to another JavaScript function or perform any ot__ operations with it
  if (val == true) {
var metaTag = document.createElement('meta');
    metaTag.setAttribute('http-equiv', 'refresh');
    metaTag.setAttribute('content', '0;url=DASHBOARD.html');
    metaTag.setAttribute('id', 'demo3');
    document.head.appendChild(metaTag);
  }
else if  (val == false){

      var metaTag = document.createElement('meta');
    metaTag.setAttribute('http-equiv', 'refresh');
    metaTag.setAttribute('content', 'None;url=#');
    metaTag.setAttribute('id', 'demo3');
    document.head.appendChild(metaTag);
}
}

function getSigne() {
      // Get the input element by its id
    var inputElement = document.getElementById("textInput_signe");
    var inppass = document.getElementById("pass_signe");
    // Get the value entered by the user
    var userInput = inputElement.value;
  var passinput = inppass.value; 
    // Do something with the user input, for example, log it to the console
  console.log("User input:", userInput);
  console.log("User password:", passinput);

  fetch('/submit', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userInput: userInput,
                    passinput: passinput
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
            })
            .catch((error) => {
                console.error('Error:', error);
            });

} 

function setGaugeValue(gauge, value) {
    if (value < 0) value = 0;
    if (value > 1) value = 1;
    
    gauge.querySelector('.gauge__fillh').style.transform = `rotate(${value / 2}turn)`;
    gauge.querySelector('.gauge__coverh').textContent = `${Math.round(value * 100)}%`;
}

// Example usage:
const gaugeElement = document.querySelector('.gaugeh');
setGaugeValue(gaugeElement, 1); // Set the gauge value to 70%
/////////////////////////////////////////////////////////////////////////


