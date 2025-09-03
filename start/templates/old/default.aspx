<%@ Page Title="" Language="C#" AutoEventWireup="true" CodeFile="default.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>
<%@ Import Namespace="System.Web.Optimization" %>

<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="">
    <meta name="author" content="">
       <script src="https://kit.fontawesome.com/441b02c796.js"></script>

      <title>Self-Weighing</title>

    <!-- Bootstrap core CSS -->
     <%: Styles.Render("~/bundles/BootstrapCss")  %>

    <!-- Custom styles for this template -->
   <style type="text/css">
        .messagealert {
            width: 100%;

            z-index: 100000;
            padding: 0;
            font-size: 15px;
        }
        .backColorLightRed
          {
            background-color: #fbbdbd;
          }
        .colorRed
          {
            color: red;
          }
        .backColorLightOrange
          {
            background-color: #fcce8d;
          }
        .backColorLightYellow
          {
            background-color: #fbf6ba;
          }
        .backColorLightGreen
          {
            background-color: #b9fbac;
          }
        .backColorLightBlue
          {
            background-color: #95eafa;
          }
        .backColorLightIndigo
          {
            background-color: #93a5fb;
          }
        .backColorLightViolet
          {
            background-color: #fea3f6;
          }

        .btn-xl {
             font-size: 50px;
         }
         .row {
             padding-top: 50px;
         }
         .extraspace {
             padding-top: 250px;
         }
         .attractive:active {
             border: 10px solid red;
         }
         body{
             background-color: #eee;
         }
    </style>
   

  </head>

     

<body>
      <form id="form1" runat="server">
         <div class="extraspace text-center">
     
          Izvēlēties valodu. Choose language.  Выберете язык.                  
             </div>
    
    <div class="container-fluid text-center">
      <!-- Main component for a primary marketing message or call to action -->
      
            

        <div class="row" >
            <div class="col-md-3 col-md-offset-3"> 
                    <a href="first-00choice.aspx?lng=lv">
                        <img src="img/lv.png" class="img-responsive attractive" alt="Latvian">
                    </a>
            </div>
            <div class="col-md-3"> 
                    <a href="first-00choice.aspx?lng=ru">
                        <img src="img/ru.png" class="img-responsive attractive" alt="Russian">
                    </a>
            </div>
         </div>
 
        <div class="row" >
            <div class="col-md-3 col-md-offset-3"> 
                    <a href="first-00choice.aspx?lng=en">
                        <img src="img/en.png" class="img-responsive attractive" alt="English">
                    </a>
            </div>
            <div class="col-md-3"> 
                    <a href="first-00choice.aspx?lng=ee">
                        <img src="img/ee.png" class="img-responsive attractive" alt="Eesti">
                    </a>
            </div>
         </div>
 
        <div class="row" >
            <div class="col-md-3 col-md-offset-3"> 
                    <a href="first-00choice.aspx?lng=lt">
                        <img src="img/lt.png" class="img-responsive attractive" alt="Lietuva">
                    </a>
            </div>
            <div class="col-md-3"> 
                    <a href="first-00choice.aspx?lng=pl">
                        <img src="img/pl.png" class="img-responsive attractive" alt="Polska">
                    </a>
            </div>
         </div>
 
                
           

    </div> <!-- /container -->

          <!-- Bootstrap core JavaScript
    ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <%: Scripts.Render("~/bundles/jQuery")  %>

           </form>


    
     <script src="../jscripts/idle-timer.min.js"></script>
    <script>

        $(function () {
            // binds to document - shorthand
            $.idleTimer(60000);
        });

        $(document).on("idle.idleTimer", function (event, elem, obj) {
            cuurentUrl=window.location.href.substring(window.location.href.lastIndexOf('/') + 1);
            location.href = "default.aspx";
        });
    </script>
   
  </body>




</html>
