<%@ Page Title="" Language="C#" AutoEventWireup="true" CodeFile="first-00choice.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>
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
    </style>
   

  </head>

     

<body>
      <form id="form1" runat="server" class="extraspace">
         
     
    
    <div class="container-fluid text-center">
      <!-- Main component for a primary marketing message or call to action -->
      
            

        <div class="row" >
                 <div class="col-md-10 col-md-offset-1">
                     
                    <asp:HyperLink CssClass="btn btn-default btn-lg btn-xl btn-block" ID="hLarrival"  runat="server">
                        <i class="fas fa-sign-in-alt"></i>  
                    <br />
                        <asp:Literal ID="arrivalButtonText" runat="server">
                        </asp:Literal>
                    </asp:HyperLink>
                      
                         
                   </div>
            </div>
            <div class="row" >

                <div class="col-md-10 col-md-offset-1">
                     <asp:HyperLink CssClass="btn btn-default btn-lg btn-xl btn-block" ID="hLdeparture"  runat="server">
                        <i class="fas fa-sign-out-alt"></i>
                    <br />
                        <asp:Literal ID="departureButtonText" runat="server">
                        </asp:Literal>
                    </asp:HyperLink>
                        
                   </div>
               
                </div>

        <div class="row" >
            <div class="col-md-12">
                <p></p>
            </div>
         </div>

         <div class="row" >
            <div class="col-md-10 col-md-offset-1">
                <a href="default.aspx" class="btn btn-danger btn-lg btn-xl btn-block" role="button">
                        X
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
