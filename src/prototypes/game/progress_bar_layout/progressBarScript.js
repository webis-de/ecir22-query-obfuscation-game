function computeTransformationProgressBar() {
	listItems = document.querySelectorAll('#progress_bar li');
	console.log(listItems);
	for (i=0; i < listItems.length; i++) {
	    var x = 15 + 14*(i + 1);
	    x = String(x) + "px";
	    var Progresstransformation = "translate(" + x + ", 0px) skew(-35deg)";
	    listItems[i].style.transform = Progresstransformation;
    }
}

computeTransformationProgressBar();