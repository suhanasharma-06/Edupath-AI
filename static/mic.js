function startMic(){

const recognition = new webkitSpeechRecognition();

recognition.onresult = function(event){
document.getElementById("message").value =
event.results[0][0].transcript;
}

recognition.start();

}