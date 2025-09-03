<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-01scan.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

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
                         <h2>
                             <asp:Literal ID="instructionText" Mode="PassThrough" runat="server">
                                 </asp:Literal>
                         </h2>
                 </div>         
             </div>

        <div class="row" >
                 <div class="col-md-12" id="buttoninstructions">
                     <img src="first-scan.gif" class="img-responsive" />
                  </div>          
        </div>

             <div class="row">
                 <div class="col-md-12 extrarow text-right">
                         <a href="default.aspx" class="btn btn-danger ">
                             <asp:Literal ID="backButtonText" runat="server">
                                 </asp:Literal>
                         </a>
                 </div>
               
             </div>
            
       

           

    </div> <!-- /container -->


</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ScriptSection" Runat="Server">
</asp:Content>

