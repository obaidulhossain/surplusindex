



function openCity(evt, cityName) {
    console.log("Tab clicked:", cityName);
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    var targetTab = document.getElementById(cityName);
    if (targetTab) {
        targetTab.style.display = "block";
        evt.currentTarget.className += " active";
    } else {
        console.error("Target tab not found:", cityName);
    }
}
// document.getElementById(cityName).style.display = "block";
// evt.currentTarget.className += " active";


// Get the element with id="defaultOpen" and click on it
document.getElementById("defaultOpen").click();