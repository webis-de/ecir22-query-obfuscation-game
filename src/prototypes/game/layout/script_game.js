/*function timer() {
    var minutesLabel = document.getElementById("minutes");
    var secondsLabel = document.getElementById("seconds");
    var totalSeconds = 0;
    console.log(minutesLabel)
    console.log(secondsLabel)
    console.log(totalSeconds)
    setInterval(setTime(minutesLabel, secondsLabel, totalSeconds), 1000);
}

    function setTime(minutesLabel, secondsLabel, totalSeconds)
    {
        ++totalSeconds;
        console.log(totalSeconds)
        secondsLabel.innerHTML = pad(totalSeconds%60);
        minutesLabel.innerHTML = pad(parseInt(totalSeconds/60));
    }

    function pad(val)
    {
        var valString = val + "";
        if(valString.length < 2)
        {
            return "0" + valString;
        }
        else
        {
            return valString;
        }
    }
*/
