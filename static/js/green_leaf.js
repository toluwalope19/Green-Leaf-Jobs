 // target html objects
 let assideBox = document.getElementById("asideBox")
 let mainBox =  document.getElementById("mainBox")
 let nicon =  document.getElementById("navicon")

 // set a toggle flag
 let flag=0

 //  perform show toggle
 function showMenu(){
     assideBox.style.width = "0px"
     mainBox.style.marginLeft = "0px"
     flag = 1
 }
 //  perform hide toggle
 function hideMenu(){
     assideBox.style.width = "200px"
     mainBox.style.marginLeft = "200px"
     flag = 0
 }

 // togglge based on current flag value
 nicon.addEventListener("click", toggleMenu)
 function toggleMenu(){
     if(flag == 0){
         showMenu()
     }else{
         hideMenu()
     }
         
 }
 
 // perform toggle event when the screen goes beyound or less than 800
 window.onresize = function(){
     if(window.innerWidth < 800){
         showMenu()
     }else{
         hideMenu()
     }
 }

 /********************************************************/
 let tbls = document.getElementsByClassName("display")
 let navs =  document.getElementsByClassName("nav-list")
 tblIndex = 0
 navIndex = 0
 /********************************************************/
 
 // hide all display table
 function hideAllTables(){
     for(i=0; i<tbls.length; i++){
         tbls[i].style.display = "none"
     }
 } 
 // deactivate any active menu-bar
 function removeActiveMenu(){
     for(i=0; i<navs.length; i++){
         navs[i].classList.remove("active")
     }
 }
 // display the first table as default
 function displayTbl(x){
     hideAllTables()
     tbls[x].style.display = "block"
 }
 function setActiveNav(x){
     removeActiveMenu()
     navs[x].classList.add("active")
 }

 // set default view
 displayTbl(tblIndex)
 setActiveNav(navIndex)
 
 let contentLen = 0
 contentLen = navs.length < tbls.length? navs.length:tbls.length;
 
 for(j=0; j<contentLen; j++){
     navs[j].addEventListener("click", seCurrentNav);
 }
 function seCurrentNav(){
     for(k=0; k<contentLen; k++){
         if(navs[k].isEqualNode(this)){
             displayTbl(k)
             setActiveNav(k)
         }
     }
     
 }
