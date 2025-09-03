<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-04bdata.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

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

            <div class="row" >
                 <div class="col-md-12">   
                          <h3>
                             <asp:Literal ID="instructionText" runat="server"></asp:Literal>

                              </h3>
                  </div>          
             </div>
          

        <div class="row" >
                 
                 <div class="col-sm-12">   
                       <img src="pprb.jpg" class="img-responsive" />
                  </div>        
                 
             </div>
            <div class="row" >
                 <div class="col-sm-6 text-right"> 
                   
                      <h4>  
                     <asp:Literal ID="cmrLabelText" runat="server"></asp:Literal>
                          </h4>
                     
                        Nr <telerik:RadTextBox ID="tXDeclarationNr" CssClass="input-lg" BackColor="#FFFF99" SelectionOnFocus="SelectAll" Skin="Bootstrap"   Font-Size="77px" Height="80px" 
                            runat="server" Width="450px"
                        MaxLength="16"></telerik:RadTextBox>
                  </div>  
                       
                  <div class="col-sm-6 text-left">   
                        
                      <h4>
                     <asp:Literal ID="weightLabelText" runat="server"></asp:Literal>
                          </h4>
                    
                        
                        <telerik:RadTextBox ID="tXweightDeclared" BackColor="#FFFF99" Skin="Bootstrap"   
                            CssClass="numbersonly txplace" SelectionOnFocus="SelectAll" runat="server" Width="230px" placeholder="26000"  Font-Size="77px" Height="80px" 
                            
                        MaxLength="16"></telerik:RadTextBox> kg 
                      <button type="button" style="margin-left:50px;" class="btn btn-sm btn-default" onclick="setDef()">
                           <asp:Literal ID="weightNotAvailableButtonText" runat="server"></asp:Literal>

                      </button>
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

          <div class="row extrarow">
                 <div class="col-md-12 extrarow text-right">
                         <a href="default.aspx" class="btn btn-danger ">
                             <asp:Literal ID="backButtonText" runat="server"></asp:Literal>
                         </a>
                 </div>
               
             </div>


    </div> <!-- /container -->


</asp:Content>
<asp:Content ID="ScripsContent" ContentPlaceHolderID="ScriptSection" Runat="Server">

    <script>

    $(function() {
        $('#<%= goButtonText.ClientID%>').hide();
    });

    $(".numbersonly").keypress(function (e) {
    //if the letter is not digit then display error and don't type anything
    if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
    //display error message
    // alert("Insert Only Numbers");
    return false;
    }
    });

    $('input[type="text"]').keyup(function (event) {
        if ($('#<%= tXDeclarationNr.ClientID%>').val().length > 0
                && $('#<%= tXweightDeclared.ClientID%>').val().length > 4
                && $('#<%= tXweightDeclared.ClientID%>').val().length < 6) {
            $('#<%= goButtonText.ClientID%>').show();
            if (event.keyCode === 13) {
                event.preventDefault();
                document.getElementById("<%= goButtonText.ClientID%>").click();
            }
           
          } else
          {
            $('#<%= goButtonText.ClientID%>').hide();
        }
        $(this).val($(this).val().toUpperCase());
    });

        function setDef()
        {
            $('#<%= tXweightDeclared.ClientID%>').val(25000);
            if ($('#<%= tXDeclarationNr.ClientID%>').val().length > 0) {
                $('#<%= goButtonText.ClientID%>').show();
            }
        }

        $(document).ready(function() {
        $(".btnspecial").click(function() {
            $("#myModal").modal('show');
            return true;
        });
      });
      

</script>

</asp:Content>

