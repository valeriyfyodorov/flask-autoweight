<%@ Page Title="" Language="C#" MasterPageFile="AutoWeightMaster.master" AutoEventWireup="true" CodeFile="first-04data.aspx.cs" Inherits="stevedore_set_tranunits_shipper" %>

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
                          
                             Norādiet am un piekabes numurus. 
                             Укажите номера а/м и прицепа. 
                            Insert plate numbers.

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
                       Norādiet am numurus. 
                             Укажите номер а/м. Front.
                         </h4>
                    
                        <telerik:RadTextBox ID="tXnrFront" Skin="Bootstrap" CssClass="input-lg"  SelectionOnFocus="SelectAll" runat="server" Width="250px" Font-Size="62px" Height="65px"
                        MaxLength="16" BackColor="#FFFF99" ></telerik:RadTextBox>
                  </div>  
                  <div class="col-md-6 col-sm-6 col-xs-6 text-left">   
                    
                      <h4>
                       Norādiet piekabes numurus. 
                             Укажите номер прицепа. Rear.
                         </h4>
                    
                        <telerik:RadTextBox ID="tXnrRear" BackColor="#FFFF99" CssClass="input-lg" SelectionOnFocus="SelectAll" Font-Size="62px" Height="65px" 
                            Skin="Bootstrap"  runat="server" Width="250px" 
                        MaxLength="16"></telerik:RadTextBox>
                    </div>   
             </div>

        <div class="row" >
                 
                 <div class="col-sm-12">   
                       <img src="ppr.jpg" class="img-responsive" />
                  </div>        
                 
             </div>
            <div class="row" >
                 <div class="col-sm-6 text-right"> 
                   
                      <h4>  
                     Norādiet pavadzīmes vai CMR numuru.
                            
                             Укажите номер накладной или CMR.
                          <br />
                             Number of the CMR:
                          </h4>
                     
                        Nr <telerik:RadTextBox ID="tXDeclarationNr" CssClass="input-lg" BackColor="#FFFF99" SelectionOnFocus="SelectAll" Skin="Bootstrap"   Font-Size="62px" Height="65px" 
                            runat="server" Width="400px"
                        MaxLength="16"></telerik:RadTextBox>
                  </div>  
                       
                  <div class="col-sm-6 text-left">   
                        
                      <h4>
                      Norādiet kravas NETO svaru kg pēc pavadzīmes.
                            
                             Укажите вес груза NETO по накладной кг.
                           <br />
                             Cargo weight NETO:
                          </h4>
                    
                        
                        <telerik:RadTextBox ID="tXweightDeclared" BackColor="#FFFF99" Skin="Bootstrap"   
                            CssClass="numbersonly txplace" SelectionOnFocus="SelectAll" runat="server" Width="200px" placeholder="26000"  Font-Size="62px" Height="65px" 
                            
                        MaxLength="16"></telerik:RadTextBox> kg 
                      <button type="button" style="margin-left:100px;" class="btn btn-sm btn-default" onclick="setDef()">Nav svara uz CMR. Не указан вес. <br >No NET weight info.</button>
                    </div>   


             </div>

           

  

         <asp:Panel ID="pLinitialWeightData" CssClass="row" runat="server" 
             style="background-color:#f9fbff;">
             
             
                  
          
              <div class="col-sm-12 col-md-12">
    
                    <asp:LinkButton ID="lbSaveGross" CssClass=" btn btn-success"  
                        Font-Size="XX-Large"  runat="server" OnClick="lbSaveGross_Click">
                      Svērt / Взвесить / Weigh

                  </asp:LinkButton>
               </div>

                
            </asp:Panel>

          <div class="row">
                 <div class="col-md-12 extrarow text-right">
                         <a href="default.aspx" class="btn btn-danger ">
                             Atpakaļ
                             <br />
                            Назад
                         </a>
                 </div>
               
             </div>


    </div> <!-- /container -->


</asp:Content>
<asp:Content ID="ScripsContent" ContentPlaceHolderID="ScriptSection" Runat="Server">

    <script>

    $(function() {
        $('#<%= lbSaveGross.ClientID%>').hide();
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
        if ($('#<%= tXnrFront.ClientID%>').val().length > 2
                && $('#<%= tXnrRear.ClientID%>').val().length > 2
                && $('#<%= tXDeclarationNr.ClientID%>').val().length > 0
                && $('#<%= tXweightDeclared.ClientID%>').val().length > 4
                && $('#<%= tXweightDeclared.ClientID%>').val().length < 6) {
            $('#<%= lbSaveGross.ClientID%>').show();
            if (event.keyCode === 13) {
                event.preventDefault();
                document.getElementById("<%= lbSaveGross.ClientID%>").click();
            }
            
          } else
          {
            $('#<%= lbSaveGross.ClientID%>').hide();
        }
        $(this).val($(this).val().toUpperCase());
    });

        function setDef()
        {
            $('#<%= tXweightDeclared.ClientID%>').val(25000);
            if ($('#<%= tXnrFront.ClientID%>').val().length > 2
                && $('#<%= tXnrRear.ClientID%>').val().length > 2
                && $('#<%= tXDeclarationNr.ClientID%>').val().length > 0) {
                $('#<%= lbSaveGross.ClientID%>').show();

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

