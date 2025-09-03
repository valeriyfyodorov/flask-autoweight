<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-04adata.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

<asp:Content ID="ContentHeaders" ContentPlaceHolderID="StyleSelection" Runat="Server">

    <script type="text/javascript" id="telerikClientEvents1">
        function confirmAndClear() {
             if (confirm('OK?')) {
                 //clearButtonsRegion();
                 return true;
             }
             else {
                 return false;
             }
         }

    </script>

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

         input[type=text] {
          background-color: #ffffe4;
        }

        input[type=text]:focus {
          background-color: #e6ffe4;
        }

        input[type="text"]
{
    font-size:40px;
}

        .bottom-column
        {
            float: none;
            display: table-cell;
            vertical-align: bottom;
        }
        .vcenter {
            display: inline-block;
            vertical-align: middle;
        }
        .txplace::-webkit-input-placeholder placeholder{
            color: #f3f3cd;
        }

        .txplace::-moz-placeholder placeholder{
           color: #f3f3cd;
        }

        .txplace:-ms-input-placeholder placeholder{
            color: #f3f3cd;
        }
        input::-webkit-input-placeholder{
            color: #f3f3cd;
        }

        input::-moz-placeholder{
            color: #f3f3cd;
        }

        input:-ms-input-placeholder{
           color: #f3f3cd;
        }

        ::-webkit-input-placeholder { /* Edge */
           color: #f3f3cd;
        }

        :-ms-input-placeholder { /* Internet Explorer 10-11 */
           color: #f3f3cd;
        }

        ::placeholder {
          color:#f3f3cd;
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
                 
        <div class="modal fade" id="myModal" role="dialog">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h4 class="modal-title">Wait</h4>
        </div>
        <div class="modal-body">
          <p>..... Gaidiet 10 sekundas. Ждите 10 секунд ....</p>
        </div>
        
      </div>
    </div>
  </div>

            <div class="row" style="padding-top: -30px; margin-top: -30px;" >
                 <div class="col-md-12">
                         <h2>
                             <asp:Label ID="lLselectedList" runat="server" Text=""></asp:Label>
                         </h2>
                 </div>         
             </div>

            <div class="row extrarow" >
                 <div class="col-md-12">   
                          <h3>
                             <asp:Literal ID="instructionText" runat="server"></asp:Literal>
                              </h3>

                  </div>          
             </div>
            <div class="row" >
                 <div class="col-md-12">   
                       <img src="truckplates.jpg" class="img-responsive" />
                  </div>          
             </div>
            <div class="row" >
                 <div class="col-md-6 col-sm-6 col-xs-6 text-right">  
                        
                     <h4>
                      <asp:Literal ID="frontPlateLabelText" runat="server">
                                 </asp:Literal>
                         </h4>
                    
                        <telerik:RadTextBox ID="tXnrFront" Skin="Bootstrap" CssClass="input-lg"  
                            runat="server" Width="350px" Font-Size="75px" Height="80px"
                        MaxLength="16" BackColor="#FFFF99" ></telerik:RadTextBox>
                  </div>  
                  <div class="col-md-6 col-sm-6 col-xs-6 text-left">   
                    
                      <h4>
                        <asp:Literal ID="rearPlateLabelText" runat="server">
                                 </asp:Literal>
                         </h4>
                    
                        <telerik:RadTextBox ID="tXnrRear" BackColor="#FFFF99" CssClass="input-lg" 
                            Font-Size="75px" Height="80px" 
                            Skin="Bootstrap"  runat="server" Width="350px" 
                        MaxLength="16"></telerik:RadTextBox>
                    </div>   
             </div>

        
            

           

  

         <asp:Panel ID="pLinitialWeightData" CssClass="row extrarow" runat="server" 
             style="background-color:#f9fbff;">
             
             
                  
          
              <div class="col-sm-12 col-md-12">
    
                    <asp:LinkButton ID="goButtonText" CssClass=" btn btn-success"  
                        Font-Size="XX-Large"  runat="server" OnClick="goButtonText_Click">
                     

                  </asp:LinkButton>
               </div>

                
            </asp:Panel>

          <div class="row">
                 <div class="col-md-12 extrarow text-right">
                         <a href="first-03factory.aspx?front=<%=front %>&rear=<%=rear %>&lng=<%=lng %>&weight=<%=weight %>&company=<%=companyId %>&list=<%=listId %>" class="btn btn-danger ">
                              <asp:Literal ID="backButtonText" runat="server">
                                 </asp:Literal>
                         </a>
                 </div>
               
             </div>


    </div> <!-- /container -->


</asp:Content>
<asp:Content ID="ScripsContent" ContentPlaceHolderID="ScriptSection" Runat="Server">

    <script>

    $(function() {
        $('#<%= goButtonText.ClientID%>').hide();
        if ($('#<%= tXnrFront.ClientID%>').val().length > 2
                && $('#<%= tXnrRear.ClientID%>').val().length > 2) {
            $('#<%= goButtonText.ClientID%>').show();
        }
    });

    $(".numbersonly").keypress(function (e) {
    //if the letter is not digit then display error and don't type anything
    if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
    //display error message
    // alert("Insert Only Numbers");
    return false;
    }
    });

    $('input[type="text"]').keyup(function(event) {
        if ($('#<%= tXnrFront.ClientID%>').val().length > 2
                && $('#<%= tXnrRear.ClientID%>').val().length > 2) {
            $('#<%= goButtonText.ClientID%>').show();
            if (event.keyCode === 13) {
                event.preventDefault();
                document.getElementById("<%= goButtonText.ClientID%>").click();
            }
            $(this).val($(this).val().toUpperCase());
          } else
          {
            $('#<%= goButtonText.ClientID%>').hide();
        }
        $(this).val($(this).val().toUpperCase());
    });

       

        $(document).ready(function() {
        $(".btnspecial").click(function() {
            $("#myModal").modal('show');
            return true;
        });
      });
      

</script>

</asp:Content>

