<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-03cargo.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

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
                         <h4>
                             <asp:Literal ID="instructionText" runat="server">
                                 </asp:Literal>
                         </h4>
                 </div>
               
             </div>
        <asp:Repeater ID="rPlists" runat="server">
            <ItemTemplate>

            <div class="row extrarow" >
                 <div class="col-md-12">
                         <a href="first-03factory.aspx?list=<%# Eval("id") %>&company=<%=companyId %>&front=<%=front %>&rear=<%=rear %>&lng=<%=lng %>&weight=<%=weight %>" class="btn btn-default btn-lg btn-xl btn-block">
                               <%# Eval("cargoName") %>
                            
                         </a>
                 </div>
               
             </div>
                </ItemTemplate>

            </asp:Repeater>
        

             <div class="row extrarow">
                         <div class="col-md-12 extrarow text-right">
                                 

                              <asp:HyperLink ID="hLgoBack" CssClass=" btn btn-danger" runat="server">

                                  <asp:Literal ID="backButtonText" runat="server">
                                 </asp:Literal>

                                   </asp:HyperLink>
                         </div>
               
            </div>
            
       

           

    </div> <!-- /container -->


</asp:Content>
<asp:Content ID="Content3" ContentPlaceHolderID="ScriptSection" Runat="Server">
</asp:Content>

