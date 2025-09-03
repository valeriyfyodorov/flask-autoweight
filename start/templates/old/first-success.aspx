<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-success.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

<asp:Content ID="ContentHeaders" ContentPlaceHolderID="StyleSelection" Runat="Server">

     <style type="text/css">
         .btn-xl {
             font-size: 50px;
         }
         .extrarow {
             padding-top: 50px;
         }
         .img-responsive {
    margin: 0 auto;
}
        </style>

    
</asp:Content>
<asp:Content ID="ContentMain" ContentPlaceHolderID="ContentSection" Runat="Server">

    <!-- Fixed navbar -->
    

    <telerik:RadAjaxManagerProxy ID="RadAjaxManagerProxy1" runat="server">
        <AjaxSettings>
        
        </AjaxSettings>
        </telerik:RadAjaxManagerProxy>
    
    <div class="container-fluid text-center">
      <!-- Main component for a primary marketing message or call to action -->
      
           

            <div class="row" >
                 <div class="col-md-12">
                         <h1>
                             <asp:Literal ID="instructionText" runat="server"></asp:Literal>

                         </h1>
                 </div>
                <div class="row" >
                 <div class="col-md-12">
                     <img src="first-directions.jpg" class="img-responsive" />
                  </div>          
        </div>
               
             </div>

        

             <div class="row">
                 <div class="col-md-12 extrarow text-right">
                         <a href="default.aspx" class="btn btn-danger ">
                              <asp:Literal ID="backButtonText" runat="server"></asp:Literal>
                         </a>
                 </div>
               
             </div>
            
       

           

    </div> <!-- /container -->

     <script>

         setTimeout(function () {
             extraquery = "";
             if (document.location.search.length > 0)
             {
                 extraquery = document.location.search.substr(1);
             }
             window.location.href = "weighting-instructions.aspx?" + extraquery; //will redirect to your 
         }, 10000); //will call the function after 



     </script>


</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ScriptSection" Runat="Server">
</asp:Content>

