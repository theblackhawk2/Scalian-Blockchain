
class Acteur{
  constructor (type,canvas) {
    // Javascript Canvas ..
    this.type        = type;
    this.canvas      = canvas;
    this.name        = "";
    this.position    = {x:canvas.width/2 , y:0};
    this.icon        = "";
    this.size        = 40;
    switch (this.type) {
      case 'client' :
        this.position.y = canvas.height/10;
        this.icon       = "img/client.png";
        this.fillStyle  = "#FF0000";
        break;
      case 'detaillant':
        this.position.y = canvas.height/10 + canvas.height/5;
        this.icon       = "img/detaillant.png";
        this.fillStyle  = "#f57542";
        break;

      case 'distributeur':
        this.position.y = canvas.height/10 + 2*(canvas.height/5);
        this.icon       = "img/distributeur.png";
        this.fillStyle  = "#f5c842";
        break;
      case 'producteur':
        this.position.y = canvas.height/10 + 3*(canvas.height/5);
        this.icon       = "img/producteur.png";
        this.fillStyle  = "#93f542";
        break;
      case 'fournisseur':
        this.position.y = canvas.height/10 + 4*(canvas.height/5);
        this.icon       = "img/fournisseur.png";
        this.fillStyle  = "#42f587";
        break;
    }
  }

  update() {
      console.log(update);
  }

  draw() {
    var context  = this.canvas.getContext("2d");

    context.beginPath();
    context.arc(this.position.x, this.position.y, 10, 0, 2 * Math.PI);
    context.fillStyle = this.fillStyle;
    context.lineWidth = 5;
    context.fill();
    context.font = "10px Arial";
    context.fillStyle = "black";
    context.fillText(this.name, this.position.x, this.position.y + 5);

  }


}

function updateCanvasText(text,canvas,acteurs) {
  let context = canvas.getContext("2d");
  for(var property in acteurs) {
    if (acteurs.hasOwnProperty(property) && acteurs[property].length >0) {
      acteurs[property].forEach(function(element){
        if (element.name == "") {
          element.name = text;
          context.font = "10px Arial black";
          context.fillText(text, element.position.x, element.position.y + 5);
        }
      });
    }
  }

}

function updateCanvas(canvas , acteurs) {
  let context = canvas.getContext('2d');
  context.clearRect(0, 0, canvas.width, canvas.height);
  for (var property in acteurs) {
    if (acteurs.hasOwnProperty(property) && acteurs[property].length > 0) {
        console.log(acteurs[property]);
        acteurs[property].forEach(function(element,index){
          element.position.x = (index + 1 ) * canvas.width/(acteurs[property].length + 1);
          element.draw();
        });
    }
}
}


$(document).ready(function() {

function scrollTo (id) {
   $('html,body').animate({
      scrollTop: $("#"+id).offset().top - $(window).height()/2
   }, 1000);
}

var secretAuthority = [];
var Actors = {"client":[],
              "detaillant":[],
              "distributeur":[],
              "producteur":[],
              "fournisseur":[]};

var cnv    = document.getElementById("myCanvas");
console.log("Hello World");

$("#Submit").on("click",function() {
  let name = $(".modal-content #nom").val();
  console.log(name);
  $(".bg-modal").css("display","none");
  updateCanvasText(name,cnv,Actors);
});

$("#actors li").on("click",function() {
  var type = $(this).attr("id");
  if (Actors[type].length < 3) {
    Actors[type].push(new Acteur(type,cnv));
    updateCanvas(cnv,Actors);
    $(".bg-modal").css("display","flex");
  }
  else {
    console.log("Maximum d'acteurs atteint sur le niveau "+type);
  }

});

$("#validateSupply").on("click",function(){
  for (var property in Actors) {
    if (Actors.hasOwnProperty(property) && Actors[property].length > 0) {
        Actors[property].forEach(function(e){
          var newListItem = $("<li class='list-group-item'>"+e.name+"</li>").on("click",function(e){
            $(this).toggleClass("active");
          });

          $("#secretAuth").append(newListItem);
        });
    }

}
$("#validateForm").css("display","block");
});

$("validateForm").on("click",function(){
  alert("Transferring Data");
});




});
